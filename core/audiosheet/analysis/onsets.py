"""Shared onset/novelty utilities — ARCHITECTURE.md Sections 1.4 and 1.6.3.

The high-resolution novelty curve (hop 128 at 44.1 kHz, about 2.9 ms) is used
both for beat tracking evidence and for snapping model onsets.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import numpy.typing as npt

from audiosheet.ingest.decode import Pcm

#: Hop size, in samples at 44.1 kHz, of the high-resolution novelty curve.
NOVELTY_HOP_SAMPLES: Final[int] = 128

#: Half-width of the window used to snap a model onset to a novelty peak.
ONSET_SNAP_WINDOW_S: Final[float] = 0.030

NoveltyCurve = npt.NDArray[np.float32]


def spectral_flux(pcm: Pcm, sample_rate: int, hop: int = NOVELTY_HOP_SAMPLES) -> NoveltyCurve:
    """Compute a spectral-flux novelty curve.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.
        hop: Hop size in samples.

    Returns:
        The novelty curve, one value per hop.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("novelty curves land in Phase 3")


def snap_to_peak(onset_s: float, novelty: NoveltyCurve, sample_rate: int, hop: int) -> float:
    """Snap an onset to the nearest novelty peak within the search window.

    Args:
        onset_s: The model's onset estimate, in seconds.
        novelty: The novelty curve.
        sample_rate: Sample rate the curve was computed at.
        hop: Hop size the curve was computed with.

    Returns:
        The refined onset, in seconds.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("onset refinement lands in Phase 5")
