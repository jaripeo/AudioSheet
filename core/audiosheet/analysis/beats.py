"""S1.1 beat and downbeat tracking — ARCHITECTURE.md Section 1.4.

Primary path: a joint beat/downbeat RNN with a DBN post-processor. Fallback path:
``librosa`` beat tracking plus a spectral-flux downbeat heuristic. The fallback
MUST always be present so the pipeline cannot hard-fail.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from audiosheet.ingest.decode import AudioBundle
from audiosheet.pipeline.stage import StageContext

#: Meters the DBN is allowed to consider.
BEATS_PER_BAR_CANDIDATES: Final[tuple[int, ...]] = (2, 3, 4, 6)

#: Frame rate of the beat activation function, in Hz.
BEAT_TRACKER_FPS: Final[int] = 100

#: Tempo search bounds for the DBN, in BPM.
MIN_BPM: Final[float] = 45.0
MAX_BPM: Final[float] = 215.0

BeatTrackerBackend = Literal["rnn-dbn", "librosa"]


@dataclass(frozen=True)
class RawBeat:
    """One tracked beat before it is placed on the tick grid."""

    time_s: float
    beat_in_bar: int
    is_downbeat: bool
    confidence: float


@dataclass(frozen=True)
class BeatTrack:
    """The S1.1 output."""

    beats: list[RawBeat]
    backend: BeatTrackerBackend
    mean_confidence: float


def track_beats(bundle: AudioBundle, ctx: StageContext) -> BeatTrack:
    """Track beats and downbeats on the full mix.

    Args:
        bundle: The S0 output; the 16 kHz mono variant is used.
        ctx: Ambient stage services.

    Returns:
        The beat track.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.1 beat tracking lands in Phase 3")


def track_beats_fallback(bundle: AudioBundle, ctx: StageContext) -> BeatTrack:
    """Track beats with the librosa fallback path.

    Args:
        bundle: The S0 output.
        ctx: Ambient stage services.

    Returns:
        The beat track.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.1 fallback beat tracking lands in Phase 3")
