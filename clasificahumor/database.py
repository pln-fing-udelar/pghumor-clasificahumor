"""Provides mechanisms to handle the database."""
import os
from typing import Any, Dict, List

import MySQLdb


def _connect():
    return MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
                           password=os.getenv('MYSQL_ROOT_PASSWORD'),
                           database=os.getenv('DB_NAME'), charset='utf8mb4', autocommit=True)


def random_least_voted_unseen_tweets(session_id: str, batch_size: int, ignore_tweet_ids: List[int]=None
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
    with _connect() as cursor:
        if ignore_tweet_ids is None:
            ignore_tweet_ids = []

        ignore_tweet_ids = [str(tweet_id) for tweet_id in ignore_tweet_ids]

        cursor.execute('SELECT t.tweet_id, text'
                       ' FROM tweets t'
                       '   LEFT JOIN (SELECT tweet_id FROM votes WHERE session_id = %(session_id)s) a'
                       '     ON t.tweet_id = a.tweet_id'
                       '   LEFT JOIN votes b'
                       '     ON t.tweet_id = b.tweet_id'
                       ' WHERE a.tweet_id IS NULL AND FIND_IN_SET(t.tweet_id, %(ignore_tweet_ids)s) = 0'
                       ' GROUP BY t.tweet_id'
                       ' ORDER BY weight DESC, COUNT(b.tweet_id), RAND()'
                       ' LIMIT %(limit)s',
                       {'session_id': session_id, 'limit': batch_size, 'ignore_tweet_ids': ','.join(ignore_tweet_ids)})
        return [{'id': id_, 'text': text} for id_, text in cursor.fetchall()]


def random_tweets(batch_size: int) -> List[Dict[str, Any]]:
    """
    Returns a random list tweets with size batch_size.

    Each tweet is represented as a dictionary with the fields 'id' and 'text'.

    :param batch_size: Size of the list to return
    :return: Random list of tweets with size batch_size
    """
    with _connect() as cursor:
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
        with _connect() as cursor:
            cursor.execute('INSERT INTO votes (tweet_id, session_id, vote)'
                           ' VALUES (%(tweet_id)s, %(session_id)s, %(vote)s)'
                           ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id',
                           {'tweet_id': tweet_id, 'session_id': session_id, 'vote': vote})


def vote_count() -> int:
    """Returns the vote count, not including skips."""
    with _connect() as cursor:
        cursor.execute('SELECT COUNT(*) FROM votes WHERE vote != \'n\'')
        return cursor.fetchone()[0]
