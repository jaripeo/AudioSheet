"""Loudness normalisation — ARCHITECTURE.md Section 1.3, step 5.

Integrated loudness targets ``TARGET_LUFS`` (ITU-R BS.1770-4) with true-peak
limiting at ``TRUE_PEAK_CEILING_DBTP``. The gain is never applied to the copy
used for waveform display.
"""

from __future__ import annotations

from audiosheet.ingest.decode import Pcm


def integrated_lufs(pcm: Pcm, sample_rate: int) -> float:
    """Measure integrated loudness in LUFS (ITU-R BS.1770-4).

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        Integrated loudness in LUFS.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("loudness measurement lands in Phase 1")


def normalise(pcm: Pcm, sample_rate: int) -> tuple[Pcm, float]:
    """Normalise to the loudness target and limit true peaks.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        The normalised PCM and the gain applied, in dB.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("loudness normalisation lands in Phase 1")


def detect_edge_silence(pcm: Pcm, sample_rate: int) -> tuple[float, float]:
    """Measure leading and trailing silence without trimming it.

    Trimming would desynchronise user playback, so the spans are reported only.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        Leading and trailing silence, in seconds.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("silence detection lands in Phase 1")
