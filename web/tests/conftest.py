import datetime
import os
import random
import re
import sqlite3
from collections.abc import AsyncGenerator
from typing import Any

# Ensure test DB environment variables are set
os.environ.setdefault("DB_USER", "root")
os.environ.setdefault("DB_PASS", "password")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "pghumor")

import httpx2
import pytest
import sqlalchemy
import sqlalchemy.event
import sqlalchemy.ext.asyncio
from httpx2 import ASGITransport

from clasificahumor.__main__ import app

sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat(" "))
sqlite3.register_converter("TIMESTAMP", lambda val: datetime.datetime.fromisoformat(val.decode()))
sqlite3.register_converter("BOOL", lambda val: bool(int(val)))

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE accounts (
        account_id BIGINT NOT NULL PRIMARY KEY,
        name VARCHAR(100),
        followers BIGINT
    )
    """,
    """
    CREATE TABLE tweets (
        tweet_id BIGINT NOT NULL PRIMARY KEY,
        text VARCHAR(1120) NOT NULL,
        account_id BIGINT,
        origin VARCHAR(30) NOT NULL DEFAULT 'hose',
        lang VARCHAR(5) NOT NULL DEFAULT 'es',
        weight INT DEFAULT 1
    )
    """,
    """
    CREATE TABLE votes (
        tweet_id BIGINT NOT NULL,
        session_id CHAR(100) NOT NULL,
        vote CHAR(1) NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_offensive BOOL DEFAULT 0,
        PRIMARY KEY (tweet_id, session_id)
    )
    """,
    """
    CREATE TABLE prolific (
        session_id CHAR(100) NOT NULL PRIMARY KEY,
        consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finish_date TIMESTAMP NULL,
        comments VARCHAR(300) DEFAULT NULL
    )
    """,
]


def configure_sqlite_mysql_compat(engine: sqlalchemy.ext.asyncio.AsyncEngine) -> None:
    """Registers SQLite helper functions and query rewrites so MySQL queries run on SQLite."""

    @sqlalchemy.event.listens_for(engine.sync_engine, "connect")
    def _on_connect(dbapi_conn: Any, _: Any) -> None:
        dbapi_conn.create_function("RAND", 0, random.random)

        def _find_in_set(val: Any, set_str: str | None) -> int:
            if not set_str:
                return 0
            items = set_str.split(",")
            s_val = str(val)
            return (items.index(s_val) + 1) if s_val in items else 0

        dbapi_conn.create_function("FIND_IN_SET", 2, _find_in_set)

    @sqlalchemy.event.listens_for(engine.sync_engine, "before_cursor_execute", retval=True)
    def _before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> tuple[str, Any]:
        statement = re.sub(
            r"ON DUPLICATE KEY UPDATE.*",
            "ON CONFLICT DO NOTHING",
            statement,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return statement, parameters


@pytest.fixture
async def db_engine() -> AsyncGenerator[sqlalchemy.ext.asyncio.AsyncEngine]:
    """Provides an isolated in-memory SQLite database configured for MySQL compatibility."""
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    configure_sqlite_mysql_compat(engine)
    async with engine.begin() as conn:
        for stmt in SCHEMA_STATEMENTS:
            await conn.execute(sqlalchemy.text(stmt))
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def seeded_db_engine(
    db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> sqlalchemy.ext.asyncio.AsyncEngine:
    """Provides a database seeded with sample accounts and tweets."""
    async with db_engine.begin() as conn:
        await conn.execute(
            sqlalchemy.text("INSERT INTO accounts (account_id, name, followers) VALUES (1, 'HumorBot', 1000)")
        )
        await conn.execute(
            sqlalchemy.text(
                "INSERT INTO tweets (tweet_id, text, account_id, origin, lang, weight) VALUES "
                "(101, 'Primer chiste gracioso', 1, 'hose', 'es', 1), "
                "(102, 'Segundo chiste', 1, 'hose', 'es', 1), "
                "(103, 'Tercer tweet no gracioso', 1, 'hose', 'es', 1), "
                "(104, 'Cuarto tweet', 1, 'hose', 'es', 1), "
                "(1088158691633713152, 'Test tweet 1', 1, 'hose', 'es', 2), "
                "(1092855393188020224, 'Test tweet 2', 1, 'hose', 'es', 2), "
                "(1086371400431095813, 'Test tweet 3', 1, 'hose', 'es', 2)"
            )
        )
    return db_engine


@pytest.fixture
async def client(
    seeded_db_engine: sqlalchemy.ext.asyncio.AsyncEngine,
) -> AsyncGenerator[httpx2.AsyncClient]:
    """Test HTTP client with database engine hooked to the seeded SQLite database."""

    async def inject_db(scope: Any, receive: Any, send: Any) -> None:
        scope.setdefault("state", {})["database_engine"] = seeded_db_engine
        await app(scope, receive, send)

    transport = ASGITransport(app=inject_db)
    async with httpx2.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
