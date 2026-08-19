#!/usr/bin/env python3
"""Verify vendored model files against models/manifest.json.

ARCHITECTURE.md Section 4.2: on startup the app verifies every sha256 and a
mismatch is a hard failure (``E_MODEL_INTEGRITY``). INV-1 forbids fetching a
missing model, so this script never downloads anything.

Modes:
    (default)  verify every entry whose status is "vendored"; pending entries are
               reported and skipped. This is the developer-loop check.
    --strict   additionally fail on any pending entry. This is a release gate:
               nothing ships with an unpinned model digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
MANIFEST: Final[Path] = REPO_ROOT / "models" / "manifest.json"

#: Read size when digesting large model files.
CHUNK_BYTES: Final[int] = 1 << 20


def sha256_of(path: Path) -> str:
    """Return the hex SHA-256 digest of a file, read in chunks.

    Args:
        path: File to digest.

    Returns:
        The lowercase hex digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when ``None``.

    Returns:
        0 when every checked entry is intact, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on entries that are not yet vendored and pinned",
    )
    args = parser.parse_args(argv)

    if not MANIFEST.is_file():
        print(f"E_MODEL_MISSING: no manifest at {MANIFEST}", file=sys.stderr)
        return 1

    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))["models"]
    failures: list[str] = []
    pending: list[str] = []
    verified = 0

    for entry in entries:
        name = entry["name"]
        path = MANIFEST.parent / entry["filename"]

        if entry["status"] != "vendored":
            pending.append(f"{name} (phase {entry['phase']})")
            continue
        if not path.is_file():
            failures.append(f"E_MODEL_MISSING: {name} -> {path}")
            continue
        if not entry["sha256"]:
            failures.append(
                f"E_MODEL_INTEGRITY: {name} is vendored but has no pinned digest"
            )
            continue
        actual = sha256_of(path)
        if actual != entry["sha256"]:
            failures.append(
                f"E_MODEL_INTEGRITY: {name} digest mismatch\n"
                f"  expected {entry['sha256']}\n  actual   {actual}"
            )
            continue
        verified += 1

    for failure in failures:
        print(failure, file=sys.stderr)
    if pending:
        print(f"pending (not yet vendored): {', '.join(pending)}")
    print(f"verified {verified}/{len(entries)} model(s)")

    if failures:
        return 1
    if args.strict and pending:
        print(
            "--strict: every model must be vendored and pinned before release",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
