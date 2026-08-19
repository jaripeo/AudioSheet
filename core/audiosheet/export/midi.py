"""MIDI 1.0 Type 1 export — ARCHITECTURE.md Section 1.11.

One track per part, tempo and meter meta events from the timing grid, drums forced
to channel 9. Pitch bends are emitted only when ``micro_cents`` exceeds
``PITCH_BEND_THRESHOLD_CENTS`` and the export profile enables them.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from audiosheet.schema import ScoreDocument

#: Pulses per quarter note written into the MIDI header.
PPQ: Final[int] = 960

#: General MIDI percussion channel, zero-indexed.
DRUM_CHANNEL: Final[int] = 9

#: Micro-tuning below this magnitude is not worth a pitch bend, in cents.
PITCH_BEND_THRESHOLD_CENTS: Final[float] = 25.0


def to_midi_bytes(doc: ScoreDocument, *, pitch_bends: bool = False) -> bytes:
    """Serialise a document to a Type 1 MIDI file.

    Args:
        doc: The document to export.
        pitch_bends: Whether to emit micro-tuning as pitch bends.

    Returns:
        The MIDI file bytes.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED``.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("MIDI export lands in Phase 1")


def write_midi(doc: ScoreDocument, path: Path, *, pitch_bends: bool = False) -> Path:
    """Write a Type 1 MIDI file to disk.

    Args:
        doc: The document to export.
        path: Destination path.
        pitch_bends: Whether to emit micro-tuning as pitch bends.

    Returns:
        The path written.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED``.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("MIDI export lands in Phase 1")
