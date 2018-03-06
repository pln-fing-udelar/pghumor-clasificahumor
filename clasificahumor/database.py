"""Provides mechanisms to handle the database."""
import os
from typing import Any, Dict, List

import MySQLdb


db = None


def _connect():
    global db
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
                         password=os.getenv('MYSQL_ROOT_PASSWORD'),
                         database=os.getenv('DB_NAME'), charset='utf8mb4', autocommit=True)


_connect()


def _reconnect_if_necessary():
    # In case of a _mysql_exceptions.OperationalError: (2006, 'MySQL server has gone away')
    # See https://stackoverflow.com/a/982873/1165181
    try:
        db.ping()
    except MySQLdb.OperationalError:
        _connect()


def random_least_voted_unseen_tweets(session_id: str, batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list of the least voted unseen tweets (by the session) with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id' and 'text'.

    :param session_id: Session ID
    :param batch_size: Size of the list to return
    :return: Random list of the least voted unseen tweets with size batch_size
    """
    _reconnect_if_necessary()
    with db.cursor() as cursor:
        cursor.execute('SELECT t.tweet_id, text'
                       ' FROM tweets t'
                       '   LEFT JOIN (SELECT tweet_id FROM votes WHERE session_id = %(session_id)s) a'
                       '     ON t.tweet_id = a.tweet_id'
                       '   LEFT JOIN votes b'
                       '     ON t.tweet_id = b.tweet_id'
                       ' WHERE a.tweet_id IS NULL'
                       ' GROUP BY t.tweet_id'
                       ' ORDER BY weight DESC, COUNT(*), RAND()'
                       ' LIMIT %(limit)s',
                       {'session_id': session_id, 'limit': batch_size})
        return [{'id': id_, 'text': text} for id_, text in cursor.fetchall()]


def random_tweets(batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list tweets with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id' and 'text'.

    :param batch_size: Size of the list to return
    :return: Random list of tweets with size batch_size
    """
    _reconnect_if_necessary()
    with db.cursor() as cursor:
        cursor.execute('SELECT t.tweet_id, text'
                       ' FROM tweets t'
                       ' ORDER BY RAND()'
                       ' LIMIT %(limit)s',
                       {'limit': batch_size})
        return [{'id': id_, 'text': text} for id_, text in cursor.fetchall()]


def add_vote(session_id: str, tweet_id: str, vote: str) -> None:
    """
    Adds a vote for a tweet by a determined session.

    If the vote is not one of ['1', '2', '3', '4', '5', 'x', 'n'], it will do nothing. If the session had already voted,
    the new vote will be ignored.

    :param session_id: Session ID
    :param tweet_id: Tweet ID
    :param vote: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    """
    if vote in ['1', '2', '3', '4', '5', 'x', 'n']:
        _reconnect_if_necessary()
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO votes (tweet_id, session_id, vote)'
                           ' VALUES (%(tweet_id)s, %(session_id)s, %(vote)s)'
                           ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id',
                           {'tweet_id': tweet_id, 'session_id': session_id, 'vote': vote})
