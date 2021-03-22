import itertools
import logging
import os
import random
import string
from datetime import timedelta
from typing import Iterable

from flask import Flask, Response, jsonify, render_template, request, send_from_directory
from raven.contrib.flask import Sentry

from clasificahumor import database
from clasificahumor.database import TYPE_TWEET


def create_app() -> Flask:
    app_ = Flask(__name__)

    app_.secret_key = os.environ["FLASK_SECRET_KEY"]
    app_.config["SESSION_TYPE"] = "filesystem"

    Sentry(app_, logging=True, level=logging.ERROR)

    return app_


app = create_app()

BATCH_SIZE = 3


def _stringify_tweet_id(tweet: TYPE_TWEET) -> None:
    tweet["id"] = str(tweet["id"])


def _stringify_tweet_ids(tweets: Iterable[TYPE_TWEET]) -> None:
    """
    Converts the tweet field "id" to string for each tweet in the tweets list.

    Tweet IDs in string format should be used in JavaScript instead of numbers.
    See https://developer.twitter.com/en/docs/basics/twitter-ids
    """
    for tweet in tweets:
        _stringify_tweet_id(tweet)


def _generate_id() -> str:  # From https://stackoverflow.com/a/2257449/1165181
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=100))


def _get_session_id() -> str:
    return request.cookies.get("id") or _generate_id()


@app.after_request
def add_header(response: Response) -> Response:
    response.cache_control.max_age = 0
    response.cache_control.no_cache = True

    response.set_cookie("id", _get_session_id(), max_age=int(timedelta(weeks=1000).total_seconds()))

    return response


@app.route("/tweets")
def tweets_route() -> Response:
    session_id = _get_session_id()

    tweets = list(database.random_least_voted_unseen_tweets(session_id, BATCH_SIZE))

    if len(tweets) < BATCH_SIZE:
        tweets = tweets + list(database.random_tweets(BATCH_SIZE - len(tweets)))

    _stringify_tweet_ids(tweets)

    return jsonify(tweets)


@app.route("/vote", methods=["POST"])
def vote_and_get_new_tweet_route() -> Response:
    session_id = _get_session_id()

    if "tweet_id" in request.form and "vote" in request.form and "is_offensive" in request.form:
        is_offensive = request.form["is_offensive"].lower() == "true"
        database.add_vote(session_id, request.form["tweet_id"], request.form["vote"], is_offensive)

    ignore_tweet_ids = request.form.getlist("ignore_tweet_ids[]")

    tweets = itertools.chain(database.random_least_voted_unseen_tweets(session_id, 1, ignore_tweet_ids),
                             database.random_tweets(1))

    tweet = next(iter(tweets), {})

    _stringify_tweet_id(tweet)

    return jsonify(tweet)


@app.route("/vote-count")
def vote_count_route() -> Response:
    return jsonify(database.vote_count_without_skips())


@app.route("/stats")
def stats_route() -> Response:
    stats = database.stats()

    stats["votes-not-consider-test"] = stats["votes"] - sum(stats["test-tweets-vote-count"])

    stats["test-tweets-vote-count"] = ", ".join(str(c) for c in stats["test-tweets-vote-count"])

    stats["histogram"] = [["Cantidad de votos", "Cantidad de tweets"]] + \
                         [[str(a), b] for a, b in stats["histogram"].items()]

    stats["votes-per-category"]["No humor"] = stats["votes-per-category"]["x"]
    del stats["votes-per-category"]["x"]
    stats["votes-per-category"]["Saltear"] = stats["votes-per-category"]["n"]
    del stats["votes-per-category"]["n"]
    stats["votes-per-category"] = [["Voto", "Cantidad de tweets"]] + \
                                  [[str(a), b] for a, b in stats["votes-per-category"].items()]

    return render_template("stats.html", stats=stats)


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_files_route(path: str) -> Response:
    return send_from_directory("static", path)
