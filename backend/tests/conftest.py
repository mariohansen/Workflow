from __future__ import annotations

import os
from collections.abc import AsyncIterator

os.environ.setdefault(
    "WFS_DATABASE_URL",
    "postgresql+asyncpg://workflow_studio:workflow_studio@localhost:5432/workflow_studio_test",
)

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.models import Base
from app.db.session import get_session
from app.main import create_app
from app.settings import get_settings


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Fresh engine per test: asyncpg connections are bound to the event loop
    they were created on, and pytest-asyncio gives each test its own loop."""
    engine = create_async_engine(get_settings().database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        transaction = await conn.begin()
        db_session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        yield db_session
        await db_session.close()
        await transaction.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
