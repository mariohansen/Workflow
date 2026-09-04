from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.contexts import ContextItemKind
from app.domain.ids import new_id

_VERIFIED_FACT_NEEDS_SOURCE = """
    (kind = 'file' AND document_id IS NOT NULL
        AND statement IS NULL AND source_item_id IS NULL AND evidence_quote IS NULL) OR
    (kind = 'verified_fact' AND document_id IS NULL
        AND statement IS NOT NULL AND source_item_id IS NOT NULL AND evidence_quote IS NOT NULL)
"""


class Context(CreatedAtMixin, Base):
    __tablename__ = "contexts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str]


class ContextItem(CreatedAtMixin, Base):
    """A FILE references a Document. A VERIFIED_FACT is a claim that must carry
    its source - a fact without evidence is invalid at the database level."""

    __tablename__ = "context_items"
    __table_args__ = (CheckConstraint(_VERIFIED_FACT_NEEDS_SOURCE, name="fact_needs_source"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    context_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contexts.id"), index=True)
    kind: Mapped[ContextItemKind]

    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"))
    statement: Mapped[str | None] = mapped_column(Text)
    source_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("context_items.id"))
    evidence_quote: Mapped[str | None] = mapped_column(Text)
