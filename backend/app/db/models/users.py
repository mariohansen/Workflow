from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.ids import new_id


class User(CreatedAtMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
