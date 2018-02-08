from datetime import timedelta
import os

from flask import Flask, request, send_from_directory, session
import MySQLdb

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('MYSQL_ROOT_PASSWORD'),
                     database=os.getenv('DB_NAME'))

BATCH_SIZE = 3


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=1000)


@app.route('/tweets')
def tweets():
    session_id = request.cookies.get('session')

    # TODO: create the necessary SQL indices.

    cursor = db.cursor()
    cursor.execute('SELECT t.id_tweet, text_tweet, COUNT(a.session_id) as c'
                   ' FROM tweets t'
                   '   LEFT JOIN (SELECT id_tweet, session_id FROM audit_table WHERE session_id != %(session_id)s) a'
                   '     ON t.id_tweet = a.id_tweet'
                   ' WHERE a.id_tweet IS NULL'
                   ' GROUP BY t.id_tweet'
                   ' ORDER BY c, RAND()'
                   ' LIMIT %(limit)s',
                   {'session_id': session_id, 'limit': BATCH_SIZE})
    app.logger.info(cursor.fetchall())  # FIXME: not logging
    return "a"


@app.route('/vote', methods=['POST'])
def vote():  # TODO: and get new tweet?
    pass


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)
