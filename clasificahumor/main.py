from datetime import timedelta
import logging
import os
import random
import string
from typing import Any, Dict, List

from flask import Flask, jsonify, request, Response, send_from_directory
from raven.contrib.flask import Sentry

from clasificahumor import database


def create_app() -> Flask:
    app_ = Flask(__name__)

    app_.secret_key = os.getenv('FLASK_SECRET_KEY')
    app_.config['SESSION_TYPE'] = 'filesystem'

    Sentry(app_, logging=True, level=logging.ERROR)

    return app_


app = create_app()

BATCH_SIZE = 3


def stringify_tweet_ids(tweets: List[Dict[str, Any]]) -> None:
    """
    Converts the tweet field 'id' from number to string for each dict tweet in the tweets list.

    Tweet IDs in string format should be used in Javascript instead of numbers.
    See https://developer.twitter.com/en/docs/basics/twitter-ids
    """
    for tweet in tweets:
        tweet['id'] = str(tweet['id'])


def generate_id():
    # https://stackoverflow.com/a/2257449/1165181
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))


def get_session_id():
    id_ = request.cookies.get('id')
    if not id_:  # Prefer checking here and not using 'default', as it would do the function call to "generate_id".
        id_ = generate_id()
    return id_


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    response.cache_control.no_cache = True

    response.set_cookie('id', get_session_id(), max_age=int(timedelta(weeks=1000).total_seconds()))

    return response


@app.route('/tweets')
def tweets_route() -> Response:
    session_id = get_session_id()

    tweets = database.random_least_voted_unseen_tweets(session_id, BATCH_SIZE)

    if len(tweets) < BATCH_SIZE:
        tweets = tweets + database.random_tweets(BATCH_SIZE - len(tweets))

    stringify_tweet_ids(tweets)

    return jsonify(tweets)


@app.route('/vote', methods=['POST'])
def vote_and_get_new_tweet_route() -> Response:
    session_id = get_session_id()

    if 'tweet_id' in request.form and 'vote' in request.form:
        database.add_vote(session_id, request.form['tweet_id'], request.form['vote'])

    ignore_tweet_ids = [int(tweet_id) for tweet_id in request.form.getlist('ignore_tweet_ids[]')]

    tweets = database.random_least_voted_unseen_tweets(session_id, 1, ignore_tweet_ids)

    if not tweets:
        tweets = database.random_tweets(1)

    stringify_tweet_ids(tweets)

    return jsonify(tweets[0] if tweets else {})


@app.route('/vote-count')
def vote_count_route() -> Response:
    return jsonify(database.vote_count_without_skips())


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> Response:
    return send_from_directory('static', path)
