from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.ids import new_id


class Prompt(CreatedAtMixin, Base):
    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(unique=True)


class PromptVersion(CreatedAtMixin, Base):
    """Append-only: a new template is a new row, never an update to an existing one."""

    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("prompt_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompts.id"), index=True)
    version: Mapped[int]
    template: Mapped[str] = mapped_column(Text)
