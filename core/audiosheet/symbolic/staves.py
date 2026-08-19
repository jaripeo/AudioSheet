"""S5.6 staff and part assignment — ARCHITECTURE.md Section 1.8.

Piano gets a grand staff split at the pitch that minimises cross-staff notes,
seeded at middle C and adjusted by a DP that penalises hand crossings.
"""

from __future__ import annotations

from typing import Final

from audiosheet.schema import Note, Part
from audiosheet.transcription.postprocess import RawNoteSet

#: Initial grand-staff split point, MIDI 60 (middle C).
GRAND_STAFF_SPLIT_SEED: Final[int] = 60


def build_part(notes: RawNoteSet, stem: str) -> Part:
    """Build the part for one stem, with clefs and notation mode resolved.

    Args:
        notes: The stem's post-processed note set.
        stem: Stem name.

    Returns:
        The assembled part.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.6 part assembly lands in Phase 6")


def split_grand_staff(notes: list[Note]) -> list[Note]:
    """Assign piano notes to staff 1 or 2, minimising hand crossings.

    Args:
        notes: The piano part's notes.

    Returns:
        New notes with ``staff`` assigned.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.6 grand-staff splitting lands in Phase 6")
