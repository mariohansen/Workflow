from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.artifacts import Artifact


class ArtifactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, artifact: Artifact) -> None:
        self._session.add(artifact)
