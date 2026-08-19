"""S3.1 polyphonic transcription with basic-pitch — ARCHITECTURE.md Section 1.6.1.

Runs under ONNX Runtime (INV-1: the model file is vendored, never downloaded).
The model emits three posteriorgrams: onsets, note activations and pitch
contours, at a frame hop of ``BASIC_PITCH_HOP_SAMPLES`` samples at 22050 Hz.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import RawNote
from audiosheet.separation.demucs_runner import Stem
from audiosheet.transcription.basic_pitch_params import BasicPitchParams

Posteriorgram = npt.NDArray[np.float32]


@dataclass(frozen=True)
class BasicPitchOutput:
    """The three raw posteriorgrams, before peak-picking.

    Attributes:
        onsets: Onset probabilities, shaped (frames, 88).
        notes: Note activations, shaped (frames, 88).
        contours: Sub-semitone pitch contours, shaped (frames, 264).
        frame_ms: Time resolution, recorded in provenance.
    """

    onsets: Posteriorgram
    notes: Posteriorgram
    contours: Posteriorgram
    frame_ms: float


def infer(stem: Stem, ctx: StageContext) -> BasicPitchOutput:
    """Run the vendored basic-pitch ONNX model over a stem.

    Args:
        stem: The stem to transcribe; the 22.05 kHz mono view is used.
        ctx: Ambient stage services.

    Returns:
        The three posteriorgrams.

    Raises:
        AudioSheetError: ``E_MODEL_MISSING`` or ``E_MODEL_INTEGRITY``.
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S3.1 basic-pitch inference lands in Phase 5")


def decode_notes(
    output: BasicPitchOutput,
    params: BasicPitchParams,
    stem_name: str,
) -> list[RawNote]:
    """Peak-pick and threshold the posteriorgrams into note events.

    Args:
        output: The model output.
        params: Per-stem decoding thresholds.
        stem_name: Stem name, recorded on each ``RawNote``.

    Returns:
        The decoded note events.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S3.1 note decoding lands in Phase 5")
