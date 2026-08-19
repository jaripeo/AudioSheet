"""S3.2 f0 track to note events — ARCHITECTURE.md Section 1.6.2, steps 2-5.

Pitch is the median cents over the segment's central 60 %, which excludes attack
scoops and release falls; the residual is retained in ``micro_cents`` so bends
and vibrato survive to the Complex renderer.
"""

from __future__ import annotations

from typing import Final

from audiosheet.schema import RawNote
from audiosheet.transcription.crepe import F0Track

#: Confidence gap that ends a segment, in seconds.
SEGMENT_GAP_S: Final[float] = 0.040

#: Pitch jump that ends a segment, in cents.
SEGMENT_JUMP_CENTS: Final[float] = 80.0

#: Frames the jump must persist for before it splits a segment.
SEGMENT_JUMP_FRAMES: Final[int] = 3

#: Segments shorter than this are discarded, in seconds.
MIN_SEGMENT_S: Final[float] = 0.060

#: Central fraction of a segment used to take the median pitch.
MEDIAN_CORE_FRACTION: Final[float] = 0.60


def segment(track: F0Track, stem_name: str) -> list[RawNote]:
    """Convert a smoothed f0 track into note events.

    Args:
        track: The S3.2 f0 track.
        stem_name: Stem name, recorded on each ``RawNote``.

    Returns:
        The decoded note events.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S3.2 segmentation lands in Phase 5")


def detect_vibrato(track: F0Track, start_frame: int, end_frame: int) -> bool:
    """Report whether a segment carries audible vibrato.

    Args:
        track: The f0 track.
        start_frame: Inclusive segment start.
        end_frame: Exclusive segment end.

    Returns:
        True when a 4-8 Hz component exceeds ``VIBRATO_CENTS_THRESHOLD``.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("vibrato detection lands in Phase 5")
