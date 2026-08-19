"""HTTP routes — ARCHITECTURE.md Section 5.2.

All non-2xx bodies are ``{code: "E_*", message, detail}``.
"""

from __future__ import annotations

from fastapi import APIRouter

from audiosheet.service.jobs import JobRegistry


def build_router(registry: JobRegistry) -> APIRouter:
    """Build the API router.

    Routes:
        ``POST /jobs``               accept an upload, return ``{job_id}``
        ``GET  /jobs/{id}/events``  server-sent per-stage progress
        ``GET  /jobs/{id}/document`` the finished ScoreDocument at Complex
        ``POST /jobs/{id}/cancel``  request cancellation
        ``POST /export/musicxml``   MusicXML for a posted document
        ``POST /export/midi``       MIDI for a posted document
        ``GET  /health``            version and model integrity

    Args:
        registry: The job registry the routes operate on.

    Returns:
        The configured router.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("service routes land in Phase 1")
