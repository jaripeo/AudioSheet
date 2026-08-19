"""The pure helpers S3 already needs: velocity, confidence, per-stem parameters."""

from __future__ import annotations

import pytest

from audiosheet.transcription.basic_pitch_params import (
    DEFAULT_PARAMS,
    NOTE_RANGE_MIDI,
    STEM_PARAMS,
    params_for,
)
from audiosheet.transcription.crepe import (
    CONFIDENCE_FLOOR,
    CONFIDENCE_FLOOR_BASS,
    confidence_floor_for,
)
from audiosheet.transcription.postprocess import (
    CONFIDENCE_WEIGHTS,
    VELOCITY_FLOOR_DB,
    estimate_velocity,
    score_confidence,
)


def test_default_params_match_the_architecture_table() -> None:
    assert DEFAULT_PARAMS.onset_threshold == 0.50
    assert DEFAULT_PARAMS.frame_threshold == 0.30
    assert DEFAULT_PARAMS.min_note_len_ms == pytest.approx(127.70)
    assert DEFAULT_PARAMS.melodia_trick is True
    assert DEFAULT_PARAMS.multiple_pitch_bends is False


def test_guitar_params_admit_drop_d() -> None:
    """min_freq is D2 (73.4 Hz), not E2, so drop-D tunings transcribe."""
    guitar = STEM_PARAMS["guitar"]
    assert guitar.min_freq_hz == pytest.approx(73.4)
    assert guitar.max_freq_hz == pytest.approx(1318.5)


def test_params_for_falls_back_to_the_default() -> None:
    assert params_for("vocals") is DEFAULT_PARAMS
    assert params_for("piano") is STEM_PARAMS["piano"]


def test_note_range_spans_88_keys() -> None:
    low, high = NOTE_RANGE_MIDI
    assert (low, high) == (21, 108)
    assert high - low + 1 == 88


def test_bass_gets_a_relaxed_confidence_floor() -> None:
    assert confidence_floor_for("bass") == CONFIDENCE_FLOOR_BASS
    assert confidence_floor_for("vocals") == CONFIDENCE_FLOOR
    assert CONFIDENCE_FLOOR_BASS < CONFIDENCE_FLOOR


@pytest.mark.parametrize(
    ("rms_db", "expected"),
    [(0.0, 127), (-30.0, 64), (-60.0, 1), (-120.0, 1)],
)
def test_velocity_mapping(rms_db: float, expected: int) -> None:
    assert estimate_velocity(rms_db) == expected


def test_velocity_stays_in_the_midi_range() -> None:
    for rms_db in range(-120, 21):
        assert 1 <= estimate_velocity(float(rms_db)) <= 127


def test_velocity_floors_at_the_documented_level() -> None:
    assert estimate_velocity(VELOCITY_FLOOR_DB) == estimate_velocity(-999.0)


def test_confidence_weights_sum_to_one() -> None:
    assert sum(CONFIDENCE_WEIGHTS) == pytest.approx(1.0)


def test_confidence_blend_is_bounded_and_monotone() -> None:
    assert score_confidence(0.0, 0.0, 0.0) == pytest.approx(0.0)
    assert score_confidence(1.0, 1.0, 1000.0) == pytest.approx(1.0)
    assert score_confidence(0.9, 0.9, 300.0) > score_confidence(0.4, 0.4, 300.0)


def test_short_notes_are_penalised_by_the_duration_prior() -> None:
    assert score_confidence(1.0, 1.0, 25.0) < score_confidence(1.0, 1.0, 250.0)
