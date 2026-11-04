"""Tests for clasificahumor.database."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sqlalchemy.ext.asyncio

from clasificahumor import database


async def test_create_engine_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASS", "testpass")
    monkeypatch.setenv("DB_HOST", "db.local")
    monkeypatch.setenv("DB_NAME", "testdb")

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine) as mock_create:
        async with database.create_engine() as eng:
            assert eng is mock_engine
            mock_create.assert_called_once_with(
                "mysql+asyncmy://testuser:testpass@db.local/testdb?charset=utf8mb4",
                pool_size=10,
                pool_recycle=3600,
                pool_pre_ping=True,
            )


async def test_random_least_voted_unseen_tweets(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> None:
    # Initially, returns up to batch_size tweets
    tweets = await database.random_least_voted_unseen_tweets(seeded_db_engine, "sess-1", 3)
    assert len(tweets) == 3
    ids = {t["id"] for t in tweets}

    # Vote on one of them
    voted_id = next(iter(ids))
    await database.add_vote(seeded_db_engine, "sess-1", voted_id, "5", False)

    # Next call should not include the voted tweet
    new_tweets = await database.random_least_voted_unseen_tweets(seeded_db_engine, "sess-1", 3)
    new_ids = {t["id"] for t in new_tweets}
    assert voted_id not in new_ids

    # Test ignore_tweet_ids
    ignored_id = next(iter(new_ids))
    filtered_tweets = await database.random_least_voted_unseen_tweets(
        seeded_db_engine, "sess-1", 3, ignore_tweet_ids=[ignored_id]
    )
    filtered_ids = {t["id"] for t in filtered_tweets}
    assert ignored_id not in filtered_ids


async def test_random_tweets(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> None:
    tweets = await database.random_tweets(seeded_db_engine, 2)
    assert len(tweets) == 2
    assert "id" in tweets[0] and "text" in tweets[0]


async def test_add_vote_and_counts(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> None:
    # Initial counts
    assert await database.session_vote_count_with_skips(seeded_db_engine, "sess-vote") == 0
    assert await database.vote_count_without_skips(seeded_db_engine) == 0

    # Add a skip vote ('n')
    await database.add_vote(seeded_db_engine, "sess-vote", "101", "n", False)
    assert await database.session_vote_count_with_skips(seeded_db_engine, "sess-vote") == 1
    # vote_count_without_skips does not count 'n'
    assert await database.vote_count_without_skips(seeded_db_engine) == 0

    # Add a normal vote ('3')
    await database.add_vote(seeded_db_engine, "sess-vote", "102", "3", True)
    assert await database.session_vote_count_with_skips(seeded_db_engine, "sess-vote") == 2
    assert await database.vote_count_without_skips(seeded_db_engine) == 1

    # Adding an invalid vote does nothing
    await database.add_vote(seeded_db_engine, "sess-vote", "103", "invalid", False)
    assert await database.session_vote_count_with_skips(seeded_db_engine, "sess-vote") == 2


async def test_prolific_consent_and_finish(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> None:
    session_id = "prolific-test-1"

    # Consent
    await database.prolific_consent(seeded_db_engine, session_id)

    async with seeded_db_engine.connect() as conn:
        stmt = sqlalchemy.text("SELECT * FROM prolific WHERE session_id = 'prolific-test-1'")
        res = (await conn.execute(stmt)).fetchone()
        assert res is not None
        assert res[0] == session_id
        assert res[2] is None  # finish_date is None

    # Finish
    await database.prolific_finish(seeded_db_engine, session_id, "Buen estudio")

    async with seeded_db_engine.connect() as conn:
        stmt = sqlalchemy.text("SELECT finish_date, comments FROM prolific WHERE session_id = 'prolific-test-1'")
        res = (await conn.execute(stmt)).fetchone()
        assert res is not None
        assert res[0] is not None
        assert res[1] == "Buen estudio"


async def test_stats(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> None:
    # Add votes that pass the quality test:
    # tweet 1092855393188020224 vote='x'
    # tweet 1088158691633713152 vote='x'
    # tweet 1086371400431095813 vote='4'
    await database.add_vote(seeded_db_engine, "pass-session", "1092855393188020224", "x", False)
    await database.add_vote(seeded_db_engine, "pass-session", "1088158691633713152", "x", False)
    await database.add_vote(seeded_db_engine, "pass-session", "1086371400431095813", "4", False)
    await database.add_vote(seeded_db_engine, "pass-session", "101", "1", False)

    # Session that fails the test
    await database.add_vote(seeded_db_engine, "fail-session", "101", "n", False)

    stats = await database.stats(seeded_db_engine)
    assert stats["votes"] == 5
    assert stats["sessions"] == 2
    assert stats["votes-without-skips"] == 4
    assert stats["sessions-without-skips"] == 1
    assert stats["votes-pass-test"] == 4
    assert stats["sessions-pass-test"] == 1
    assert "x" in stats["votes-per-category"]
    assert "n" in stats["votes-per-category"]
    assert "1" in stats["votes-per-category"]
