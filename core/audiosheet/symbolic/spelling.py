"""S5.3 pitch spelling — ARCHITECTURE.md Section 1.8.

MIDI numbers carry no spelling: Db4 and C#4 are the same integer, and the wrong
choice makes a score unreadable. ps13s1 (Meredith) supplies the base decision,
then the key regions from S1.5 override it.

``step``, ``alter`` and ``octave`` are always emitted explicitly; the renderer
never guesses.
"""

from __future__ import annotations

from typing import Final

from audiosheet.schema import KeyEstimate, Note

#: ps13s1 context windows, in notes.
PS13_K_PRE: Final[int] = 10
PS13_K_POST: Final[int] = 42


def spell(notes: list[Note], key: KeyEstimate) -> list[Note]:
    """Assign step/alter/octave to every note.

    Args:
        notes: Notes to spell, in onset order.
        key: The S1.5 key estimate, including regions.

    Returns:
        New notes with spelling assigned.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.3 pitch spelling lands in Phase 6")


def spell_midi(midi: int, fifths: int, ascending: bool) -> tuple[str, int, int]:
    """Spell one MIDI pitch inside a key signature.

    Args:
        midi: MIDI note number.
        fifths: Key signature, -7..7.
        ascending: Whether the melodic line is rising, which prefers sharps.

    Returns:
        The ``(step, alter, octave)`` triple.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.3 pitch spelling lands in Phase 6")
