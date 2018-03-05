from datetime import timedelta
import logging
import os
from typing import Any, Dict, List

from flask import Flask, jsonify, request, Response, send_from_directory, session
from raven.contrib.flask import Sentry

from clasificahumor import database

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

Sentry(app, logging=True, level=logging.ERROR)

BATCH_SIZE = 3


def stringify_tweet_ids(tweets: List[Dict[str, Any]]) -> None:
    """
    Converts the tweet field 'id' from number to string for each dict tweet in the tweets list.

    Tweet IDs in string format should be used in Javascript instead of numbers.
    See https://developer.twitter.com/en/docs/basics/twitter-ids
    """
    for tweet in tweets:
        tweet['id'] = str(tweet['id'])


@app.before_request
def make_session_permanent() -> None:
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=1000)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


@app.route('/tweets')
def tweets_route() -> Response:
    session_id = request.cookies.get('session')

    tweets = database.random_least_voted_unseen_tweets(session_id, BATCH_SIZE)

    if len(tweets) < BATCH_SIZE:
        tweets = tweets + database.random_tweets(BATCH_SIZE - len(tweets))

    stringify_tweet_ids(tweets)

    return jsonify(tweets)


@app.route('/vote', methods=['POST'])
def vote_and_get_new_tweet_route() -> Response:
    session_id = request.cookies.get('session')

    if 'tweet_id' in request.form and 'vote' in request.form:
        database.add_vote(session_id, request.form['tweet_id'], request.form['vote'])

    tweets = database.random_least_voted_unseen_tweets(session_id, 1)

    if not tweets:
        tweets = database.random_tweets(1)

    stringify_tweet_ids(tweets)

    return jsonify(tweets[0] if tweets else {})


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> Response:
    None.get()
    return send_from_directory('static', path)
