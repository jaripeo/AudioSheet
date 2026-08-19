"""S1.3 meter estimation — ARCHITECTURE.md Section 1.4.

The argmax candidate must beat the runner-up by ``METER_MARGIN``; otherwise the
meter defaults to 4/4 with a low confidence so the UI can offer an override.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from audiosheet.analysis.beats import BeatTrack
from audiosheet.ingest.decode import AudioBundle

#: Candidate meters, as (numerator, denominator) pairs.
METER_CANDIDATES: Final[tuple[tuple[int, int], ...]] = (
    (4, 4),
    (3, 4),
    (2, 4),
    (6, 8),
    (12, 8),
    (5, 4),
    (7, 8),
)

#: Minimum score margin over the runner-up before a non-default meter is chosen.
METER_MARGIN: Final[float] = 0.10

#: Fallback meter when the margin is not met.
DEFAULT_METER: Final[tuple[int, int]] = (4, 4)


@dataclass(frozen=True)
class MeterEstimate:
    """The S1.3 output."""

    numerator: int
    denominator: int
    confidence: float
    margin: float


def estimate_meter(bundle: AudioBundle, track: BeatTrack) -> MeterEstimate:
    """Estimate the time signature from downbeat likelihood and accent periodicity.

    Args:
        bundle: The S0 output.
        track: The S1.1 beat track.

    Returns:
        The meter estimate.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.3 meter estimation lands in Phase 3")
