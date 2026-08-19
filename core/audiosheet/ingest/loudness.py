"""Loudness normalisation — ARCHITECTURE.md Section 1.3, step 5.

Integrated loudness targets ``TARGET_LUFS`` (ITU-R BS.1770-4) with true-peak
limiting at ``TRUE_PEAK_CEILING_DBTP``. The gain is never applied to the copy
used for waveform display.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Final

import numpy as np
import pyloudnorm

from audiosheet.config.constants import (
    SILENCE_FLOOR_DBFS,
    SILENCE_MIN_SPAN_S,
    TARGET_LUFS,
    TRUE_PEAK_CEILING_DBTP,
)
from audiosheet.ingest.resample import resample

if TYPE_CHECKING:  # a runtime import would cycle: decode imports this module
    from audiosheet.ingest.decode import Pcm

#: Oversampling factor for true-peak estimation. BS.1770-4 Annex 2 requires at
#: least 4x for material at or below 48 kHz.
TRUE_PEAK_OVERSAMPLE: Final[int] = 4


def dbfs_to_amplitude(dbfs: float) -> float:
    """Convert a dBFS level to a linear amplitude.

    Args:
        dbfs: Level in dBFS, where ``0.0`` is full scale.

    Returns:
        The equivalent linear amplitude.
    """
    return float(10.0 ** (dbfs / 20.0))


def amplitude_to_dbfs(amplitude: float) -> float:
    """Convert a linear amplitude to dBFS.

    Args:
        amplitude: Linear amplitude; silence is ``0.0``.

    Returns:
        The level in dBFS, or negative infinity for digital silence.
    """
    if amplitude <= 0.0:
        return -math.inf
    return 20.0 * math.log10(amplitude)


def integrated_lufs(pcm: Pcm, sample_rate: int) -> float:
    """Measure integrated loudness in LUFS (ITU-R BS.1770-4).

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        Integrated loudness in LUFS, or negative infinity for digital silence.

    Raises:
        ValueError: When ``pcm`` is not planar, ``sample_rate`` is not positive,
            or the signal is shorter than the meter's 400 ms block. Ingestion
            never sees the last case: ``MIN_DURATION_S`` is 1.0 s.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    if sample_rate <= 0:
        raise ValueError(f"sample rate must be positive, got {sample_rate}")

    meter = pyloudnorm.Meter(sample_rate)
    interleaved = np.ascontiguousarray(pcm.T, dtype=np.float64)
    return float(meter.integrated_loudness(interleaved))


def true_peak_dbtp(pcm: Pcm, sample_rate: int) -> float:
    """Estimate the true peak in dBTP.

    The sample peak understates the peak of the reconstructed analogue
    waveform, so the signal is oversampled ``TRUE_PEAK_OVERSAMPLE`` times before
    the maximum is taken.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        The true peak in dBTP, or negative infinity for digital silence.

    Raises:
        ValueError: When ``pcm`` is not planar or ``sample_rate`` is not positive.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    if sample_rate <= 0:
        raise ValueError(f"sample rate must be positive, got {sample_rate}")
    if pcm.shape[1] == 0:
        return -math.inf

    oversampled = resample(pcm, sample_rate, sample_rate * TRUE_PEAK_OVERSAMPLE)
    return amplitude_to_dbfs(float(np.abs(oversampled).max()))


def normalise(pcm: Pcm, sample_rate: int) -> tuple[Pcm, float]:
    """Normalise to the loudness target and limit true peaks.

    A single linear gain is applied, chosen as the smaller of the gain that
    reaches ``TARGET_LUFS`` and the gain that leaves the true peak at
    ``TRUE_PEAK_CEILING_DBTP``. Trading loudness for headroom this way is the
    EBU R128 resolution when the two cannot both be met, and keeps the operation
    linear: no dynamics processing distorts the signal the transcriber sees, and
    the display copy is recoverable exactly by undoing the gain.

    Digital silence has no defined loudness, so it is returned unchanged.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        The normalised PCM and the gain applied, in dB.

    Raises:
        ValueError: When ``pcm`` is not planar or ``sample_rate`` is not positive.
    """
    loudness = integrated_lufs(pcm, sample_rate)
    if not math.isfinite(loudness):
        return pcm, 0.0

    peak_dbtp = true_peak_dbtp(pcm, sample_rate)
    gain_db = TARGET_LUFS - loudness
    if math.isfinite(peak_dbtp):
        gain_db = min(gain_db, TRUE_PEAK_CEILING_DBTP - peak_dbtp)

    scaled = (pcm * np.float32(dbfs_to_amplitude(gain_db))).astype(np.float32)
    return scaled, gain_db


def detect_edge_silence(pcm: Pcm, sample_rate: int) -> tuple[float, float]:
    """Measure leading and trailing silence without trimming it.

    Trimming would desynchronise user playback, so the spans are reported only.
    A span counts as silence when every channel stays below
    ``SILENCE_FLOOR_DBFS`` for longer than ``SILENCE_MIN_SPAN_S``; shorter runs
    report ``0.0``. An entirely silent signal is reported as leading silence, so
    that the two spans never describe the same samples twice.

    Args:
        pcm: Planar float32 PCM.
        sample_rate: Sample rate in Hz.

    Returns:
        Leading and trailing silence, in seconds.

    Raises:
        ValueError: When ``pcm`` is not planar or ``sample_rate`` is not positive.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    if sample_rate <= 0:
        raise ValueError(f"sample rate must be positive, got {sample_rate}")

    samples = pcm.shape[1]
    if samples == 0:
        return 0.0, 0.0

    floor = dbfs_to_amplitude(SILENCE_FLOOR_DBFS)
    sounding = np.flatnonzero(np.abs(pcm).max(axis=0) >= floor)

    if sounding.size == 0:
        leading, trailing = samples, 0
    else:
        leading = int(sounding[0])
        trailing = samples - 1 - int(sounding[-1])

    return _reportable(leading, sample_rate), _reportable(trailing, sample_rate)


def _reportable(span_samples: int, sample_rate: int) -> float:
    """Return a silence span in seconds, or ``0.0`` when it is too short to report.

    Args:
        span_samples: Length of the sub-floor run, in samples.
        sample_rate: Sample rate in Hz.

    Returns:
        The span in seconds when it exceeds ``SILENCE_MIN_SPAN_S``, else ``0.0``.
    """
    seconds = span_samples / sample_rate
    return seconds if seconds > SILENCE_MIN_SPAN_S else 0.0
