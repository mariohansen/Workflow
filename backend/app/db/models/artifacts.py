from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.artifacts import ArtifactKind
from app.domain.ids import new_id

_EXACTLY_ONE_PAYLOAD = """
    (kind = 'text' AND text IS NOT NULL AND document_id IS NULL AND json_data IS NULL) OR
    (kind = 'document' AND document_id IS NOT NULL AND text IS NULL AND json_data IS NULL) OR
    (kind = 'json' AND json_data IS NOT NULL AND text IS NULL AND document_id IS NULL)
"""


class Artifact(CreatedAtMixin, Base):
    """Immutable typed output of a step. Exactly one payload column is set,
    matching `kind` - enforced in the database, not just in application code."""

    __tablename__ = "artifacts"
    __table_args__ = (CheckConstraint(_EXACTLY_ONE_PAYLOAD, name="payload_matches_kind"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    kind: Mapped[ArtifactKind]
    produced_by_step_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("step_runs.id"), index=True
    )

    text: Mapped[str | None] = mapped_column(Text)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"))
    json_schema_id: Mapped[str | None]
    json_data: Mapped[dict[str, object] | None] = mapped_column(JSONB)
