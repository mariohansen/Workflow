from __future__ import annotations

import enum


class ArtifactKind(enum.StrEnum):
    TEXT = "text"
    DOCUMENT = "document"
    JSON = "json"
