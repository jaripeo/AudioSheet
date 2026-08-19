"""Ingestion limits — ARCHITECTURE.md Section 1.3, step 2 (Normative)."""

from __future__ import annotations

from typing import Final

#: Largest accepted upload.
MAX_FILE_SIZE_BYTES: Final[int] = 120 * 1024 * 1024

#: Longest accepted audio.
MAX_DURATION_S: Final[float] = 600.0

#: Shortest accepted audio.
MIN_DURATION_S: Final[float] = 1.0

#: Channel count above which the input is downmixed with equal weights.
MAX_CHANNELS: Final[int] = 2

#: Per-stage resident memory ceiling (Section 4.3).
MAX_STAGE_MEMORY_BYTES: Final[int] = 4 * 1024 * 1024 * 1024
