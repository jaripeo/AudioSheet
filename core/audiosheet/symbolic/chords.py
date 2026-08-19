"""S5.5 chord recognition — ARCHITECTURE.md Section 1.8.

Two independent estimates are fused: an audio-side model over beat-synchronous
chroma, and a symbolic-side template match over the pitches S3 actually found.
When they disagree on quality but agree on root, the symbolic quality wins because
it saw real note content; when they disagree on root, audio wins and confidence
drops by ``ROOT_DISAGREEMENT_PENALTY``.
"""

from __future__ import annotations

from typing import Final

from audiosheet.ingest.decode import AudioBundle
from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import ChordEvent, Note, TimingGrid

#: Confidence deduction applied when the two estimates disagree on the root.
ROOT_DISAGREEMENT_PENALTY: Final[float] = 0.2

#: Confidence at or above which a chord label is trusted by the difficulty engine.
CHORD_TRUST_THRESHOLD: Final[float] = 0.5


def recognise_audio(bundle: AudioBundle, grid: TimingGrid, ctx: StageContext) -> list[ChordEvent]:
    """Estimate chords from beat-synchronous chroma of the full mix.

    Args:
        bundle: The S0 output.
        grid: The timing grid, for beat synchronisation.
        ctx: Ambient stage services.

    Returns:
        One chord event per beat, before merging.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.5 audio chord recognition lands in Phase 6")


def recognise_symbolic(notes: list[Note], grid: TimingGrid) -> list[ChordEvent]:
    """Estimate chords by template matching over transcribed pitches.

    Args:
        notes: Notes sounding across the piece.
        grid: The timing grid, for beat windows.

    Returns:
        One chord event per beat, before merging.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.5 symbolic chord recognition lands in Phase 6")


def fuse(audio: list[ChordEvent], symbolic: list[ChordEvent]) -> list[ChordEvent]:
    """Fuse the two estimates and merge consecutive identical labels.

    Args:
        audio: Audio-side estimates.
        symbolic: Symbolic-side estimates.

    Returns:
        The fused chord track.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.5 chord fusion lands in Phase 6")
