from __future__ import annotations

import os
import time
import uuid


def new_id() -> uuid.UUID:
    """UUIDv7 (RFC 9562): sortable by creation time, generated in the app."""
    unix_ts_ms = time.time_ns() // 1_000_000
    rand = bytearray(os.urandom(10))
    rand[0] = (rand[0] & 0x0F) | 0x70  # version 7
    rand[2] = (rand[2] & 0x3F) | 0x80  # variant 10
    return uuid.UUID(bytes=unix_ts_ms.to_bytes(6, "big") + bytes(rand))
