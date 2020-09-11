from datetime import timedelta
import logging
import os
import random
import string
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request, Response, send_from_directory
from raven.contrib.flask import Sentry

from clasificahumor import database

from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect

PROLIFIC_REDIRECT_URL = "https://app.prolific.co/submissions/complete?cc=2A8B0A57"

def random_choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]

def create_app() -> Flask:
    app_ = Flask(__name__)

    app_.secret_key = os.environ['FLASK_SECRET_KEY']
    app_.config['SESSION_TYPE'] = 'filesystem'

    Sentry(app_, logging=True, level=logging.ERROR)

    return app_


app = create_app()

BATCH_SIZE = 5
VOTES_SIZE = 25


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
    return ''.join(random_choices(string.ascii_uppercase + string.digits, k=100))


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

    if 'tweet_id' in request.form and 'vote_humor' in request.form and 'vote_offensive' in request.form and 'vote_personal' in request.form:
        database.add_vote(session_id, request.form['tweet_id'], request.form['vote_humor'], request.form['vote_offensive'], request.form['vote_personal'])

    ignore_tweet_ids = [int(tweet_id) for tweet_id in request.form.getlist('ignore_tweet_ids[]')]

    tweets = database.random_least_voted_unseen_tweets(session_id, 1, ignore_tweet_ids)

    if not tweets:
        tweets = database.random_tweets(1)

    stringify_tweet_ids(tweets)

    return jsonify(tweets[0] if tweets else {})

@app.route('/vote_ready', methods=['POST'])
def vote_ready() -> Response:
    if 'votes' in request.form and int(request.form['votes']) >= VOTES_SIZE:
        return jsonify({ "msg": "OK" })
    else:
        return jsonify({ "msg": 'ERROR: %s votes expected, %s found' % (VOTES_SIZE,request.form['votes'])})

@app.route('/annotator', methods=['POST'])
def register_annotator() -> Response:
    session_id = get_session_id()

    if 'prolific_id' in request.form and 'question1' in request.form and 'question2' in request.form and 'question3' in request.form and 'question4' in request.form and 'question5' in request.form and 'question6' in request.form:
        prolific_id = request.form['prolific_id'].strip()
        if prolific_id == "":
            return jsonify("Error: Please specify your Prolific ID")
        prolific_session_id = ""
        if "prolific_session_id" in request.form:
            prolific_session_id = request.form["prolific_session_id"]
        study_id = ""
        if "study_id" in request.form:
            study_id = request.form["study_id"]
        database.add_annotator(session_id, prolific_id, prolific_session_id, study_id, request.form['question1'], request.form['question2'], request.form['question3'], request.form['question4'], request.form['question5'], request.form['question6'])
        if request.form['question1'] != 'y' or request.form['question2'] != 'y' or request.form['question3'] != 'y' or request.form['question4'] != 'y' or request.form['question5'] != 'y' or request.form['question6'] != 'y':
            return jsonify("NO-CONSENT")

        result = database.is_personality_registered(prolific_id)
        if 'count' not in result or result['count'] == 0:
            return jsonify("OK-NO-SURVEY")
        else:
            return jsonify("OK-SURVEY")
    else:
        return jsonify("Error: Please answer all questions")

@app.route('/personality_survey', methods=['POST'])
def add_personality_survey() -> Response:
    session_id = get_session_id()

    result = database.get_prolific_id(session_id)
    if 'prolific_id' not in result:
        return jsonify("Error: Annotator not registered")
    prolific_id = result['prolific_id']

    if 'question1' in request.form and 'question2' in request.form and 'question3' in request.form and 'question4' in request.form and 'question5' in request.form and 'question6' in request.form and 'question7' in request.form and 'question8' in request.form and 'question9' in request.form and 'question10' in request.form and 'question11' in request.form:
        database.add_personality(prolific_id, request.form['question1'], request.form['question2'], request.form['question3'], request.form['question4'], request.form['question5'], request.form['question6'], request.form['question7'], request.form['question8'], request.form['question9'], request.form['question10'], request.form['question11'])
        return jsonify("OK")
    else:
        return jsonify("Error: Please answer all questions")

@app.route('/vote-count')
def vote_count_route() -> Response:
    return jsonify(database.vote_count_without_skips())


@app.route('/get-prolific-url', methods=['POST'])
def get_prolific_url() -> Response:
    return jsonify({ "url" : PROLIFIC_REDIRECT_URL })

@app.route('/stats')
def stats_route() -> Response:
    stats = database.stats()

    stats['votes-not-consider-test'] = stats['votes'] - sum(stats['test-tweets-vote-count'])

    stats['test-tweets-vote-count'] = ', '.join(str(c) for c in stats['test-tweets-vote-count'])

    stats['histogram'] = [["Cantidad de votos", "Cantidad de tweets"]] + \
                         [[str(a), b] for a, b in stats['histogram'].items()]

    stats['votes-per-category']['No humor'] = stats['votes-per-category']['x']
    del stats['votes-per-category']['x']
    stats['votes-per-category']['Saltear'] = stats['votes-per-category']['n']
    del stats['votes-per-category']['n']
    stats['votes-per-category'] = [["Voto", "Cantidad de tweets"]] + \
                                  [[str(a), b] for a, b in stats['votes-per-category'].items()]

    return render_template('stats.html', stats=stats)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> Response:
    return send_from_directory('static', path)
