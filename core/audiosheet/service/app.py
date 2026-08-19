"""FastAPI application factory — ARCHITECTURE.md Sections 4.1 and 5.2.

The service binds 127.0.0.1 on an ephemeral port and requires a bearer token.
INV-1: it makes no outbound connections of any kind.
"""

from __future__ import annotations

from fastapi import FastAPI

from audiosheet.version import APP_VERSION


def create_app() -> FastAPI:
    """Build the FastAPI application with auth, routes and error mapping.

    Returns:
        The configured application.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("service application lands in Phase 1")


def describe() -> dict[str, str]:
    """Return the static part of the ``/health`` payload.

    Returns:
        Version information available without touching the model files.
    """
    return {"app_version": APP_VERSION}
