"""S2 energy gating — ARCHITECTURE.md Section 1.5, post-separation step 1.

Stems more than ``STEM_PRESENCE_GATE_DB`` below the loudest stem are marked
absent and skipped entirely. This is the single largest end-to-end speedup: a
solo-piano recording skips four stems.
"""

from __future__ import annotations

from audiosheet.pipeline.stage import StageContext
from audiosheet.separation.demucs_runner import StemSet


def apply_presence_gate(stems: StemSet, ctx: StageContext) -> StemSet:
    """Mark quiet stems absent and record a ``W_STEM_QUIET`` warning for each.

    Args:
        stems: The raw separation output.
        ctx: Ambient stage services.

    Returns:
        A new stem set with ``present`` resolved.

    Raises:
        NotImplementedError: Phase 4.
    """
    raise NotImplementedError("S2 energy gating lands in Phase 4")
