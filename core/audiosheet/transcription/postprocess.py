"""S3.3 per-stem post-processing — ARCHITECTURE.md Section 1.6.3.

Six steps, applied in order to every pitched stem: onset refinement, repeated-note
splitting, octave-error correction, duplicate/overlap resolution, velocity
estimation and confidence scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import RawNote
from audiosheet.separation.demucs_runner import Stem

#: A re-articulation peak this far after a note's own onset splits the note.
REARTICULATION_MIN_GAP_S: Final[float] = 0.100

#: Onset probability a re-articulation peak must exceed.
REARTICULATION_PEAK_THRESHOLD: Final[float] = 0.5

#: Sub-octave energy advantage that triggers an octave correction, in dB.
OCTAVE_CORRECTION_DB: Final[float] = 6.0

#: Same-pitch overlap fraction above which two notes are merged.
MERGE_OVERLAP_FRACTION: Final[float] = 0.50

#: Gap left when truncating an earlier note against a later onset, in seconds.
TRUNCATION_GAP_S: Final[float] = 0.010

#: Window over which velocity RMS is measured, in seconds.
VELOCITY_WINDOW_S: Final[float] = 0.050

#: Floor for the velocity RMS measurement, in dBFS.
VELOCITY_FLOOR_DB: Final[float] = -60.0

#: Duration at which the confidence duration prior saturates, in milliseconds.
CONFIDENCE_DURATION_PRIOR_MS: Final[float] = 250.0

#: Confidence blend weights: onset probability, mean frame probability, duration.
CONFIDENCE_WEIGHTS: Final[tuple[float, float, float]] = (0.5, 0.3, 0.2)


@dataclass(frozen=True)
class RawNoteSet:
    """The S3/S4 output for one stem.

    Attributes:
        stem: Stem the notes came from.
        notes: Post-processed note events.
        model: Which transcription model produced them.
        frame_ms: Time resolution of that model.
        octave_corrections: How many notes were moved an octave.
    """

    stem: str
    notes: list[RawNote]
    model: str
    frame_ms: float
    octave_corrections: int = 0
    warnings: list[str] = field(default_factory=list)

    def ids(self) -> set[str]:
        """Return every note id, for the strict form of validator V-5."""
        return {note.id for note in self.notes}

    def content_hash(self) -> str:
        """Return a stable fingerprint for cache keying."""
        payload = "|".join(f"{n.id}:{n.onset_s:.6f}:{n.offset_s:.6f}:{n.midi}" for n in self.notes)
        return blake3_hex(self.stem.encode("utf-8"), payload.encode("utf-8"))


def postprocess(notes: list[RawNote], stem: Stem, ctx: StageContext) -> RawNoteSet:
    """Apply the six post-processing steps to a stem's note events.

    Args:
        notes: Raw decoded note events.
        stem: The stem they came from, for spectrogram-based checks.
        ctx: Ambient stage services.

    Returns:
        The post-processed note set.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S3.3 post-processing lands in Phase 5")


def estimate_velocity(rms_db: float) -> int:
    """Map a windowed RMS level to a MIDI velocity.

    ``velocity = clamp(round(127 * (rms_db + 60) / 60), 1, 127)``.

    Args:
        rms_db: RMS over the note's first ``VELOCITY_WINDOW_S``, in dBFS.

    Returns:
        A MIDI velocity in ``1..127``.
    """
    scaled = round(127.0 * (max(rms_db, VELOCITY_FLOOR_DB) + 60.0) / 60.0)
    return max(1, min(127, scaled))


def score_confidence(onset_prob: float, mean_frame_prob: float, duration_ms: float) -> float:
    """Blend onset probability, frame probability and a duration prior.

    Args:
        onset_prob: Onset probability in ``[0, 1]``.
        mean_frame_prob: Mean frame probability over the note, in ``[0, 1]``.
        duration_ms: Note duration in milliseconds.

    Returns:
        A confidence in ``[0, 1]``.
    """
    w_onset, w_frame, w_duration = CONFIDENCE_WEIGHTS
    duration_prior = min(1.0, duration_ms / CONFIDENCE_DURATION_PRIOR_MS)
    blended = w_onset * onset_prob + w_frame * mean_frame_prob + w_duration * duration_prior
    return max(0.0, min(1.0, blended))
