from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {  # noqa: RUF012 - SQLAlchemy reads this as a class attribute
        datetime: DateTime(timezone=True),
        uuid.UUID: Uuid(as_uuid=True),
    }


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


def pg_enum(enum_cls: type[enum.Enum]) -> Enum:
    """Postgres enum storing member *values* (e.g. "text"), not member names
    (e.g. "TEXT") - SQLAlchemy defaults to names, which then can't satisfy
    CHECK constraints written against the domain enum's own string values."""
    return Enum(enum_cls, values_callable=lambda cls: [member.value for member in cls])
