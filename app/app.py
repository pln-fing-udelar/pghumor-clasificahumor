from datetime import timedelta

from flask import Flask, send_from_directory, session

app = Flask(__name__)

# TODO:
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=1000)


@app.route('/tweets')
def tweets():
    return "Hello World!"


@app.route('/vote', methods=['POST'])
def vote():
    pass


# @app.route('/')
# def index():  # FIXME
#     return app.send_static_file('static/index.html')


@app.route('/<path:path>')  # , defaults={'file': 'static/index.html'}
def static_files(path):
    return send_from_directory('static', path)
