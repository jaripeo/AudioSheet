"""S5.2 rhythmic quantisation — ARCHITECTURE.md Section 2.1.3.

A dynamic program over grid positions, not nearest-neighbour snapping: naive
snapping produces zero-length notes, chord de-synchronisation and impossible
tuplet soups.

This module and ``packages/engine/src/quantize.ts`` implement the same DP for
different runtimes (S5 next to the models, S7 next to the slider). They MUST
agree on every vector in ``core/tests/golden/quantize/`` — that shared suite is
what stops the two implementations drifting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from audiosheet.schema import DifficultyProfile, Note, TimingGrid

#: Search half-width around a raw onset, in beats. Bounds the DP to O(N*M*W).
SEARCH_WINDOW_BEATS: Final[float] = 1.0


@dataclass(frozen=True)
class QuantizeResult:
    """The outcome of quantising one voice.

    Attributes:
        notes: The quantised notes.
        mean_shift_ticks: Mean absolute snap applied, for diagnostics.
        dropped_ids: Notes dropped for falling below the minimum duration.
    """

    notes: list[Note]
    mean_shift_ticks: float
    dropped_ids: list[str]


def quantize(
    notes: list[Note],
    grid: TimingGrid,
    profile: DifficultyProfile,
) -> QuantizeResult:
    """Snap onsets then durations to the profile's grid via the Section 2.1.3 DP.

    Ties break toward the earlier grid position, which keeps the result
    deterministic (INV-2).

    Args:
        notes: Notes of a single voice, in onset order.
        grid: The timing grid.
        profile: Difficulty profile supplying the grid and the cost weights.

    Returns:
        The quantised notes plus diagnostics.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.2 quantisation lands in Phase 6")


def syncopation_penalty(tick: int, grid: TimingGrid) -> float:
    """Return the off-beat penalty for a grid position, scaled by metric depth.

    Args:
        tick: Candidate grid position.
        grid: The timing grid.

    Returns:
        A non-negative penalty; 0 on a downbeat.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("syncopation scoring lands in Phase 6")
