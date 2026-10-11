"""Shared test fixtures.

Each test gets its own in-memory SQLite engine and one event loop that lives
for the whole test. Everything - schema creation, the scenario itself, and
engine disposal - runs on that same loop, so Greenlet-spawned async SQL never
crosses a closed loop (no async pytest plugin needed).
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any, TypeVar, cast

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db.base import Base

T = TypeVar("T")


@pytest.fixture
def db() -> Iterator[tuple[AsyncEngine, asyncio.AbstractEventLoop]]:
    loop = asyncio.new_event_loop()
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )

    async def create_schema() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(create_schema())
    try:
        yield engine, loop
    finally:
        loop.run_until_complete(engine.dispose())
        loop.close()


def run_on(loop: asyncio.AbstractEventLoop, coro: Any) -> T:
    """Run a coroutine on the fixture's own loop and return its result."""
    return cast(T, loop.run_until_complete(coro))


async def session(engine: AsyncEngine) -> AsyncSession:
    maker = async_sessionmaker(engine, expire_on_commit=False)
    return maker()