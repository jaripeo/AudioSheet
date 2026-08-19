"""Content-addressed stage cache — ARCHITECTURE.md Section 1.2.

A stage is skippable when its fingerprint hits the cache. Everything written
here is canonical JSON so that two runs of the same input produce byte-identical
cache contents (INV-2).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from blake3 import blake3

from audiosheet.pipeline.errors import AudioSheetError, ErrorCode

#: Prefix marking a fingerprint as BLAKE3, so the algorithm is never ambiguous.
FINGERPRINT_PREFIX: Final[str] = "b3:"

#: Number of hex characters retained from a BLAKE3 digest.
FINGERPRINT_HEX_LENGTH: Final[int] = 32


def canonical_json(value: Any) -> str:
    """Serialise ``value`` to the one canonical JSON form used everywhere.

    Sorted keys, no insignificant whitespace, non-ASCII preserved, and a single
    trailing newline. This is the only serialiser permitted for anything that is
    hashed, cached, or compared byte-for-byte (INV-2).

    Args:
        value: Any JSON-serialisable value.

    Returns:
        The canonical JSON text, newline-terminated.
    """
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def blake3_hex(*parts: bytes) -> str:
    """Return a prefixed BLAKE3 digest over ``parts``.

    Each part is length-prefixed so that ``(b"ab", b"c")`` and ``(b"a", b"bc")``
    hash differently.

    Args:
        *parts: Byte strings to hash in order.

    Returns:
        A fingerprint of the form ``b3:<hex>``.
    """
    hasher = blake3()
    for part in parts:
        hasher.update(len(part).to_bytes(8, "big"))
        hasher.update(part)
    return FINGERPRINT_PREFIX + hasher.hexdigest()[:FINGERPRINT_HEX_LENGTH]


def hash_json(value: Any) -> str:
    """Return the fingerprint of a JSON-serialisable value.

    Args:
        value: Any JSON-serialisable value.

    Returns:
        A fingerprint of the form ``b3:<hex>``.
    """
    return blake3_hex(canonical_json(value).encode("utf-8"))


class StageCache:
    """A per-project, content-addressed cache keyed by stage fingerprint.

    Layout::

        <root>/<stage-name>/<fingerprint>.json    structured stage output
        <root>/<stage-name>/<fingerprint>.<ext>   opaque blobs (PCM, FLAC, ...)
    """

    def __init__(self, root: Path) -> None:
        """Create a cache rooted at ``root``, creating the directory if absent."""
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, stage: str) -> Path:
        path = self.root / stage
        path.mkdir(parents=True, exist_ok=True)
        return path

    def json_path(self, stage: str, fingerprint: str) -> Path:
        """Return the path of the JSON entry for ``stage``/``fingerprint``."""
        return self._dir(stage) / f"{self._safe(fingerprint)}.json"

    def blob_path(self, stage: str, fingerprint: str, extension: str) -> Path:
        """Return the path of an opaque blob for ``stage``/``fingerprint``."""
        suffix = extension if extension.startswith(".") else f".{extension}"
        return self._dir(stage) / f"{self._safe(fingerprint)}{suffix}"

    def has(self, stage: str, fingerprint: str) -> bool:
        """Return whether a JSON entry exists for ``stage``/``fingerprint``."""
        return self.json_path(stage, fingerprint).is_file()

    def get(self, stage: str, fingerprint: str) -> Any | None:
        """Read a cached JSON entry, or return ``None`` on a miss.

        Raises:
            AudioSheetError: ``E_CACHE_CORRUPT`` when the entry is unparseable.
        """
        path = self.json_path(stage, fingerprint)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AudioSheetError(
                ErrorCode.E_CACHE_CORRUPT,
                f"cache entry is not valid JSON: {path}",
                detail={"path": str(path)},
            ) from exc

    def put(self, stage: str, fingerprint: str, value: Any) -> Path:
        """Write a JSON entry atomically and return its path."""
        path = self.json_path(stage, fingerprint)
        temp = path.with_suffix(".json.tmp")
        temp.write_text(canonical_json(value), encoding="utf-8")
        temp.replace(path)
        return path

    def clear(self, stage: str | None = None) -> int:
        """Delete cached entries and return how many files were removed.

        Args:
            stage: Clear only this stage, or every stage when ``None``.
        """
        target = self._dir(stage) if stage is not None else self.root
        removed = 0
        for path in sorted(target.rglob("*")):
            if path.is_file():
                path.unlink()
                removed += 1
        return removed

    @staticmethod
    def _safe(fingerprint: str) -> str:
        """Return a filename-safe form of a fingerprint."""
        return fingerprint.replace(":", "_").replace("/", "_")
