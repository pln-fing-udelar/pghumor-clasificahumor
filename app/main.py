from datetime import timedelta
import os

import flask

from app import database

app = flask.Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

BATCH_SIZE = 3


@app.before_request
def make_session_permanent() -> None:
    flask.session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=1000)


@app.route('/tweets')
def tweets_route() -> flask.Response:
    session_id = flask.request.cookies.get('session')

    tweets = database.random_least_voted_unseen_tweets(session_id, BATCH_SIZE)

    if len(tweets) < BATCH_SIZE:
        tweets = tweets + database.random_tweets(BATCH_SIZE - len(tweets))

    # app.logger.info(tweets)

    return flask.jsonify(tweets)


@app.route('/vote', methods=['POST'])
def vote_route() -> flask.Response:  # TODO: and get new tweet?
    pass


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> flask.Response:
    return flask.send_from_directory('static', path)
