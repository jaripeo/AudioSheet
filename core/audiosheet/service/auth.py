"""Loopback bearer-token auth — ARCHITECTURE.md Section 5.2.

The service binds 127.0.0.1 only and requires a bearer token that the desktop
shell reads from a file the sidecar writes. This stops any other local process
driving the pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

#: Name of the token file inside the runtime directory.
TOKEN_FILENAME: Final[str] = "service-token"

#: Token length in bytes before hex encoding.
TOKEN_BYTES: Final[int] = 32

#: The only interface the service is permitted to bind.
BIND_HOST: Final[str] = "127.0.0.1"


def generate_token() -> str:
    """Return a fresh, cryptographically random bearer token.

    Returns:
        A hex-encoded token.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("service auth lands in Phase 1")


def write_token(runtime_dir: Path, token: str) -> Path:
    """Write the token with owner-only permissions.

    Args:
        runtime_dir: Directory the shell reads the token from.
        token: The token to persist.

    Returns:
        The path written.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("service auth lands in Phase 1")


def verify_token(presented: str, expected: str) -> bool:
    """Compare tokens in constant time.

    Args:
        presented: Token from the ``Authorization`` header.
        expected: The token this process issued.

    Returns:
        Whether the tokens match.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("service auth lands in Phase 1")
