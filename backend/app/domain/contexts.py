from __future__ import annotations

import enum


class ContextItemKind(enum.StrEnum):
    FILE = "file"
    VERIFIED_FACT = "verified_fact"
