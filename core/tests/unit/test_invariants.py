"""V-1..V-7: every invariant has a passing and a deliberately-failing case.

Each failure mutates the hand-authored fixture in a way that still satisfies the
JSON Schema, so the test proves the invariant — not the schema — is what catches
it. Mutations are chosen so that only the invariant under test is violated.
"""

from __future__ import annotations

from typing import Any

import pytest

from audiosheet.pipeline.errors import ErrorCode, InvariantViolationError
from audiosheet.schema import ScoreDocument
from audiosheet.validate.invariants import (
    INVARIANTS,
    check_invariants,
    check_v1_durations,
    check_v2_no_voice_overlap,
    check_v3_measures,
    check_v4_measure_capacity,
    check_v5_origin_ids,
    check_v6_time_roundtrip,
    check_v7_tab_pitches,
)


def test_all_invariants_pass_on_the_handmade_fixture(
    simple_scale: ScoreDocument, raw_ids: set[str]
) -> None:
    """The hand-authored fixture satisfies every invariant, strict V-5 included."""
    check_invariants(simple_scale, known_raw_ids=raw_ids)


def test_registry_lists_seven_invariants() -> None:
    """The module enforces exactly V-1..V-7."""
    assert INVARIANTS == ("V-1", "V-2", "V-3", "V-4", "V-5", "V-6", "V-7")


def _expect(invariant: str, document: ScoreDocument, check: Any) -> None:
    with pytest.raises(InvariantViolationError) as excinfo:
        check(document)
    assert excinfo.value.invariant == invariant
    assert excinfo.value.code is ErrorCode.E_INVARIANT_VIOLATED


# --- V-1 -------------------------------------------------------------------


def test_v1_passes(simple_scale: ScoreDocument) -> None:
    check_v1_durations(simple_scale)


def test_v1_fails_on_zero_length_note(mutate_payload: Any) -> None:
    """A note whose offset equals its onset is schema-valid but musically void."""

    def mutate(payload: dict[str, Any]) -> None:
        note = payload["parts"][0]["notes"][0]
        note["tick_off"] = note["tick_on"]
        note["time_off_s"] = note["time_on_s"]

    _expect("V-1", mutate_payload(mutate), check_v1_durations)


# --- V-2 -------------------------------------------------------------------


def test_v2_passes(simple_scale: ScoreDocument) -> None:
    check_v2_no_voice_overlap(simple_scale)


def test_v2_fails_on_overlapping_notes_in_one_voice(mutate_payload: Any) -> None:
    """Two sounding notes in one voice may not overlap unless flagged as a chord."""

    def mutate(payload: dict[str, Any]) -> None:
        notes = payload["parts"][0]["notes"]
        intruder = dict(notes[0])
        intruder["id"] = "n-9001"
        intruder["origin_ids"] = ["raw-0001"]
        intruder["tick_on"] = 480
        intruder["tick_off"] = 1440
        intruder["time_on_s"] = 0.25
        intruder["time_off_s"] = 0.75
        notes.append(intruder)

    _expect("V-2", mutate_payload(mutate), check_v2_no_voice_overlap)


def test_v2_allows_chord_members_sharing_an_onset(mutate_payload: Any) -> None:
    """Notes sharing an onset are legal when marked as MusicXML chord members."""

    def mutate(payload: dict[str, Any]) -> None:
        notes = payload["parts"][0]["notes"]
        member = dict(notes[0])
        member["id"] = "n-9002"
        member["origin_ids"] = ["raw-0001"]
        member["is_chord_member"] = True
        member["midi"] = 64
        member["step"] = "E"
        member["tab"] = {
            "string": 1,
            "fret": 0,
            "finger": None,
            "is_barre_root": False,
            "position": 0,
        }
        notes.append(member)

    check_v2_no_voice_overlap(mutate_payload(mutate))


# --- V-3 -------------------------------------------------------------------


def test_v3_passes(simple_scale: ScoreDocument) -> None:
    check_v3_measures(simple_scale)


def test_v3_fails_when_measures_do_not_start_at_tick_zero(mutate_payload: Any) -> None:
    """Measure spans must be contiguous and gapless from tick 0."""

    def mutate(payload: dict[str, Any]) -> None:
        for measure in payload["timing"]["measures"]:
            measure["tick_start"] += 960
            measure["tick_end"] += 960

    _expect("V-3", mutate_payload(mutate), check_v3_measures)


def test_v3_fails_on_a_gap_between_measures(mutate_payload: Any) -> None:
    """A gap between two measures is a layout bug, not a rest."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["timing"]["measures"][1]["tick_start"] += 960

    _expect("V-3", mutate_payload(mutate), check_v3_measures)


# --- V-4 -------------------------------------------------------------------


def test_v4_passes(simple_scale: ScoreDocument) -> None:
    check_v4_measure_capacity(simple_scale)


def test_v4_fails_when_a_measure_contradicts_its_meter(mutate_payload: Any) -> None:
    """A 3/4 signature cannot govern a measure that spans four quarter notes."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["timing"]["time_signatures"][0]["numerator"] = 3

    _expect("V-4", mutate_payload(mutate), check_v4_measure_capacity)


def test_v4_fails_on_a_dangling_time_signature_reference(mutate_payload: Any) -> None:
    """A measure may not reference a time signature that does not exist."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["timing"]["measures"][0]["time_signature_ref"] = 7

    _expect("V-4", mutate_payload(mutate), check_v4_measure_capacity)


# --- V-5 -------------------------------------------------------------------


def test_v5_passes_strict(simple_scale: ScoreDocument, raw_ids: set[str]) -> None:
    check_v5_origin_ids(simple_scale, raw_ids)


def test_v5_passes_structurally_without_the_raw_set(simple_scale: ScoreDocument) -> None:
    """Without the raw note set the structural half is still enforced."""
    check_v5_origin_ids(simple_scale, None)


def test_v5_fails_on_missing_provenance(mutate_payload: Any) -> None:
    """A note that is not synthetic must say where it came from."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][2]["origin_ids"] = []

    document = mutate_payload(mutate)
    with pytest.raises(InvariantViolationError) as excinfo:
        check_v5_origin_ids(document, None)
    assert excinfo.value.invariant == "V-5"


def test_v5_fails_on_unknown_raw_id(mutate_payload: Any, raw_ids: set[str]) -> None:
    """An origin id that resolves to nothing breaks the provenance chain."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][0]["origin_ids"] = ["raw-does-not-exist"]

    document = mutate_payload(mutate)
    with pytest.raises(InvariantViolationError) as excinfo:
        check_v5_origin_ids(document, raw_ids)
    assert excinfo.value.invariant == "V-5"


def test_v5_allows_synthetic_notes_without_provenance(mutate_payload: Any) -> None:
    """Engine-inserted material legitimately has no audio origin."""

    def mutate(payload: dict[str, Any]) -> None:
        note = payload["parts"][0]["notes"][2]
        note["origin_ids"] = []
        note["flags"]["synthetic"] = True

    check_v5_origin_ids(mutate_payload(mutate), None)


# --- V-6 -------------------------------------------------------------------


def test_v6_passes(simple_scale: ScoreDocument) -> None:
    check_v6_time_roundtrip(simple_scale)


def test_v6_fails_when_seconds_contradict_ticks(mutate_payload: Any) -> None:
    """The two time encodings must agree to within 2 ms."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][3]["time_on_s"] += 0.05

    _expect("V-6", mutate_payload(mutate), check_v6_time_roundtrip)


def test_v6_fails_when_a_tempo_event_time_is_inconsistent(mutate_payload: Any) -> None:
    """A second tempo event must sit where integrating from the first puts it."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["timing"]["tempo_map"].append(
            {"tick": 3840, "time_s": 9.0, "bpm": 120.0, "confidence": 1.0}
        )

    _expect("V-6", mutate_payload(mutate), check_v6_time_roundtrip)


def test_v6_tolerates_sub_millisecond_drift(mutate_payload: Any) -> None:
    """Drift below the 2 ms tolerance is float noise, not a bug."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][3]["time_on_s"] += 0.0005

    check_v6_time_roundtrip(mutate_payload(mutate))


# --- V-7 -------------------------------------------------------------------


def test_v7_passes(simple_scale: ScoreDocument) -> None:
    check_v7_tab_pitches(simple_scale)


def test_v7_fails_when_the_fret_does_not_sound_the_pitch(mutate_payload: Any) -> None:
    """A tab position that contradicts the notated pitch is a hard error."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][0]["tab"]["fret"] += 1

    _expect("V-7", mutate_payload(mutate), check_v7_tab_pitches)


def test_v7_fails_when_the_string_does_not_exist(mutate_payload: Any) -> None:
    """A six-string tuning has no string 7."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["notes"][0]["tab"]["string"] = 7

    _expect("V-7", mutate_payload(mutate), check_v7_tab_pitches)


def test_v7_fails_without_a_tuning(mutate_payload: Any) -> None:
    """Tab positions are meaningless without a declared tuning."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["instrument"]["tuning"] = None

    _expect("V-7", mutate_payload(mutate), check_v7_tab_pitches)


def test_v7_accounts_for_a_capo(mutate_payload: Any) -> None:
    """With a capo, the same shapes sound higher: open + capo + fret.

    Capo 2 turns the C major fingering into a sounding D major scale, and V-7
    must accept it without any fret changing.
    """
    transposed = [
        (62, "D", 0, 4),
        (64, "E", 0, 4),
        (66, "F", 1, 4),
        (67, "G", 0, 4),
        (69, "A", 0, 4),
        (71, "B", 0, 4),
        (73, "C", 1, 5),
        (74, "D", 0, 5),
    ]

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["instrument"]["tuning"]["capo"] = 2
        for note, (midi, step, alter, octave) in zip(
            payload["parts"][0]["notes"], transposed, strict=True
        ):
            note["midi"] = midi
            note["step"] = step
            note["alter"] = alter
            note["octave"] = octave

    check_v7_tab_pitches(mutate_payload(mutate))


def test_v7_fails_when_a_capo_is_ignored(mutate_payload: Any) -> None:
    """Fitting a capo without re-notating the pitches breaks the invariant."""

    def mutate(payload: dict[str, Any]) -> None:
        payload["parts"][0]["instrument"]["tuning"]["capo"] = 2

    _expect("V-7", mutate_payload(mutate), check_v7_tab_pitches)


def test_check_invariants_reports_the_first_failure(mutate_payload: Any) -> None:
    """The suite short-circuits, so the message names exactly one invariant."""

    def mutate(payload: dict[str, Any]) -> None:
        note = payload["parts"][0]["notes"][0]
        note["tick_off"] = note["tick_on"]
        note["time_off_s"] = note["time_on_s"]
        payload["parts"][0]["notes"][1]["tab"]["fret"] += 1

    with pytest.raises(InvariantViolationError) as excinfo:
        check_invariants(mutate_payload(mutate))
    assert excinfo.value.invariant == "V-1"
