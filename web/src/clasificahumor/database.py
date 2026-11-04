"""Provides mechanisms to handle the database."""

import os
from collections.abc import AsyncGenerator, Iterable, MutableMapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.sql

TYPE_TWEET = MutableMapping[str, Any]
TYPE_TWEET_ID = int | str

VOTE_CHOICES = frozenset(("1", "2", "3", "4", "5", "x", "n"))

STATEMENT_RANDOM_LEAST_VOTED_UNSEEN_TWEETS = sqlalchemy.sql.text(
    "SELECT t.tweet_id, text"
    " FROM tweets t"
    "   LEFT JOIN (SELECT tweet_id FROM votes WHERE session_id = :session_id) a"
    "     ON t.tweet_id = a.tweet_id"
    "   LEFT JOIN (SELECT tweet_id FROM votes WHERE vote != 'n') b"
    "     ON t.tweet_id = b.tweet_id"
    " WHERE a.tweet_id IS NULL AND FIND_IN_SET(t.tweet_id, :ignore_tweet_ids) = 0"
    " GROUP BY t.tweet_id, weight"
    " ORDER BY weight DESC, COUNT(b.tweet_id), RAND()"
    " LIMIT :limit"
)
STATEMENT_RANDOM_TWEETS = sqlalchemy.sql.text("SELECT t.tweet_id, text FROM tweets t ORDER BY RAND() LIMIT :limit")
STATEMENT_ADD_VOTE = sqlalchemy.sql.text(
    "INSERT INTO votes (tweet_id, session_id, vote, is_offensive)"
    " VALUES (:tweet_id, :session_id, :vote, :is_offensive)"
    " ON DUPLICATE KEY UPDATE tweet_id = tweet_id"
)
STATEMENT_SESSION_VOTE_COUNT = sqlalchemy.sql.text(
    "SELECT COUNT(*) FROM votes v WHERE session_id = :session_id AND (NOT :without_skips OR vote != 'n')"
)
STATEMENT_VOTE_COUNT = sqlalchemy.sql.text(
    "SELECT COUNT(*)"
    " FROM votes v"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1092855393188020224 AND vote = 'x') s1"
    "     ON v.session_id = s1.session_id"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1088158691633713152 AND vote = 'x') s2"
    "     ON v.session_id = s2.session_id"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1086371400431095813"
    "                 AND vote != 'x'"
    "                 AND vote != 'n') s3"
    "     ON v.session_id = s3.session_id"
    " WHERE (NOT :without_skips OR vote != 'n')"
    "   AND (NOT :pass_test"
    "     OR (s1.session_id IS NOT NULL"
    "       AND s2.session_id IS NOT NULL"
    "       AND s3.session_id IS NOT NULL))"
)
STATEMENT_SESSION_COUNT = sqlalchemy.sql.text(
    "SELECT COUNT(DISTINCT v.session_id)"
    " FROM votes v"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1092855393188020224 AND vote = 'x') s1"
    "     ON v.session_id = s1.session_id"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1088158691633713152 AND vote = 'x') s2"
    "     ON v.session_id = s2.session_id"
    "   LEFT JOIN (SELECT session_id"
    "               FROM votes"
    "               WHERE tweet_id = 1086371400431095813"
    "                 AND vote != 'x'"
    "                 AND vote != 'n') s3"
    "     ON v.session_id = s3.session_id"
    " WHERE (NOT :without_skips OR vote != 'n')"
    "   AND (NOT :pass_test"
    "     OR (s1.session_id IS NOT NULL"
    "       AND s2.session_id IS NOT NULL"
    "       AND s3.session_id IS NOT NULL))"
)
STATEMENT_TEST_TWEETS_VOTE_COUNT = sqlalchemy.sql.text(
    "SELECT COUNT(v.tweet_id) AS c"
    " FROM tweets t"
    "   LEFT JOIN votes v ON t.tweet_id = v.tweet_id"
    " WHERE weight > 1"
    " GROUP BY t.tweet_id"
    " ORDER BY c DESC"
)
STATEMENT_HISTOGRAM = sqlalchemy.sql.text(
    "SELECT c, COUNT(*) as freq"
    " FROM (SELECT COUNT(v.tweet_id) c"
    "        FROM tweets t"
    "          LEFT JOIN (SELECT tweet_id FROM votes) v"
    "            ON t.tweet_id = v.tweet_id"
    "        WHERE weight <= 1 AND t.tweet_id <> 1088158691633713152"
    "        GROUP BY t.tweet_id) a"
    " GROUP BY c"
    " ORDER BY c"
)
STATEMENT_VOTE_COUNT_PER_CATEGORY = sqlalchemy.sql.text("SELECT vote, COUNT(*) FROM votes GROUP BY vote ORDER BY vote")

STATEMENT_PROLIFIC_CONSENT = sqlalchemy.sql.text(
    "INSERT INTO prolific (session_id) VALUES (:session_id) ON DUPLICATE KEY UPDATE session_id = session_id"
)

STATEMENT_PROLIFIC_FINISH = sqlalchemy.sql.text(
    "UPDATE prolific SET finish_date = :finish_date, comments = :comments WHERE session_id = :session_id"
)


@asynccontextmanager
async def create_engine() -> AsyncGenerator[sqlalchemy.ext.asyncio.AsyncEngine]:
    """Creates and yields an async SQLAlchemy engine using DB environment variables."""
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        f"mysql+asyncmy://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}"
        f"/{os.environ['DB_NAME']}?charset=utf8mb4",
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


async def random_least_voted_unseen_tweets(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    session_id: str,
    batch_size: int,
    ignore_tweet_ids: Iterable[TYPE_TWEET_ID] = (),
) -> list[TYPE_TWEET]:
    """Returns a random list of the least voted unseen tweets with size batch_size."""
    ignore_str = ",".join(str(tid) for tid in ignore_tweet_ids)
    async with engine.connect() as connection:
        result = await connection.execute(
            STATEMENT_RANDOM_LEAST_VOTED_UNSEEN_TWEETS,
            {
                "session_id": session_id,
                "limit": batch_size,
                "ignore_tweet_ids": ignore_str,
            },
        )
        return [{"id": str(id_), "text": text} for id_, text in result]


async def random_tweets(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    batch_size: int,
) -> list[TYPE_TWEET]:
    """Returns a random list of tweets with size batch_size."""
    async with engine.connect() as connection:
        result = await connection.execute(STATEMENT_RANDOM_TWEETS, {"limit": batch_size})
        return [{"id": str(id_), "text": text} for id_, text in result]


async def add_vote(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    session_id: str,
    tweet_id: TYPE_TWEET_ID,
    vote: str,
    is_offensive: bool,
) -> None:
    """Adds a vote for a tweet by a determined session."""
    if vote in VOTE_CHOICES:
        async with engine.begin() as connection:
            await connection.execute(
                STATEMENT_ADD_VOTE,
                {"tweet_id": tweet_id, "session_id": session_id, "vote": vote, "is_offensive": is_offensive},
            )


async def session_vote_count_with_skips(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    session_id: str,
) -> int:
    """Returns the vote count for a given session ID, including skips."""
    async with engine.connect() as connection:
        result = await connection.execute(
            STATEMENT_SESSION_VOTE_COUNT, {"session_id": session_id, "without_skips": False}
        )
        row = result.fetchone()
        return int(row[0]) if row else 0


async def vote_count_without_skips(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> int:
    """Returns the total vote count, not including skips."""
    async with engine.connect() as connection:
        result = await connection.execute(STATEMENT_VOTE_COUNT, {"without_skips": True, "pass_test": False})
        row = result.fetchone()
        return int(row[0]) if row else 0


async def prolific_consent(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    session_id: str,
) -> None:
    """Sets the current time as the consent date for the prolific session ID."""
    async with engine.begin() as connection:
        await connection.execute(STATEMENT_PROLIFIC_CONSENT, {"session_id": session_id})


async def prolific_finish(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
    session_id: str,
    comments: str,
) -> None:
    """Sets the finish date and comments for the prolific session ID."""
    async with engine.begin() as connection:
        await connection.execute(
            STATEMENT_PROLIFIC_FINISH,
            {"session_id": session_id, "finish_date": datetime.now(UTC), "comments": comments},
        )


async def stats(
    engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> dict[str, Any]:
    """Returns the vote count, vote count without skips, histogram, and votes per category."""
    async with engine.connect() as connection:
        votes_row = (
            await connection.execute(STATEMENT_VOTE_COUNT, {"without_skips": False, "pass_test": False})
        ).fetchone()
        sessions_row = (
            await connection.execute(STATEMENT_SESSION_COUNT, {"without_skips": False, "pass_test": False})
        ).fetchone()
        test_tweets_res = await connection.execute(STATEMENT_TEST_TWEETS_VOTE_COUNT)
        histogram_res = await connection.execute(STATEMENT_HISTOGRAM)
        category_res = await connection.execute(STATEMENT_VOTE_COUNT_PER_CATEGORY)
        votes_without_skips_row = (
            await connection.execute(STATEMENT_VOTE_COUNT, {"without_skips": True, "pass_test": False})
        ).fetchone()
        sessions_without_skips_row = (
            await connection.execute(STATEMENT_SESSION_COUNT, {"without_skips": True, "pass_test": False})
        ).fetchone()
        votes_pass_test_row = (
            await connection.execute(STATEMENT_VOTE_COUNT, {"without_skips": True, "pass_test": True})
        ).fetchone()
        sessions_pass_test_row = (
            await connection.execute(STATEMENT_SESSION_COUNT, {"without_skips": True, "pass_test": True})
        ).fetchone()

        result: dict[str, Any] = {
            "votes": int(votes_row[0]) if votes_row else 0,
            "sessions": int(sessions_row[0]) if sessions_row else 0,
            "test-tweets-vote-count": [int(t[0]) for t in test_tweets_res],
            "histogram": {int(k): int(v) for k, v in histogram_res},
            "votes-per-category": {str(k): int(v) for k, v in category_res},
            "votes-without-skips": int(votes_without_skips_row[0]) if votes_without_skips_row else 0,
            "sessions-without-skips": int(sessions_without_skips_row[0]) if sessions_without_skips_row else 0,
            "votes-pass-test": int(votes_pass_test_row[0]) if votes_pass_test_row else 0,
            "sessions-pass-test": int(sessions_pass_test_row[0]) if sessions_pass_test_row else 0,
        }

    for category in VOTE_CHOICES:
        result["votes-per-category"].setdefault(category, 0)

    return result
