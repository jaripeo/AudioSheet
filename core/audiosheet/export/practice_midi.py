"""Practice MIDI export — ARCHITECTURE.md Section 1.11.

A second, optional export quantised to the difficulty grid with flattened
velocities, for click-accurate practice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from audiosheet.schema import ScoreDocument

#: Every note is written at this velocity so the click stays audible.
FLAT_VELOCITY: Final[int] = 80


def to_practice_midi_bytes(doc: ScoreDocument) -> bytes:
    """Serialise a practice MIDI file with flattened velocities.

    Args:
        doc: The document to export.

    Returns:
        The MIDI file bytes.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED``.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("practice MIDI export lands in Phase 1")


def write_practice_midi(doc: ScoreDocument, path: Path) -> Path:
    """Write a practice MIDI file to disk.

    Args:
        doc: The document to export.
        path: Destination path.

    Returns:
        The path written.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED``.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("practice MIDI export lands in Phase 1")
