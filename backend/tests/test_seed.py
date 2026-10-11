"""Seeding is idempotent and preserves runtime data."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models import Plant, SearchQuery
from app.services.seed import seed_database
from tests.conftest import run_on, session


def test_seed_inserts_once_and_is_idempotent(db):
    engine, loop = db

    async def run():
        result = None
        async with await session(engine) as db_session:
            first = await seed_database(db_session)
            await db_session.commit()

            # Simulate accumulated runtime data: a popularity bump and a search log.
            plant = (await db_session.execute(select(Plant))).scalars().first()
            assert plant is not None
            plant.search_count += 5
            db_session.add(SearchQuery(query="tomato", plant_id=plant.id, matched=True))
            await db_session.commit()

            second = await seed_database(db_session)
            await db_session.commit()

            total = await db_session.scalar(select(func.count()).select_from(Plant))
            queries = await db_session.scalar(select(func.count()).select_from(SearchQuery))
            refreshed = (await db_session.execute(select(Plant))).scalars().first()
            assert refreshed is not None
            result = first, second, total, queries, refreshed.search_count
        return result

    first, second, total, queries, search_count = run_on(loop, run())

    assert first.inserted == 17
    assert first.regions == 90
    assert first.updated == 0

    assert second.inserted == 0
    assert second.updated == 0

    assert total == 17
    assert queries == 1
    # Runtime popularity data survives a reseed untouched.
    assert search_count == 5


def test_seed_force_refreshes_content_but_preserves_popularity(db):
    engine, loop = db

    async def run():
        async with await session(engine) as db_session:
            first = await seed_database(db_session)
            await db_session.commit()

            plant = (await db_session.execute(select(Plant))).scalars().first()
            assert plant is not None
            plant.search_count = 9
            await db_session.commit()

            forced = await seed_database(db_session, force=True)
            await db_session.commit()

            refreshed = (await db_session.execute(select(Plant))).scalars().first()
            assert refreshed is not None
            return first.inserted, forced.inserted, forced.updated, refreshed.search_count

    inserted_first, inserted_second, updated_second, search_count = run_on(loop, run())
    assert inserted_first == 17
    assert inserted_second == 0
    assert updated_second == 17
    assert search_count == 9