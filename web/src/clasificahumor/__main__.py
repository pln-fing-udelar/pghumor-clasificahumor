"""FastAPI application for ClasificaHumor."""

import json
import logging
import os
import random
import string
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Form, Request, Response, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sentry_sdk.integrations.logging import LoggingIntegration
from starlette.datastructures import MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from clasificahumor import database
from clasificahumor.database import TYPE_TWEET

logger = logging.getLogger(__name__)

REQUEST_TWEET_BATCH_SIZE = 3
SESSION_ID_MAX_AGE = int(timedelta(weeks=1000).total_seconds())

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        send_default_pii=True,
        traces_sample_rate=1.0,
        integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
    )


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    async with database.create_engine() as database_engine:
        yield {"database_engine": database_engine}


def _generate_id() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=100))


def _get_session_id(request: Request) -> str:
    if prolific_id := request.query_params.get("PROLIFIC_PID"):
        return f"prolific-id-{prolific_id}"
    return request.cookies.get("id") or _generate_id()


class CacheControlMiddleware:
    """Sets session cookies and security cache headers on all HTTP responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        session_id = _get_session_id(Request(scope))
        scope.setdefault("state", {})["session_id"] = session_id

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("Cache-Control", "max-age=0, no-cache")
                headers.append("Set-Cookie", f"id={session_id}; Max-Age={SESSION_ID_MAX_AGE}; Path=/; SameSite=lax")
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "SAMEORIGIN")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
            await send(message)

        await self.app(scope, receive, send_with_headers)


app = FastAPI(lifespan=_lifespan)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        *(f"https://{host.strip()}" for host in os.environ.get("VIRTUAL_HOST", "").split(",") if host.strip()),
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=600,
)


class VotePayload(BaseModel):
    tweet_id: str | int | None = None
    vote: str | None = None
    is_offensive: bool = False
    ignore_tweet_ids: list[str | int] = []


@app.get("/tweets")
async def tweets_route(request: Request) -> list[TYPE_TWEET]:
    """Returns a batch of random least-voted unseen tweets for the current session."""
    session_id: str = request.state.session_id
    engine = request.state.database_engine

    tweets = await database.random_least_voted_unseen_tweets(engine, session_id, REQUEST_TWEET_BATCH_SIZE)

    if len(tweets) < REQUEST_TWEET_BATCH_SIZE:
        tweets.extend(await database.random_tweets(engine, REQUEST_TWEET_BATCH_SIZE - len(tweets)))

    for tweet in tweets:
        tweet["id"] = str(tweet["id"])

    return tweets


@app.post("/vote")
async def vote_and_get_new_tweet_route(request: Request) -> TYPE_TWEET:
    """Submits a tweet vote and returns the next unseen tweet."""
    session_id: str = request.state.session_id
    engine = request.state.database_engine

    tweet_id: str | None = None
    vote: str | None = None
    is_offensive: bool = False
    ignore_tweet_ids: list[str] = []

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            payload = VotePayload.model_validate(body)
            tweet_id = str(payload.tweet_id) if payload.tweet_id is not None else None
            vote = payload.vote
            is_offensive = payload.is_offensive
            ignore_tweet_ids = [str(t) for t in payload.ignore_tweet_ids]
        except Exception:
            pass
    else:
        form = await request.form()
        if "tweet_id" in form:
            tweet_id = str(form["tweet_id"])
        if "vote" in form:
            vote = str(form["vote"])
        if "is_offensive" in form:
            is_offensive = str(form["is_offensive"]).lower() == "true"
        ignore_tweet_ids = [str(x) for x in form.getlist("ignore_tweet_ids[]")]

    if tweet_id is not None and vote is not None:
        await database.add_vote(engine, session_id, tweet_id, vote, is_offensive)

    tweets = await database.random_least_voted_unseen_tweets(engine, session_id, 1, ignore_tweet_ids)
    if not tweets:
        tweets = await database.random_tweets(engine, 1)

    tweet = tweets[0] if tweets else {}
    if tweet and "id" in tweet:
        tweet["id"] = str(tweet["id"])

    return tweet


@app.get("/session-vote-count")
async def session_vote_count_route(request: Request) -> Response:
    """Returns the total vote count for the current session, including skips."""
    count = await database.session_vote_count_with_skips(request.state.database_engine, request.state.session_id)
    return Response(content=json.dumps(count), media_type="application/json")


@app.get("/vote-count")
async def vote_count_route(request: Request) -> Response:
    """Returns the global vote count, excluding skips."""
    count = await database.vote_count_without_skips(request.state.database_engine)
    return Response(content=json.dumps(count), media_type="application/json")


@app.post("/prolific-consent")
async def prolific_consent_route(request: Request) -> Response:
    """Records user consent for the Prolific session."""
    await database.prolific_consent(request.state.database_engine, request.state.session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/prolific-finish")
async def prolific_finish_route(
    request: Request,
    comments: str = Form(""),
) -> RedirectResponse:
    """Records session completion and comments, redirecting to Prolific."""
    await database.prolific_finish(request.state.database_engine, request.state.session_id, comments)
    return RedirectResponse(
        url="https://app.prolific.co/submissions/complete?cc=5E395F77",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/stats")
async def stats_route(request: Request) -> Response:
    """Renders annotation statistics."""
    stats_data = await database.stats(request.state.database_engine)

    stats_data["votes-not-consider-test"] = stats_data["votes"] - sum(stats_data["test-tweets-vote-count"])
    stats_data["test-tweets-vote-count"] = ", ".join(str(c) for c in stats_data["test-tweets-vote-count"])

    stats_data["histogram"] = [["Cantidad de votos", "Cantidad de tweets"]] + [
        [str(a), b] for a, b in stats_data["histogram"].items()
    ]

    stats_data["votes-per-category"]["No humor"] = stats_data["votes-per-category"].pop("x", 0)
    stats_data["votes-per-category"]["Saltear"] = stats_data["votes-per-category"].pop("n", 0)
    stats_data["votes-per-category"] = [["Voto", "Cantidad de tweets"]] + [
        [str(a), b] for a, b in stats_data["votes-per-category"].items()
    ]

    return templates.TemplateResponse(request=request, name="stats.html", context={"stats": stats_data})


@app.get("/")
async def root_route() -> FileResponse:
    """Serves the main annotation single-page application."""
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
