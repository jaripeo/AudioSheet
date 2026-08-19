"""S2 bleed suppression — ARCHITECTURE.md Section 1.5, post-separation step 2.

Attenuation is bounded to ``MAX_ATTENUATION_DB`` so the stage never invents
silence where the separator merely left a little bleed.
"""

from __future__ import annotations

from typing import Final

from audiosheet.separation.demucs_runner import StemSet

#: Spectral coherence above which two stems are considered to share content.
COHERENCE_THRESHOLD: Final[float] = 0.85

#: Level advantage that makes one stem the owner of a shared band, in dB.
DOMINANCE_DB: Final[float] = 12.0

#: Hard bound on how much the weaker stem may be attenuated, in dB.
MAX_ATTENUATION_DB: Final[float] = -6.0


def suppress_bleed(stems: StemSet) -> StemSet:
    """Soft-mask cross-stem bleed within the bounded attenuation.

    Args:
        stems: The gated stem set.

    Returns:
        A new stem set with bleed suppressed.

    Raises:
        NotImplementedError: Phase 4.
    """
    raise NotImplementedError("S2 bleed suppression lands in Phase 4")
