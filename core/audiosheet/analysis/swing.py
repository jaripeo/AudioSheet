"""S1.4 swing detection — ARCHITECTURE.md Section 1.4.

Swung eighths are notated as plain eighths plus a swing directive rather than as
unreadable triplet chains; the quantiser consumes this (Section 2.1.3).
"""

from __future__ import annotations

from typing import Final

from audiosheet.analysis.beats import BeatTrack
from audiosheet.ingest.decode import AudioBundle
from audiosheet.schema import SwingSpec

#: Off-beat phase window, within a beat, that counts as swung.
SWING_PHASE_RANGE: Final[tuple[float, float]] = (0.58, 0.72)

#: Minimum share of onset mass inside the window before swing is declared.
SWING_MASS_THRESHOLD: Final[float] = 0.15


def detect_swing(bundle: AudioBundle, track: BeatTrack) -> SwingSpec:
    """Detect swing from the histogram of off-beat onset phases.

    Args:
        bundle: The S0 output.
        track: The S1.1 beat track.

    Returns:
        The swing specification for the timing grid.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.4 swing detection lands in Phase 3")
