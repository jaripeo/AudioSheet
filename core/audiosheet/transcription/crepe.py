"""S3.2 monophonic f0 tracking with CREPE — ARCHITECTURE.md Section 1.6.2.

Used for bass and vocals, where a dedicated f0 tracker clearly beats a
polyphonic model. Input is 16 kHz mono; the output is a 360-bin cents activation
at 20-cent resolution plus per-frame confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import numpy.typing as npt

from audiosheet.pipeline.stage import StageContext
from audiosheet.separation.demucs_runner import Stem

#: Analysis hop, in seconds.
HOP_S: Final[float] = 0.010

#: Cents-axis resolution of the activation matrix.
CENTS_PER_BIN: Final[int] = 20

#: Number of cents bins the model emits.
CENTS_BINS: Final[int] = 360

#: Confidence floor; bass is relaxed because low partials reduce confidence.
CONFIDENCE_FLOOR: Final[float] = 0.50
CONFIDENCE_FLOOR_BASS: Final[float] = 0.35

#: Vibrato is declared when a 4-8 Hz component exceeds this peak-to-peak, in cents.
VIBRATO_CENTS_THRESHOLD: Final[float] = 25.0

CentsTrack = npt.NDArray[np.float32]


@dataclass(frozen=True)
class F0Track:
    """A smoothed f0 track.

    Attributes:
        cents: Pitch in cents relative to C0, one value per hop.
        confidence: Per-frame confidence in ``[0, 1]``.
        hop_s: Hop size, in seconds.
    """

    cents: CentsTrack
    confidence: CentsTrack
    hop_s: float


def infer(stem: Stem, ctx: StageContext) -> F0Track:
    """Run the vendored CREPE ONNX model and Viterbi-smooth the cents axis.

    Args:
        stem: The stem to track; the 16 kHz mono view is used.
        ctx: Ambient stage services.

    Returns:
        The smoothed f0 track.

    Raises:
        AudioSheetError: ``E_MODEL_MISSING`` or ``E_MODEL_INTEGRITY``.
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S3.2 CREPE inference lands in Phase 5")


def confidence_floor_for(stem_name: str) -> float:
    """Return the confidence floor for ``stem_name``.

    Args:
        stem_name: Stem name.

    Returns:
        The floor below which frames are discarded.
    """
    return CONFIDENCE_FLOOR_BASS if stem_name == "bass" else CONFIDENCE_FLOOR
