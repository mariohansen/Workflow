from __future__ import annotations

import uuid

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.ids import new_id


class Document(CreatedAtMixin, Base):
    """A deduplicated, content-addressed file. Referenced by DOCUMENT artifacts
    and by FILE context items; the blob itself lives in the ArtifactStore."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    filename: Mapped[str]
    mime_type: Mapped[str]
    storage_ref: Mapped[str]
    sha256: Mapped[str] = mapped_column(unique=True, index=True)
    page_count: Mapped[int | None]
    extracted_text: Mapped[str | None] = mapped_column(Text)
    doc_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSONB, default=dict)
