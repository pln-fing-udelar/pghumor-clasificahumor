from datetime import timedelta
import os

from flask import Flask, jsonify, request, Response, send_from_directory, session

from app import database

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

BATCH_SIZE = 3


@app.before_request
def make_session_permanent() -> None:
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=1000)


@app.route('/tweets')
def tweets_route() -> Response:
    session_id = request.cookies.get('session')

    tweets = database.random_least_voted_unseen_tweets(session_id, BATCH_SIZE)

    if len(tweets) < BATCH_SIZE:
        tweets = tweets + database.random_tweets(BATCH_SIZE - len(tweets))

    return jsonify(tweets)


@app.route('/vote', methods=['POST'])
def vote_and_get_new_tweet_route() -> Response:
    session_id = request.cookies.get('session')

    app.logger.info(request.form)

    if 'tweet_id' in request.form and 'vote' in request.form:
        database.add_vote(session_id, request.form['tweet_id'], request.form['vote'])

    tweets = database.random_least_voted_unseen_tweets(session_id, 1)

    if not tweets:
        tweets = database.random_tweets(1)

    return jsonify(tweets[0] if tweets else {})


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> Response:
    return send_from_directory('static', path)
