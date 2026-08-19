"""Timing-grid construction and the canonical tick <-> seconds conversion.

INV-5: every temporal value exists in both seconds and ticks, and conversion
goes through the tempo map only — never by multiplying a single global BPM.
The two conversion functions here are that single bridge; nothing else in the
codebase may convert between the two domains.

Grid *lattice* construction (S5.1) arrives in Phase 6; the conversions are
implemented now because validator V-6 depends on them.
"""

from __future__ import annotations

from audiosheet.config.constants import PPQ
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode
from audiosheet.schema import DifficultyProfile, TempoEvent, TimingGrid

#: Seconds per minute, named so the conversion formulae read as the spec does.
_SECONDS_PER_MINUTE = 60.0


def quarters_to_seconds(quarters: float, bpm: float) -> float:
    """Convert a duration in quarter notes to seconds at ``bpm``.

    Args:
        quarters: Duration in quarter notes.
        bpm: Quarter notes per minute.

    Returns:
        The duration in seconds.
    """
    return quarters * (_SECONDS_PER_MINUTE / bpm)


def measure_capacity_ticks(numerator: int, denominator: int) -> int:
    """Return how many ticks one measure of ``numerator/denominator`` holds.

    Args:
        numerator: Beats per measure.
        denominator: Beat unit as a power of two (4 = quarter, 8 = eighth).

    Returns:
        The measure capacity in ticks.

    Raises:
        AudioSheetError: ``E_INVARIANT_VIOLATED`` on a non-positive meter.
    """
    if numerator <= 0 or denominator <= 0:
        raise AudioSheetError(
            ErrorCode.E_INVARIANT_VIOLATED,
            f"invalid time signature {numerator}/{denominator}",
        )
    return numerator * (PPQ * 4) // denominator


def _tempo_anchor(grid: TimingGrid, tick: int) -> TempoEvent:
    """Return the tempo event governing ``tick``."""
    anchor = grid.tempo_map[0]
    for event in grid.tempo_map:
        if event.tick <= tick:
            anchor = event
        else:
            break
    return anchor


def _anchor_for_seconds(grid: TimingGrid, seconds: float) -> TempoEvent:
    """Return the tempo event governing ``seconds``."""
    anchor = grid.tempo_map[0]
    for event in grid.tempo_map:
        if event.time_s <= seconds:
            anchor = event
        else:
            break
    return anchor


def tick_to_seconds(grid: TimingGrid, tick: int) -> float:
    """Convert a tick position to absolute seconds through the tempo map.

    Args:
        grid: The timing grid; ``tempo_map`` must be sorted and start at tick 0.
        tick: The tick position.

    Returns:
        Absolute seconds from the start of the decoded, untrimmed audio.
    """
    anchor = _tempo_anchor(grid, tick)
    quarters = (tick - anchor.tick) / grid.ppq
    return anchor.time_s + quarters_to_seconds(quarters, anchor.bpm)


def seconds_to_tick(grid: TimingGrid, seconds: float) -> int:
    """Convert absolute seconds to the nearest tick through the tempo map.

    Args:
        grid: The timing grid.
        seconds: Absolute seconds.

    Returns:
        The nearest integral tick.
    """
    anchor = _anchor_for_seconds(grid, seconds)
    elapsed = seconds - anchor.time_s
    quarters = elapsed * anchor.bpm / _SECONDS_PER_MINUTE
    return anchor.tick + round(quarters * grid.ppq)


def build_grid(grid: TimingGrid, profile: DifficultyProfile) -> list[int]:
    """Return the legal onset lattice in ticks for ``profile`` (S5.1).

    Args:
        grid: The timing grid.
        profile: The difficulty profile supplying ``grid_divisions`` and
            ``allow_tuplets``.

    Returns:
        Sorted, de-duplicated legal onset positions in ticks.

    Raises:
        NotImplementedError: Phase 6 (ARCHITECTURE.md Section 5.3).
    """
    raise NotImplementedError("S5.1 grid construction lands in Phase 6")
