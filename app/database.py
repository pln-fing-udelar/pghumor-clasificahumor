"""Provides mechanisms to handle the database."""
import os
from typing import Any, Dict, List

import MySQLdb

db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('MYSQL_ROOT_PASSWORD'),
                     database=os.getenv('DB_NAME'))


# TODO: create the necessary SQL indices.

# TODO: test with not voted tweets to see what happens. Create tests?
def random_least_voted_unseen_tweets(session_id: str, batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list of the least voted unseen tweets (by the session) with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id_tweet' and 'text_tweet'.

    :param session_id: Session ID
    :param batch_size: Size of the list to return
    :return: Random list of the least voted unseen tweets with size batch_size
    """
    cursor = db.cursor()
    cursor.execute('SELECT t.id_tweet, text_tweet'
                   ' FROM tweets t'
                   '   LEFT JOIN (SELECT id_tweet, session_id FROM audit_table WHERE session_id != %(session_id)s) a'
                   '     ON t.id_tweet = a.id_tweet'
                   ' GROUP BY t.id_tweet'
                   ' ORDER BY COUNT(a.session_id), RAND()'
                   ' LIMIT %(limit)s',
                   {'session_id': session_id, 'limit': batch_size})
    return [{'id_tweet': id_, 'text_tweet': text} for id_, text in cursor.fetchall()]


def random_tweets(batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list tweets with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id_tweet' and 'text_tweet'.

    :param batch_size: Size of the list to return
    :return: Random list of tweets with size batch_size
    """
    cursor = db.cursor()
    cursor.execute('SELECT t.id_tweet, text_tweet'
                   ' FROM tweets t'
                   ' ORDER BY RAND()'
                   ' LIMIT %(limit)s',
                   {'limit': batch_size})
    return [{'id_tweet': id_, 'text_tweet': text} for id_, text in cursor.fetchall()]


def add_vote(session_id: str, tweet_id: str, vote: str) -> None:
    """
    Adds a vote for a tweet by a determined session.

    If the vote is not one of ['1', '2', '3', '4', '5', 'x', 'n'], it will do nothing.

    :param session_id: Session ID
    :param tweet_id: Tweet ID
    :param vote: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    """
    if vote in ['1', '2', '3', '4', '5', 'x', 'n']:
        cursor = db.cursor()
        cursor.execute('INSERT INTO audit_table (id_tweet, session_id, votacion)'
                       ' VALUES (%(tweet_id)s, %(session_id)s, %(vote)s)',
                       {'tweet_id': tweet_id, 'session_id': session_id, 'vote': vote})
