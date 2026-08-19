"""S5 orchestrator — ARCHITECTURE.md Section 1.8.

Turns per-stem note clouds into one notation-ready ``ScoreDocument`` at Complex
difficulty. The step ordering (grid, quantise, spell, voices, chords, staves) is
normative.
"""

from __future__ import annotations

from audiosheet.ingest.decode import AudioBundle
from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import KeyEstimate, ScoreDocument, TimingGrid
from audiosheet.transcription.drums import RawDrumSet
from audiosheet.transcription.postprocess import RawNoteSet


def consolidate(
    bundle: AudioBundle,
    grid: TimingGrid,
    key: KeyEstimate,
    note_sets: list[RawNoteSet],
    drums: RawDrumSet | None,
    ctx: StageContext,
) -> ScoreDocument:
    """Assemble the canonical Complex-difficulty document.

    Args:
        bundle: The S0 output, for ``ScoreDocument.source``.
        grid: The S1 timing grid.
        key: The S1.5 key estimate.
        note_sets: One post-processed note set per pitched stem.
        drums: The S4 percussion set, when the drums stem was present.
        ctx: Ambient stage services.

    Returns:
        The canonical ``ScoreDocument`` at Complex difficulty.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5 consolidation lands in Phase 6")
