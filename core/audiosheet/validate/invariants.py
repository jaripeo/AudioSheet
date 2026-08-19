"""Structural invariants V-1..V-7 — ARCHITECTURE.md Section 1.9.

The S6 gate performs pure checks and no musical decisions. It MUST fail loudly
rather than pass a malformed document downstream, and the difficulty engine
re-runs the same checks after every ``reduce`` (Section 2.0, step 14).

Every check is an independent function so that a failure names exactly one
invariant, and so each one can be unit-tested with both a passing and a
deliberately-failing document.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from itertools import pairwise

from audiosheet.config.constants import TICK_SECONDS_ROUNDTRIP_TOLERANCE_S
from audiosheet.pipeline.errors import InvariantViolationError
from audiosheet.schema import Measure, Note, Part, ScoreDocument
from audiosheet.symbolic.grid import (
    measure_capacity_ticks,
    quarters_to_seconds,
    seconds_to_tick,
    tick_to_seconds,
)

#: The invariant identifiers this module enforces, in document order.
INVARIANTS: tuple[str, ...] = ("V-1", "V-2", "V-3", "V-4", "V-5", "V-6", "V-7")


def _rendered_notes(part: Part) -> list[Note]:
    """Return the notes of ``part`` that are actually drawn.

    Notes carried for provenance only (``render = False``) are excluded from the
    layout invariants; they deliberately overlap the notes that replaced them.
    """
    return [note for note in part.notes if note.render]


def check_v1_durations(doc: ScoreDocument) -> None:
    """V-1: every note has ``tick_on < tick_off`` and a duration of >= 1 tick.

    Raises:
        InvariantViolationError: On a zero-length or inverted note.
    """
    for part in doc.parts:
        for note in part.notes:
            if note.tick_off <= note.tick_on:
                raise InvariantViolationError(
                    "V-1",
                    f"note {note.id} in part {part.id} has tick_on={note.tick_on} "
                    f">= tick_off={note.tick_off}",
                    tick=note.tick_on,
                )


def check_v2_no_voice_overlap(doc: ScoreDocument) -> None:
    """V-2: no two rendered notes in one ``(part, staff, voice)`` overlap.

    Notes sharing an onset within a voice are legal only as chord members
    (MusicXML ``<chord/>``), which the flag ``is_chord_member`` marks.

    Raises:
        InvariantViolationError: On an illegal overlap.
    """
    for part in doc.parts:
        by_voice: dict[tuple[int, int], list[Note]] = defaultdict(list)
        for note in _rendered_notes(part):
            by_voice[(note.staff, note.voice)].append(note)

        for (staff, voice), notes in sorted(by_voice.items()):
            ordered = sorted(notes, key=lambda n: (n.tick_on, n.tick_off, n.id))
            for earlier, later in pairwise(ordered):
                if later.tick_on >= earlier.tick_off:
                    continue
                if later.tick_on == earlier.tick_on and later.is_chord_member:
                    continue
                raise InvariantViolationError(
                    "V-2",
                    f"notes {earlier.id} and {later.id} overlap in part {part.id} "
                    f"staff {staff} voice {voice} "
                    f"({earlier.tick_on}-{earlier.tick_off} vs "
                    f"{later.tick_on}-{later.tick_off})",
                    tick=later.tick_on,
                )


def _measure_for_tick(measures: Iterable[Measure], tick: int) -> Measure | None:
    for measure in measures:
        if measure.tick_start <= tick < measure.tick_end:
            return measure
    return None


def check_v3_measures(doc: ScoreDocument) -> None:
    """V-3: measures are contiguous and gapless from tick 0, and contain the notes.

    Raises:
        InvariantViolationError: On a gap, an overlap, a non-zero start, or a note
            whose onset falls outside every declared measure.
    """
    measures = sorted(doc.timing.measures, key=lambda m: m.tick_start)
    if not measures:
        raise InvariantViolationError("V-3", "document declares no measures")

    if measures[0].tick_start != 0:
        raise InvariantViolationError(
            "V-3",
            f"first measure starts at tick {measures[0].tick_start}, expected 0",
            tick=measures[0].tick_start,
        )

    for earlier, later in pairwise(measures):
        if earlier.tick_end != later.tick_start:
            raise InvariantViolationError(
                "V-3",
                f"measures {earlier.index} and {later.index} are not contiguous "
                f"({earlier.tick_end} != {later.tick_start})",
                tick=earlier.tick_end,
            )

    for measure in measures:
        if measure.tick_end <= measure.tick_start:
            raise InvariantViolationError(
                "V-3",
                f"measure {measure.index} has a non-positive span",
                tick=measure.tick_start,
            )

    last_tick = measures[-1].tick_end
    for part in doc.parts:
        for note in part.notes:
            if _measure_for_tick(measures, note.tick_on) is None:
                raise InvariantViolationError(
                    "V-3",
                    f"note {note.id} onset {note.tick_on} in part {part.id} falls "
                    f"outside every declared measure (0..{last_tick})",
                    tick=note.tick_on,
                )
            if note.tick_off > last_tick:
                raise InvariantViolationError(
                    "V-3",
                    f"note {note.id} ends at {note.tick_off}, past the last measure "
                    f"boundary {last_tick}",
                    tick=note.tick_off,
                )


def check_v4_measure_capacity(doc: ScoreDocument) -> None:
    """V-4: no measure holds more than its meter allows, in any voice.

    An over-full measure is the signature of a quantiser bug, so this checks two
    things: an explicit (non-pickup) measure spans exactly its meter capacity,
    and no voice's clipped note durations exceed that span.

    Raises:
        InvariantViolationError: On a measure span that contradicts the meter, or on
            an over-full voice.
    """
    signatures = doc.timing.time_signatures
    for measure in doc.timing.measures:
        if not 0 <= measure.time_signature_ref < len(signatures):
            raise InvariantViolationError(
                "V-4",
                f"measure {measure.index} references time signature "
                f"{measure.time_signature_ref}, which does not exist",
                tick=measure.tick_start,
            )
        signature = signatures[measure.time_signature_ref]
        capacity = measure_capacity_ticks(signature.numerator, signature.denominator)
        span = measure.tick_end - measure.tick_start

        if not measure.implicit and span != capacity:
            raise InvariantViolationError(
                "V-4",
                f"measure {measure.index} spans {span} ticks but "
                f"{signature.numerator}/{signature.denominator} holds {capacity}",
                tick=measure.tick_start,
            )
        if measure.implicit and span > capacity:
            raise InvariantViolationError(
                "V-4",
                f"pickup measure {measure.index} spans {span} ticks, more than the "
                f"{capacity} its meter allows",
                tick=measure.tick_start,
            )

        for part in doc.parts:
            occupied: dict[tuple[int, int], int] = defaultdict(int)
            for note in _rendered_notes(part):
                if note.is_chord_member:
                    continue
                overlap = min(note.tick_off, measure.tick_end) - max(
                    note.tick_on, measure.tick_start
                )
                if overlap > 0:
                    occupied[(note.staff, note.voice)] += overlap
            for (staff, voice), total in sorted(occupied.items()):
                if total > span:
                    raise InvariantViolationError(
                        "V-4",
                        f"measure {measure.index} of part {part.id} staff {staff} "
                        f"voice {voice} holds {total} ticks, exceeding its {span}",
                        tick=measure.tick_start,
                    )


def check_v5_origin_ids(doc: ScoreDocument, known_raw_ids: set[str] | None = None) -> None:
    """V-5: every ``origin_ids`` entry resolves to a real ``RawNote`` id.

    The raw note set lives outside the document, so the caller supplies it. When
    ``known_raw_ids`` is ``None`` the structural half of the invariant is still
    enforced: ids are non-empty and unique, and any note that is not flagged
    ``synthetic`` must carry at least one origin.

    Args:
        doc: The document under test.
        known_raw_ids: Ids emitted by S3/S4, when available.

    Raises:
        InvariantViolationError: On an empty, duplicated or unresolvable origin id, or
            on an audio-derived note with no provenance.
    """
    for part in doc.parts:
        for note in part.notes:
            if not note.flags.synthetic and not note.origin_ids:
                raise InvariantViolationError(
                    "V-5",
                    f"note {note.id} in part {part.id} is not synthetic but carries no origin_ids",
                    tick=note.tick_on,
                )
            if len(set(note.origin_ids)) != len(note.origin_ids):
                raise InvariantViolationError(
                    "V-5",
                    f"note {note.id} has duplicate origin_ids",
                    tick=note.tick_on,
                )
            for origin in note.origin_ids:
                if not origin:
                    raise InvariantViolationError(
                        "V-5", f"note {note.id} has an empty origin id", tick=note.tick_on
                    )
                if known_raw_ids is not None and origin not in known_raw_ids:
                    raise InvariantViolationError(
                        "V-5",
                        f"note {note.id} references unknown raw note {origin!r}",
                        tick=note.tick_on,
                    )


def check_v6_time_roundtrip(doc: ScoreDocument) -> None:
    """V-6: the tick and seconds encodings agree to within +/- 2 ms.

    Three things are checked: each tempo event's declared ``time_s`` matches the
    value integrated from its predecessor; each note's declared seconds match its
    ticks; and ticks survive a seconds round-trip.

    Raises:
        InvariantViolationError: On any disagreement beyond the tolerance.
    """
    grid = doc.timing
    tolerance = TICK_SECONDS_ROUNDTRIP_TOLERANCE_S

    if not grid.tempo_map:
        raise InvariantViolationError("V-6", "document declares no tempo events")
    if grid.tempo_map[0].tick != 0:
        raise InvariantViolationError(
            "V-6",
            f"first tempo event is at tick {grid.tempo_map[0].tick}, expected 0",
            tick=grid.tempo_map[0].tick,
        )

    events = sorted(grid.tempo_map, key=lambda e: e.tick)
    for earlier, later in pairwise(events):
        quarters = (later.tick - earlier.tick) / grid.ppq
        integrated = earlier.time_s + quarters_to_seconds(quarters, earlier.bpm)
        if abs(integrated - later.time_s) > tolerance:
            raise InvariantViolationError(
                "V-6",
                f"tempo event at tick {later.tick} declares time_s={later.time_s} but "
                f"integrating from tick {earlier.tick} gives {integrated:.6f}",
                tick=later.tick,
            )

    for part in doc.parts:
        for note in part.notes:
            for label, tick, declared in (
                ("onset", note.tick_on, note.time_on_s),
                ("offset", note.tick_off, note.time_off_s),
            ):
                computed = tick_to_seconds(grid, tick)
                if abs(computed - declared) > tolerance:
                    raise InvariantViolationError(
                        "V-6",
                        f"note {note.id} {label} declares {declared}s but tick {tick} "
                        f"maps to {computed:.6f}s",
                        tick=tick,
                    )
                if seconds_to_tick(grid, computed) != tick:
                    raise InvariantViolationError(
                        "V-6",
                        f"note {note.id} {label} tick {tick} does not survive a seconds round-trip",
                        tick=tick,
                    )


def check_v7_tab_pitches(doc: ScoreDocument) -> None:
    """V-7: every tab position reproduces its note's MIDI pitch.

    ``sounding = open_string_pitch + capo + fret``, with string 1 the highest
    pitched. A mismatch is a hard error, never a warning (Section 2.3.5).

    Raises:
        InvariantViolationError: On a missing tuning, an out-of-range string, or a
            position that does not sound the note's pitch.
    """
    for part in doc.parts:
        for note in part.notes:
            tab = note.tab
            if tab is None:
                continue
            tuning = part.instrument.tuning
            if tuning is None:
                raise InvariantViolationError(
                    "V-7",
                    f"note {note.id} carries a tab position but part {part.id} declares no tuning",
                    tick=note.tick_on,
                )
            if not 1 <= tab.string <= len(tuning.strings):
                raise InvariantViolationError(
                    "V-7",
                    f"note {note.id} uses string {tab.string}, outside the "
                    f"{len(tuning.strings)} strings of tuning {tuning.name!r}",
                    tick=note.tick_on,
                )
            if tab.fret < 0:
                raise InvariantViolationError(
                    "V-7",
                    f"note {note.id} is a sounding note but its fret is {tab.fret} "
                    "(muted positions belong in a chord frame, not on a note)",
                    tick=note.tick_on,
                )
            expected = tuning.strings[tab.string - 1] + tuning.capo + tab.fret
            if expected != note.midi:
                raise InvariantViolationError(
                    "V-7",
                    f"note {note.id} is MIDI {note.midi} but string {tab.string} "
                    f"fret {tab.fret} with capo {tuning.capo} sounds MIDI {expected}",
                    tick=note.tick_on,
                )


#: The full check suite, in invariant order.
CHECKS: tuple[tuple[str, Callable[[ScoreDocument], None]], ...] = (
    ("V-1", check_v1_durations),
    ("V-2", check_v2_no_voice_overlap),
    ("V-3", check_v3_measures),
    ("V-4", check_v4_measure_capacity),
    ("V-5", check_v5_origin_ids),
    ("V-6", check_v6_time_roundtrip),
    ("V-7", check_v7_tab_pitches),
)


def check_invariants(
    doc: ScoreDocument,
    *,
    known_raw_ids: set[str] | None = None,
) -> None:
    """Run every invariant in order, failing on the first violation.

    Args:
        doc: The document under test.
        known_raw_ids: Raw note ids for the strict form of V-5.

    Raises:
        InvariantViolationError: On the first invariant that fails.
    """
    for name, check in CHECKS:
        if name == "V-5":
            check_v5_origin_ids(doc, known_raw_ids)
        else:
            check(doc)
