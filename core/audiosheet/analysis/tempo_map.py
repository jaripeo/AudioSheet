"""S1.2 tempo map construction — ARCHITECTURE.md Section 1.4.

A new tempo event is emitted only when a segment's mean differs from its
predecessor by more than ``TEMPO_CHANGE_THRESHOLD`` AND the segment spans at
least ``MIN_TEMPO_SEGMENT_BARS`` bars. Without both conditions the score acquires
one tempo marking per bar and becomes unreadable.
"""

from __future__ import annotations

from typing import Final

from audiosheet.analysis.beats import BeatTrack
from audiosheet.schema import TimingGrid

#: Median filter width, in beats, applied to instantaneous BPM.
BPM_MEDIAN_FILTER_BEATS: Final[int] = 5

#: Relative change below which a new tempo segment is not worth notating.
TEMPO_CHANGE_THRESHOLD: Final[float] = 0.02

#: Shortest tempo segment that earns its own tempo event, in bars.
MIN_TEMPO_SEGMENT_BARS: Final[int] = 2

#: Below this median BPM the tracker is suspected of halving the tempo.
TEMPO_OCTAVE_LOW_BPM: Final[float] = 60.0

#: Above this median BPM the tracker is suspected of doubling the tempo.
TEMPO_OCTAVE_HIGH_BPM: Final[float] = 190.0


def build_tempo_map(track: BeatTrack, numerator: int, denominator: int) -> TimingGrid:
    """Turn a beat track into a piecewise-constant timing grid.

    Tick 0 is anchored to the first downbeat, not to ``t = 0``; audio before it
    becomes an implicit pickup measure.

    Args:
        track: The S1.1 beat track.
        numerator: Meter numerator from S1.3.
        denominator: Meter denominator from S1.3.

    Returns:
        The populated timing grid.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.2 tempo map construction lands in Phase 3")


def correct_tempo_octave(track: BeatTrack) -> tuple[BeatTrack, bool]:
    """Halve or double an octave-confused tempo estimate.

    Args:
        track: The S1.1 beat track.

    Returns:
        The corrected track and whether a correction was applied.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("tempo octave correction lands in Phase 3")
