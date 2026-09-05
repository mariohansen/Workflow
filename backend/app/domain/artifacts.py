from __future__ import annotations

import enum
from dataclasses import dataclass


class ArtifactKind(enum.StrEnum):
    TEXT = "text"
    DOCUMENT = "document"
    JSON = "json"


@dataclass(frozen=True)
class TextArtifact:
    text: str


Artifact = TextArtifact
