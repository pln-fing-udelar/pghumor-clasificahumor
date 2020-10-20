"""Provides mechanisms to handle the database."""
import os
from typing import Any, Dict, List

import sqlalchemy
import sqlalchemy.sql

STATEMENT_RANDOM_LEAST_VOTED_UNSEEN_TWEETS = \
    sqlalchemy.sql.text('SELECT t.tweet_id, text'
                        ' FROM tweets t'
                        '   LEFT JOIN (SELECT tweet_id FROM votes WHERE session_id = :session_id) a'
                        '     ON t.tweet_id = a.tweet_id'
                        '   LEFT JOIN (SELECT tweet_id FROM votes) b'
                        '     ON t.tweet_id = b.tweet_id'
                        ' WHERE a.tweet_id IS NULL AND FIND_IN_SET(t.tweet_id, :ignore_tweet_ids) = 0'
                        ' GROUP BY t.tweet_id'
                        ' ORDER BY weight DESC, COUNT(b.tweet_id), RAND()'
                        ' LIMIT :limit')
STATEMENT_RANDOM_TWEETS = sqlalchemy.sql.text('SELECT t.tweet_id, text'
                                              ' FROM tweets t'
                                              ' ORDER BY RAND()'
                                              ' LIMIT :limit')
STATEMENT_ADD_VOTE = sqlalchemy.sql.text('INSERT INTO votes (tweet_id, session_id, vote_humor, vote_offensive, vote_personal)'
                                         ' VALUES (:tweet_id, :session_id, :vote_humor, :vote_offensive, :vote_personal)'
                                         ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id')
STATEMENT_GET_FINISHED_TWEETS = sqlalchemy.sql.text('SELECT tweet_id FROM votes GROUP BY tweet_id HAVING count(*) >= 1')
STATEMENT_UPDATE_FINISHED_TWEETS = sqlalchemy.sql.text('UPDATE tweets SET weight=0 WHERE tweet_id IN :tweet_ids')
STATEMENT_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(*)'
                                           ' FROM votes v'
                                           # '   LEFT JOIN (SELECT session_id'
                                           # '               FROM votes'
                                           # '               WHERE tweet_id = 1092855393188020224 AND vote = \'x\') s1'
                                           # '     ON v.session_id = s1.session_id'
                                           # '   LEFT JOIN (SELECT session_id'
                                           # '               FROM votes'
                                           # '               WHERE tweet_id = 1088158691633713152 AND vote = \'x\') s2'
                                           # '     ON v.session_id = s2.session_id'
                                           # '   LEFT JOIN (SELECT session_id'
                                           # '               FROM votes'
                                           # '               WHERE tweet_id = 1086371400431095813'
                                           # '                 AND vote != \'x\''
                                           # '                 AND vote != \'n\') s3'
                                           # '     ON v.session_id = s3.session_id'
                                           # ' WHERE NOT :without_skips OR vote != \'n\')'
                                           # '   AND (NOT :pass_test'
                                           # '     OR (s1.session_id IS NOT NULL'
                                           # '       AND s2.session_id IS NOT NULL'
                                           # '       AND s3.session_id IS NOT NULL))')
                                           ' WHERE NOT :without_skips')
STATEMENT_SESSION_COUNT = sqlalchemy.sql.text('SELECT COUNT(DISTINCT v.session_id)'
                                              ' FROM votes v'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 1092855393188020224 AND vote = \'x\') s1'
                                              '     ON v.session_id = s1.session_id'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 1088158691633713152 AND vote = \'x\') s2'
                                              '     ON v.session_id = s2.session_id'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 1086371400431095813'
                                              '                 AND vote != \'x\''
                                              '                 AND vote != \'n\') s3'
                                              '     ON v.session_id = s3.session_id'
                                              ' WHERE (NOT :without_skips OR vote != \'n\')'
                                              '   AND (NOT :pass_test'
                                              '     OR (s1.session_id IS NOT NULL'
                                              '       AND s2.session_id IS NOT NULL'
                                              '       AND s3.session_id IS NOT NULL))')
STATEMENT_TEST_TWEETS_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(v.tweet_id) AS c'
                                                       ' FROM tweets t'
                                                       '   LEFT JOIN votes v ON t.tweet_id = v.tweet_id'
                                                       ' WHERE weight > 1'
                                                       ' GROUP BY t.tweet_id'
                                                       ' ORDER BY c DESC')
STATEMENT_HISTOGRAM = sqlalchemy.sql.text('SELECT c, COUNT(*) as freq'
                                          ' FROM (SELECT COUNT(v.tweet_id) c'
                                          '        FROM tweets t'
                                          '          LEFT JOIN (SELECT tweet_id FROM votes) v'  # WHERE vote != \'n\'
                                          '            ON t.tweet_id = v.tweet_id'
                                          '        WHERE weight <= 1 AND t.tweet_id <> 1088158691633713152'
                                          '        GROUP BY t.tweet_id) a'
                                          ' GROUP BY c'
                                          ' ORDER BY c')
STATEMENT_VOTE_COUNT_PER_CATEGORY = sqlalchemy.sql.text('SELECT vote, COUNT(*) FROM votes GROUP BY vote ORDER BY vote')

STATEMENT_ADD_ANNOTATOR = sqlalchemy.sql.text('INSERT INTO annotators (session_id, prolific_id, prolific_session_id, study_id, question1, question2, question3, question4, question5, question6)'
                                         ' VALUES (:session_id, :prolific_id, :prolific_session_id, :study_id, :question1, :question2, :question3, :question4, :question5, :question6)')

STATEMENT_ADD_PERSONALITY = sqlalchemy.sql.text('INSERT INTO personality (prolific_id, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10, question11)'
                                         ' VALUES (:prolific_id, :question1, :question2, :question3, :question4, :question5, :question6, :question7, :question8, :question9, :question10, :question11)')

STATEMENT_ADD_EVENT = sqlalchemy.sql.text('INSERT INTO events (session_id, event, content) VALUES (:session_id, :event, :content)')

STATEMENT_COUNT_PERSONALITY = sqlalchemy.sql.text('SELECT COUNT(*) FROM personality WHERE prolific_id = :prolific_id')

STATEMENT_GET_PROLIFIC_ID = sqlalchemy.sql.text('SELECT prolific_id FROM annotators WHERE session_id = :session_id ORDER BY form_sent DESC LIMIT 1')

STATEMENT_VOTES_BY_SESSION = sqlalchemy.sql.text('SELECT session_id,count(*) as vote_count FROM votes GROUP BY session_id')

STATEMENT_VOTES_BY_TWEET = sqlalchemy.sql.text('SELECT tweet_id,count(*) as vote_count FROM votes GROUP BY tweet_id')

STATEMENT_VOTE_COUNT_ALL = sqlalchemy.sql.text('SELECT COUNT(*) FROM votes v')

STATEMENT_SESSION_COUNT_ALL = sqlalchemy.sql.text('SELECT COUNT(DISTINCT v.session_id) FROM votes v')

STATEMENT_ANNOTATORS = sqlalchemy.sql.text('SELECT session_id, prolific_id FROM annotators')

STATEMENT_GET_VOTES = sqlalchemy.sql.text('SELECT tweet_id, session_id, vote_humor, vote_offensive, vote_personal, date FROM votes')

STATEMENT_GET_ANNOTATORS = sqlalchemy.sql.text('SELECT session_id, prolific_id, prolific_session_id, study_id, form_sent, question1, question2, question3, question4, question5, question6 FROM annotators')

STATEMENT_GET_PERSONALITIES = sqlalchemy.sql.text('SELECT prolific_id, form_sent, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10, question11 FROM personality')

STATEMENT_GET_EVENTS = sqlalchemy.sql.text('SELECT session_id, event, content, date FROM events')

STATEMENT_UPDATE_RESET_TWEETS = sqlalchemy.sql.text('UPDATE tweets SET weight=1 WHERE weight=0')

STATEMENT_DELETE_VOTES = sqlalchemy.sql.text('DELETE FROM votes')

STATEMENT_DELETE_PERSONALITY = sqlalchemy.sql.text('DELETE FROM personality')

STATEMENT_DELETE_ANNOTATORS = sqlalchemy.sql.text('DELETE FROM annotators')

STATEMENT_DELETE_EVENTS = sqlalchemy.sql.text('DELETE FROM events')

STATEMENT_DELETE_VOTES_FOR_SESSION = sqlalchemy.sql.text('DELETE FROM votes WHERE session_id = :session_id')

def create_engine():
    return sqlalchemy.create_engine('mysql://'+os.environ["DB_USER"]+':'+os.environ["DB_PASS"]+'@'+os.environ["DB_HOST"]+'/'+os.environ["DB_NAME"]+'?charset=utf8mb4', pool_size=10, pool_recycle=3600)


engine = create_engine()


def random_least_voted_unseen_tweets(session_id: str, batch_size: int, ignore_tweet_ids: List[int] = None
                                     ) -> List[Dict[str, Any]]:
    """
    Returns a random list of the least voted unseen tweets (by the session) with size batch_size, ignoring certain list
    of tweet IDs.

    If there are fewer than batch_size tweets that hold the condition, the response is padded with random tweets.

    Each tweet in the result is represented as a dictionary with the fields 'id' and 'text'.

    :param session_id: Session ID
    :param batch_size: Size of the list to return
    :param ignore_tweet_ids: List of tweet IDs to ignore, not returning them in the result
    :return: Random list of the least voted unseen tweets with size batch_size
    """
    with engine.connect() as connection:
        if ignore_tweet_ids is None:
            ignore_tweet_ids = []

        result = connection.execute(STATEMENT_RANDOM_LEAST_VOTED_UNSEEN_TWEETS,
                                    {'session_id': session_id, 'limit': batch_size,
                                     'ignore_tweet_ids': ','.join(str(tweet_id) for tweet_id in ignore_tweet_ids)})

        return [{'id': id_, 'text': text} for id_, text in result.fetchall()]


def random_tweets(batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list tweets with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id' and 'text'.

    :param batch_size: Size of the list to return
    :return: Random list of tweets with size batch_size
    """
    with engine.connect() as connection:
        result = connection.execute(STATEMENT_RANDOM_TWEETS, {'limit': batch_size})
        return [{'id': id_, 'text': text} for id_, text in result.fetchall()]

def add_vote(session_id: str, tweet_id: str, vote_humor: str, vote_offensive: str, vote_personal: str) -> None:
    """
    Adds a vote for a tweet by a determined session.

    :param session_id: Session ID
    :param tweet_id: Tweet ID
    :param vote_humor: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    :param vote_offensive: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    :param vote_personal: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    """
    if vote_humor in ['1', '2', '3', '4', '5', 'd', 'n'] and vote_offensive in ['1', '2', '3', '4', '5', 'n'] and vote_personal in ['1', '2', '3', '4', '5', 'n']:
        with engine.connect() as connection:
            connection.execute(STATEMENT_ADD_VOTE, {'tweet_id': tweet_id, 'session_id': session_id,
                                                    'vote_humor': vote_humor, 'vote_offensive': vote_offensive, 'vote_personal': vote_personal})

def update_finished_tweets():
    with engine.connect() as connection:
        finished_tweets = [str(t[0]) for t in connection.execute(STATEMENT_GET_FINISHED_TWEETS).fetchall()]
        if len(finished_tweets) == 0:
          return -1
        else:
          return connection.execute(STATEMENT_UPDATE_FINISHED_TWEETS, {'tweet_ids': tuple(finished_tweets)}).rowcount

def add_annotator(session_id, prolific_id, prolific_session_id, study_id, question1, question2, question3, question4, question5, question6) -> None:
    """
    Registers an annotator and their consent form

    :param session_id: Session ID
    :param prolific_id: Prolific ID
    :param prolific_session_id: Session ID from Prolific
    :param study_id: Study ID from Prolific
    :param question1: Answer to question1 in the form 'y' or 'n'
    :param question2: Answer to question2 in the form 'y' or 'n'
    :param question3: Answer to question3 in the form 'y' or 'n'
    :param question4: Answer to question4 in the form 'y' or 'n'
    :param question5: Answer to question5 in the form 'y' or 'n'
    :param question6: Answer to question6 in the form 'y' or 'n'
    """
    with engine.connect() as connection:
        connection.execute(STATEMENT_ADD_ANNOTATOR, {
          'session_id': session_id,
          'prolific_id': prolific_id,
          'prolific_session_id': prolific_session_id,
          'study_id': study_id,
          'question1': question1,
          'question2': question2,
          'question3': question3,
          'question4': question4,
          'question5': question5,
          'question6': question6})

def add_personality(prolific_id, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10, question11) -> None:
    """
    Registers the personality questionaire for an

    :param prolific_id: Prolific ID
    :param question[1-10]: Answer to question[1-10] from '1' or '7'
    :param question11: Answer to question11 with values in ['U','A','F','I']
    """
    with engine.connect() as connection:
        connection.execute(STATEMENT_ADD_PERSONALITY, {
          'prolific_id': prolific_id,
          'question1': question1,
          'question2': question2,
          'question3': question3,
          'question4': question4,
          'question5': question5,
          'question6': question6,
          'question7': question7,
          'question8': question8,
          'question9': question9,
          'question10': question10,
          'question11': question11})

def add_event(session_id, event, content) -> None:
    """
    Registers an envent

    :param session_id: Session ID
    :param event: Short event name
    :param content: Content associated to the event
    """
    with engine.connect() as connection:
        connection.execute(STATEMENT_ADD_EVENT, {
          'session_id': session_id,
          'event': event,
          'content': content})

def is_personality_registered(prolific_id):
    """
    Returns the number of personality surveys registered for a Prolific ID

    :param prolific_id: Prolific ID
    """
    with engine.connect() as connection:
        result = connection.execute(STATEMENT_COUNT_PERSONALITY, {'prolific_id': prolific_id})
        return {'count': result.fetchone()[0]}

def get_prolific_id(session_id):
    """
    Returns the Prolific ID associated to a session

    :param session_id: Session ID
    """
    with engine.connect() as connection:
        result = connection.execute(STATEMENT_GET_PROLIFIC_ID, {'session_id': session_id})
        return {'prolific_id': result.fetchone()[0]}

def vote_count_without_skips() -> int:
    """Returns the vote count, not including skips."""
    with engine.connect() as connection:
        return connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': True, 'pass_test': False}).fetchone()[0]


def stats() -> Dict[str, Any]:
    """Returns the vote count, vote count without skips, vote count histogram and votes per category."""
    with engine.connect() as connection:
        result = {
            'votes': connection.execute(STATEMENT_VOTE_COUNT_ALL, {}).fetchone()[0],
            'sessions': connection.execute(STATEMENT_SESSION_COUNT_ALL, {}).fetchone()[0],
            'votes_by_session_id': dict(connection.execute(STATEMENT_VOTES_BY_SESSION, {}).fetchall()),
            'votes_by_tweet_id': dict(connection.execute(STATEMENT_VOTES_BY_TWEET, {}).fetchall()),
            'annotators': connection.execute(STATEMENT_ANNOTATORS, {}).fetchall()
        }

    return result

def all_votes():
  with engine.connect() as connection:
    return connection.execute(STATEMENT_GET_VOTES, {}).fetchall()

def all_annotators():
  with engine.connect() as connection:
    return connection.execute(STATEMENT_GET_ANNOTATORS, {}).fetchall()

def all_personalities():
  with engine.connect() as connection:
    return connection.execute(STATEMENT_GET_PERSONALITIES, {}).fetchall()

def all_events():
  with engine.connect() as connection:
    return connection.execute(STATEMENT_GET_EVENTS, {}).fetchall()

def reset_state():
  with engine.connect() as connection:
    result = {
        'updated_tweets': connection.execute(STATEMENT_UPDATE_RESET_TWEETS, {}).rowcount,
        'deleted_votes': connection.execute(STATEMENT_DELETE_VOTES, {}).rowcount,
        'deleted_personalities': connection.execute(STATEMENT_DELETE_PERSONALITY, {}).rowcount,
        'deleted_annotators': connection.execute(STATEMENT_DELETE_ANNOTATORS, {}).rowcount,
        'deleted_events': connection.execute(STATEMENT_DELETE_EVENTS, {}).rowcount
    }

  return result

def delete_votes_session(session_id):
    with engine.connect() as connection:
        return connection.execute(STATEMENT_DELETE_VOTES_FOR_SESSION, {'session_id': session_id}).rowcount
