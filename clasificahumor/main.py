from datetime import timedelta
import datetime
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
VOTES_SIZE = 100


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
    session_id = get_session_id()
    if 'votes' in request.form and int(request.form['votes']) >= VOTES_SIZE:
        database.add_event(session_id, "VOTE_READY", str(request.form['votes']))
        return jsonify({ "msg": "OK" })
    else:
        msg = 'ERROR: %s votes expected, %s found' % (VOTES_SIZE,request.form['votes'])
        database.add_event(session_id, "VOTE_NOT_READY", msg)
        return jsonify({ "msg": msg})

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
        database.add_event(session_id, "REGISTER", "prolific_id: " + str(prolific_id))
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
        database.add_event(session_id, "SURVEY_ADDED", "prolific_id: " + str(prolific_id))
        return jsonify("OK")
    else:
        return jsonify("Error: Please answer all questions")

@app.route('/vote-count')
def vote_count_route() -> Response:
    return jsonify(database.vote_count_without_skips())

@app.route('/close-instructions', methods=['POST'])
def close_instructions() -> Response:
    session_id = get_session_id()
    database.add_event(session_id, "CLOSE_INSTRUCTIONS", "")
    return jsonify("OK")

@app.route('/get-prolific-url', methods=['POST'])
def get_prolific_url() -> Response:
    session_id = get_session_id()
    database.add_event(session_id, "GO_BACK_TO_PROLIFIC", request.form['comments'])
    return jsonify({ "url" : PROLIFIC_REDIRECT_URL })

@app.route('/stats')
def stats_route() -> Response:
    stats = database.stats()

    annotators = {}
    for session_id,prolific_id in stats['annotators']:
        annotators[session_id] = prolific_id

    stats['votes_by_prolific_id'] = {annotators[session_id] : stats['votes_by_session_id'][session_id] for session_id in stats['votes_by_session_id']}

    tweets_by_vote_count = {}
    for tweet_id in stats['votes_by_tweet_id']:
        vote_count = stats['votes_by_tweet_id'][tweet_id]
        tweets_by_vote_count[vote_count] = tweets_by_vote_count.get(vote_count,0) + 1

    stats['tweets_by_vote_count'] = tweets_by_vote_count

    return render_template('stats.html', stats=stats)

@app.route("/download-votes")
def download_votes():
    rows = []
    rows.append("tweet_id,session_id,vote_humor,vote_offensive,vote_personal,date")
    votes = database.all_votes()
    for votes_data in votes:
        rows.append(",".join([str(d) for d in votes_data]))

    return Response(
        "\n".join(rows),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=votes.csv"})

@app.route("/download-annotators")
def download_annotators():
    rows = []
    rows.append("session_id,prolific_id,prolific_session_id,study_id,form_sent,question1,question2,question3,question4,question5,question6")
    annotators = database.all_annotators()
    for annotators_data in annotators:
        rows.append(",".join([wrap_escape(str(d)) for d in annotators_data]))

    return Response(
        "\n".join(rows),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=annotators.csv"})

@app.route("/download-personalities")
def download_personalities():
    rows = []
    rows.append("prolific_id,form_sent,question1,question2,question3,question4,question5,question6,question7,question8,question9,question10,question11")
    personalities = database.all_personalities()
    for personalities_data in personalities:
        rows.append(",".join([wrap_escape(str(d)) for d in personalities_data]))

    return Response(
        "\n".join(rows),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=personalities.csv"})

@app.route("/download-events")
def download_events():
    rows = []
    rows.append("session_id,event,content,date")
    events = database.all_events()
    for events_data in events:
        rows.append(",".join([wrap_escape(str(d)) for d in events_data]))

    return Response(
        "\n".join(rows),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=events.csv"})

def wrap_escape(s):
    return '"' + s.replace('"','""') + '"'

@app.route("/update-finished")
def update_finished():
    updated = database.update_finished_tweets()
    return jsonify({'updated': updated})

@app.route("/backup-and-reset")
def backup_and_reset():
    results = {}
    current_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

    with open('backup_' + current_date + '_votes.csv','w') as f:
        f.write("tweet_id,session_id,vote_humor,vote_offensive,vote_personal,date\n")
        votes = database.all_votes()
        for votes_data in votes:
            f.write(",".join([str(d) for d in votes_data]) + "\n")
        results['backup_votes'] = (len(votes), os.path.realpath(f.name))

    with open('backup_' + current_date + '_annotators.csv','w') as f:
        f.write("session_id,prolific_id,prolific_session_id,study_id,form_sent,question1,question2,question3,question4,question5,question6\n")
        annotators = database.all_annotators()
        for annotators_data in annotators:
            f.write(",".join([wrap_escape(str(d)) for d in annotators_data]) + "\n")
        results['backup_annotators'] = (len(annotators), os.path.realpath(f.name))

    with open('backup_' + current_date + '_personalities.csv','w') as f:
        f.write("prolific_id,form_sent,question1,question2,question3,question4,question5,question6,question7,question8,question9,question10,question11\n")
        personalities = database.all_personalities()
        for personalities_data in personalities:
            f.write(",".join([wrap_escape(str(d)) for d in personalities_data]) + "\n")
        results['backup_personalities'] = (len(personalities), os.path.realpath(f.name))

    with open('backup_' + current_date + '_events.csv','w') as f:
        f.write("session_id,event,content,date")
        events = database.all_events()
        for events_data in events:
            f.write(",".join([wrap_escape(str(d)) for d in events_data]) + "\n")
        results['backup_events'] = (len(events), os.path.realpath(f.name))

    res = database.reset_state()
    for k in res:
        results[k] = res[k]

    return jsonify(results)

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files_route(path) -> Response:
    return send_from_directory('static', path)
