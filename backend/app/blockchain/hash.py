from __future__ import annotations

import hashlib
import re

from app.blockchain.canonical import canonical_json


SHA256_HEX_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_payload(payload: dict) -> str:
    return sha256_hex(canonical_json(payload))


def is_sha256_hex(value: str | None) -> bool:
    return bool(value and SHA256_HEX_PATTERN.fullmatch(value))
