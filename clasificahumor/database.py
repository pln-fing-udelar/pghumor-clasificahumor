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
                        '   LEFT JOIN (SELECT tweet_id FROM votes WHERE vote != \'n\') b'
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
STATEMENT_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(*)'
                                           ' FROM votes v'
                                           '   LEFT JOIN (SELECT session_id'
                                           '               FROM votes'
                                           '               WHERE tweet_id = 965857626843172864 AND vote = \'x\') s1'
                                           '     ON v.session_id = s1.session_id'
                                           '   LEFT JOIN (SELECT session_id'
                                           '               FROM votes'
                                           '               WHERE tweet_id = 965758586747047936 AND vote = \'x\') s2'
                                           '     ON v.session_id = s2.session_id'
                                           '   LEFT JOIN (SELECT session_id'
                                           '               FROM votes'
                                           '               WHERE tweet_id = 301481614033170432) s3'
                                           '     ON v.session_id = s3.session_id'
                                           ' WHERE (:without_skips = FALSE OR vote != \'n\')'
                                           '   AND (:pass_test = FALSE'
                                           '     OR (s1.session_id IS NOT NULL'
                                           '       AND s2.session_id IS NOT NULL'
                                           '       AND (s3.session_id IS NULL OR (s3.session_id != \'x\''
                                           '         AND s3.session_id != \'n\'))))')
STATEMENT_SESSION_COUNT = sqlalchemy.sql.text('SELECT COUNT(DISTINCT v.session_id)'
                                              ' FROM votes v'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 965857626843172864 AND vote = \'x\') s1'
                                              '     ON v.session_id = s1.session_id'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 965758586747047936 AND vote = \'x\') s2'
                                              '     ON v.session_id = s2.session_id'
                                              '   LEFT JOIN (SELECT session_id'
                                              '               FROM votes'
                                              '               WHERE tweet_id = 301481614033170432) s3'
                                              '     ON v.session_id = s3.session_id'
                                              ' WHERE (:without_skips = FALSE OR vote != \'n\')'
                                              '   AND (:pass_test = FALSE'
                                              '     OR (s1.session_id IS NOT NULL'
                                              '       AND s2.session_id IS NOT NULL'
                                              '       AND (s3.session_id IS NULL OR (s3.session_id != \'x\''
                                              '         AND s3.session_id != \'n\'))))')
STATEMENT_TEST_TWEETS_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(v.tweet_id) AS c'
                                                       ' FROM tweets t'
                                                       '   LEFT JOIN votes v ON t.tweet_id = v.tweet_id'
                                                       ' WHERE weight > 1 OR t.tweet_id = 968699034540978176'
                                                       ' GROUP BY t.tweet_id'
                                                       ' ORDER BY c DESC')
STATEMENT_HISTOGRAM = sqlalchemy.sql.text('SELECT c, COUNT(*) as freq'
                                          ' FROM (SELECT COUNT(v.tweet_id) c'
                                          '        FROM tweets t'
                                          '          LEFT JOIN (SELECT tweet_id FROM votes) v'  # WHERE vote != \'n\'
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
        return connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': True, 'pass_test': False}).fetchone()[0]


def stats() -> Dict[str, Any]:
    """Returns the vote count, vote count without skips, vote count histogram and votes per category."""
    with engine.connect() as connection:
        return {
            'votes': connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': False,
                                                               'pass_test': False}).fetchone()[0],
            'sessions': connection.execute(STATEMENT_SESSION_COUNT, {'without_skips': False,
                                                                     'pass_test': False}).fetchone()[0],
            'test-tweets-vote-count': [t[0] for t in connection.execute(STATEMENT_TEST_TWEETS_VOTE_COUNT).fetchall()],
            'histogram': dict(connection.execute(STATEMENT_HISTOGRAM).fetchall()),
            'votes-per-category': dict(connection.execute(STATEMENT_VOTE_COUNT_PER_CATEGORY).fetchall()),

            'votes-without-skips': connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': True,
                                                                             'pass_test': False}).fetchone()[0],
            'sessions-without-skips': connection.execute(STATEMENT_SESSION_COUNT, {'without_skips': True,
                                                                                   'pass_test': False}).fetchone()[0],

            'votes-pass-test': connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': True,
                                                                         'pass_test': True}).fetchone()[0],
            'sessions-pass-test': connection.execute(STATEMENT_SESSION_COUNT, {'without_skips': True,
                                                                               'pass_test': True}).fetchone()[0],
        }
