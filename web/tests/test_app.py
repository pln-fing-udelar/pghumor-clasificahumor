"""Tests for the FastAPI application routes and middlewares."""

import httpx2
import pytest


async def test_healthz_route(client: httpx2.AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_tweets_route(client: httpx2.AsyncClient) -> None:
    response = await client.get("/tweets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0] and "text" in data[0]

    # Verify cookie and security headers
    assert "id" in response.cookies or "Set-Cookie" in response.headers
    set_cookie = response.headers.get("Set-Cookie", "").lower()
    assert "httponly" in set_cookie
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "no-cache" in response.headers.get("Cache-Control", "")


async def test_prolific_session_id(client: httpx2.AsyncClient) -> None:
    response = await client.get("/tweets?PROLIFIC_PID=user_xyz")
    assert response.status_code == 200
    set_cookie = response.headers.get("Set-Cookie", "")
    assert "prolific-id-user_xyz" in set_cookie

    response_composite = await client.get("/tweets?PROLIFIC_PID=user_xyz&SESSION_ID=study_session_1")
    assert response_composite.status_code == 200
    set_cookie_composite = response_composite.headers.get("Set-Cookie", "")
    assert "prolific-id-user_xyz-study_session_1" in set_cookie_composite


def test_generate_id() -> None:
    from clasificahumor.__main__ import _generate_id

    generated = _generate_id()
    assert len(generated) == 16
    assert all(c in "0123456789abcdef" for c in generated)


async def test_vote_route_form(client: httpx2.AsyncClient) -> None:
    # Vote via form data
    res_vote = await client.post(
        "/vote",
        data={
            "tweet_id": "101",
            "vote": "4",
            "is_offensive": "true",
            "ignore_tweet_ids[]": ["101"],
        },
    )
    assert res_vote.status_code == 200
    data = res_vote.json()
    assert isinstance(data, dict)
    assert data.get("id") != "101"

    # Verify vote count incremented
    res_count = await client.get("/session-vote-count")
    assert res_count.status_code == 200
    assert res_count.json() == 1


async def test_vote_route_json(client: httpx2.AsyncClient) -> None:
    # Vote via JSON payload
    res_vote = await client.post(
        "/vote",
        json={
            "tweet_id": "102",
            "vote": "x",
            "is_offensive": False,
            "ignore_tweet_ids": ["102"],
        },
    )
    assert res_vote.status_code == 200
    data = res_vote.json()
    assert isinstance(data, dict)
    assert data.get("id") != "102"


async def test_vote_count_route(client: httpx2.AsyncClient) -> None:
    await client.post("/vote", json={"tweet_id": "103", "vote": "5", "is_offensive": False})
    res = await client.get("/vote-count")
    assert res.status_code == 200
    assert res.json() >= 1


async def test_prolific_consent_and_finish_routes(client: httpx2.AsyncClient) -> None:
    # Consent
    res_consent = await client.post("/prolific-consent")
    assert res_consent.status_code == 204

    # Finish
    res_finish = await client.post(
        "/prolific-finish",
        data={"comments": "Todo claro"},
        follow_redirects=False,
    )
    assert res_finish.status_code == 303
    assert "prolific.co" in res_finish.headers.get("Location", "")


async def test_stats_route(client: httpx2.AsyncClient) -> None:
    await client.post("/vote", json={"tweet_id": "104", "vote": "1", "is_offensive": False})
    response = await client.get("/stats")
    assert response.status_code == 200
    assert "Estadísticas" in response.text
    assert "chart-histogram" in response.text


async def test_root_and_static_files(client: httpx2.AsyncClient) -> None:
    res_root = await client.get("/")
    assert res_root.status_code == 200
    assert "<!DOCTYPE html>" in res_root.text

    res_static = await client.get("/css/main.css")
    assert res_static.status_code == 200


async def test_vote_invalid_json(client: httpx2.AsyncClient) -> None:
    res = await client.post(
        "/vote",
        content="not valid json",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200


async def test_middleware_non_http() -> None:
    from starlette.types import Message, Receive, Scope, Send

    from clasificahumor.__main__ import CacheControlMiddleware

    called = False

    async def dummy_app(scope: Scope, receive: Receive, send: Send) -> None:
        nonlocal called
        called = True

    async def mock_receive() -> Message:
        return {}

    async def mock_send(message: Message) -> None:
        pass

    mw = CacheControlMiddleware(dummy_app)
    await mw({"type": "websocket"}, mock_receive, mock_send)
    assert called


async def test_lifespan(monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import AsyncMock, patch

    from clasificahumor.__main__ import _lifespan, app

    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASS", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_NAME", "d")

    mock_engine = AsyncMock()
    with patch("clasificahumor.database.create_engine") as mock_create:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_engine
        mock_ctx.__aexit__.return_value = None
        mock_create.return_value = mock_ctx

        async with _lifespan(app) as state:
            assert state["database_engine"] == mock_engine


async def test_tweets_route_fallback_random(client: httpx2.AsyncClient) -> None:
    # Vote on almost all tweets so unseen tweets < REQUEST_TWEET_BATCH_SIZE (3)
    all_seeded = ["101", "102", "103", "104", "1088158691633713152", "1092855393188020224"]
    for tid in all_seeded:
        await client.post("/vote", json={"tweet_id": tid, "vote": "1"})

    # GET /tweets should now have fewer than 3 unseen tweets, triggering fallback to random_tweets
    res = await client.get("/tweets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3


async def test_vote_route_fallback_random(client: httpx2.AsyncClient) -> None:
    # Ignore all tweets in the database so random_least_voted_unseen_tweets returns []
    all_ids = ["101", "102", "103", "104", "1088158691633713152", "1092855393188020224", "1086371400431095813"]
    res = await client.post(
        "/vote",
        json={"tweet_id": "101", "vote": "2", "ignore_tweet_ids": all_ids},
    )
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
