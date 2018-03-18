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
                        '   LEFT JOIN votes b'
                        '     ON t.tweet_id = b.tweet_id'
                        ' WHERE a.tweet_id IS NULL AND FIND_IN_SET(t.tweet_id, :ignore_tweet_ids) = 0'
                        ' GROUP BY t.tweet_id'
                        ' ORDER BY weight DESC, COUNT(b.tweet_id), RAND()'
                        ' LIMIT :limit')
STATEMENT_RANDOM_TWEETS = sqlalchemy.sql.text('SELECT t.tweet_id, text'
                                              ' FROM tweets t'
                                              ' ORDER BY RAND()'
                                              ' LIMIT :limit')
STATEMENT_ADD_VOTE = sqlalchemy.sql.text('INSERT INTO votes (tweet_id, session_id, vote)'
                                         ' VALUES (:tweet_id, :session_id, :vote)'
                                         ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id')
STATEMENT_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(*) FROM votes')
STATEMENT_VOTE_COUNT_WITHOUT_SKIPS = sqlalchemy.sql.text('SELECT COUNT(*) FROM votes WHERE vote != \'n\'')
STATEMENT_HISTOGRAM = sqlalchemy.sql.text('SELECT c, COUNT(*) as freq'
                                          ' FROM (SELECT COUNT(v.tweet_id) c'
                                          '        FROM tweets t'
                                          '          LEFT JOIN (SELECT tweet_id FROM votes WHERE vote != \'n\') v'
                                          '            ON t.tweet_id = v.tweet_id'
                                          '        WHERE weight = 1'
                                          '          AND t.tweet_id != 968699034540978176'  # The old test tweet.
                                          '        GROUP BY t.tweet_id) a'
                                          ' GROUP BY c'
                                          ' ORDER BY c')
STATEMENT_VOTE_COUNT_PER_CATEGORY = sqlalchemy.sql.text('SELECT vote, COUNT(*) FROM votes GROUP BY vote ORDER BY vote')


def create_engine():
    return sqlalchemy.create_engine(f'mysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}'
                                    f'/{os.getenv("DB_NAME")}?charset=utf8mb4', pool_size=10,
                                    pool_recycle=3600)


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
        with engine.connect() as connection:
            connection.execute(STATEMENT_ADD_VOTE, {'tweet_id': tweet_id, 'session_id': session_id, 'vote': vote})


def vote_count_without_skips() -> int:
    """Returns the vote count, not including skips."""
    with engine.connect() as connection:
        return connection.execute(STATEMENT_VOTE_COUNT_WITHOUT_SKIPS).fetchone()[0]


def stats() -> Dict[str, Any]:
    """Returns the vote count, vote count without skips, vote count histogram and votes per category."""
    with engine.connect() as connection:
        # TODO
        return {
            "votes": connection.execute(STATEMENT_VOTE_COUNT).fetchone()[0],
            "votes-without-skips": connection.execute(STATEMENT_VOTE_COUNT_WITHOUT_SKIPS).fetchone()[0],
            "histogram": dict(connection.execute(STATEMENT_HISTOGRAM).fetchall()),
            "votes-per-category": dict(connection.execute(STATEMENT_VOTE_COUNT_PER_CATEGORY).fetchall()),
        }
