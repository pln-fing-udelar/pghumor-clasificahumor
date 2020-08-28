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
STATEMENT_ADD_VOTE = sqlalchemy.sql.text('INSERT INTO votes (tweet_id, session_id, vote, is_offensive)'
                                         ' VALUES (:tweet_id, :session_id, :vote, :is_offensive)'
                                         ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id')
STATEMENT_ADD_VOTE_2020 = sqlalchemy.sql.text('INSERT INTO votes2020 (tweet_id, session_id, vote_humor, vote_offensive, vote_personal)'
                                         ' VALUES (:tweet_id, :session_id, :vote_humor, :vote_offensive, :vote_personal)'
                                         ' ON DUPLICATE KEY UPDATE tweet_id = tweet_id')
STATEMENT_VOTE_COUNT = sqlalchemy.sql.text('SELECT COUNT(*)'
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


def create_engine():
    return sqlalchemy.create_engine(f'mysql://{os.environ["DB_USER"]}:{os.environ["DB_PASS"]}@{os.environ["DB_HOST"]}'
                                    f'/{os.environ["DB_NAME"]}?charset=utf8mb4', pool_size=10,
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


def add_vote(session_id: str, tweet_id: str, vote: str, is_offensive: bool) -> None:
    """
    Adds a vote for a tweet by a determined session.

    If the vote is not one of ['1', '2', '3', '4', '5', 'x', 'n'], it will do nothing. If the session had already voted,
    the new vote will be ignored.

    :param session_id: Session ID
    :param tweet_id: Tweet ID
    :param vote: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    :param is_offensive: If the tweet is considered offensive
    """
    if vote in ['1', '2', '3', '4', '5', 'x', 'n']:
        with engine.connect() as connection:
            connection.execute(STATEMENT_ADD_VOTE, {'tweet_id': tweet_id, 'session_id': session_id, 'vote': vote,
                                                    'is_offensive': is_offensive})

def add_vote_2020(session_id: str, tweet_id: str, vote_humor: str, vote_offensive: str, vote_personal: str) -> None:
    """
    Adds a vote for a tweet by a determined session.

    :param session_id: Session ID
    :param tweet_id: Tweet ID
    :param vote_humor: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    :param vote_offensive: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    :param vote_personal: Vote of the tweet: '1' to '5' for the stars, 'x' for non-humorous and 'n' for skipped
    """
    if vote_humor in ['1', '2', '3', '4', '5', 'x', 'n'] and vote_offensive in ['1', '2', '3', '4', '5', 'x', 'n'] and vote_personal in ['1', '2', '3', '4', '5', 'x', 'n']:
        with engine.connect() as connection:
            connection.execute(STATEMENT_ADD_VOTE_2020, {'tweet_id': tweet_id, 'session_id': session_id,
                                                    'vote_humor': vote_humor, 'vote_offensive': vote_offensive, 'vote_personal': vote_personal})


def vote_count_without_skips() -> int:
    """Returns the vote count, not including skips."""
    with engine.connect() as connection:
        return connection.execute(STATEMENT_VOTE_COUNT, {'without_skips': True, 'pass_test': False}).fetchone()[0]


def stats() -> Dict[str, Any]:
    """Returns the vote count, vote count without skips, vote count histogram and votes per category."""
    with engine.connect() as connection:
        result = {
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

    for category in ['1', '2', '3', '4', '5', 'x', 'n']:
        result['votes-per-category'].setdefault(category, 0)

    return result
