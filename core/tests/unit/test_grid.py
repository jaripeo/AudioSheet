"""The canonical tick <-> seconds bridge and measure capacity (INV-5)."""

from __future__ import annotations

import pytest

from audiosheet.pipeline.errors import AudioSheetError
from audiosheet.schema import ScoreDocument, TempoEvent
from audiosheet.symbolic.grid import (
    build_grid,
    measure_capacity_ticks,
    quarters_to_seconds,
    seconds_to_tick,
    tick_to_seconds,
)


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    [
        (4, 4, 3840),
        (3, 4, 2880),
        (2, 4, 1920),
        (6, 8, 2880),
        (12, 8, 5760),
        (5, 4, 4800),
        (7, 8, 3360),
    ],
)
def test_measure_capacity(numerator: int, denominator: int, expected: int) -> None:
    assert measure_capacity_ticks(numerator, denominator) == expected


def test_measure_capacity_rejects_a_nonsense_meter() -> None:
    with pytest.raises(AudioSheetError):
        measure_capacity_ticks(0, 4)


def test_quarters_to_seconds_at_120_bpm() -> None:
    assert quarters_to_seconds(1.0, 120.0) == pytest.approx(0.5)


def test_tick_to_seconds_on_the_fixture(simple_scale: ScoreDocument) -> None:
    grid = simple_scale.timing
    assert tick_to_seconds(grid, 0) == pytest.approx(0.0)
    assert tick_to_seconds(grid, 960) == pytest.approx(0.5)
    assert tick_to_seconds(grid, 7680) == pytest.approx(4.0)


def test_seconds_to_tick_is_the_inverse(simple_scale: ScoreDocument) -> None:
    grid = simple_scale.timing
    for tick in (0, 240, 960, 3840, 7680):
        assert seconds_to_tick(grid, tick_to_seconds(grid, tick)) == tick


def test_conversion_follows_a_tempo_change(simple_scale: ScoreDocument) -> None:
    """A tempo change must be honoured, not averaged into a single global BPM."""
    grid = simple_scale.timing.model_copy(
        update={
            "tempo_map": [
                TempoEvent(tick=0, time_s=0.0, bpm=120.0, confidence=1.0),
                TempoEvent(tick=3840, time_s=2.0, bpm=60.0, confidence=1.0),
            ]
        }
    )
    # After the change a quarter note lasts a full second, not half of one.
    assert tick_to_seconds(grid, 4800) == pytest.approx(3.0)
    assert seconds_to_tick(grid, 3.0) == 4800


def test_ticks_before_the_first_event_use_the_first_anchor(simple_scale: ScoreDocument) -> None:
    grid = simple_scale.timing
    assert tick_to_seconds(grid, -960) == pytest.approx(-0.5)


def test_grid_construction_is_deferred_to_phase_six(simple_scale: ScoreDocument) -> None:
    with pytest.raises(NotImplementedError):
        build_grid(simple_scale.timing, simple_scale.difficulty)
