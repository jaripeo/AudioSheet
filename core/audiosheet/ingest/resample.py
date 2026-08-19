"""Resampling — ARCHITECTURE.md Section 1.3, step 4.

Resampling happens exactly once, here. No downstream stage may resample.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

import numpy as np
import soxr

if TYPE_CHECKING:  # a runtime import would cycle: decode imports this module
    from audiosheet.ingest.decode import Pcm

#: soxr quality preset. Section 1.3 mandates SoX "very high quality" polyphase.
SOXR_QUALITY: Final[str] = "VHQ"


def resample(pcm: Pcm, source_rate: int, target_rate: int) -> Pcm:
    """Resample planar PCM with a polyphase, SoX-quality (VHQ) filter.

    soxr works on interleaved frames, so the planar input is transposed in and
    out. A no-op rate change returns the input untouched (INV-3).

    Args:
        pcm: Planar float32 PCM shaped ``(channels, samples)``.
        source_rate: Input sample rate in Hz.
        target_rate: Output sample rate in Hz.

    Returns:
        Resampled planar PCM shaped ``(channels, resampled_samples)``.

    Raises:
        ValueError: When ``pcm`` is not planar or either rate is not positive.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    if source_rate <= 0 or target_rate <= 0:
        raise ValueError(f"sample rates must be positive, got {source_rate} -> {target_rate}")
    if source_rate == target_rate:
        return pcm

    interleaved = np.ascontiguousarray(pcm.T, dtype=np.float32)
    resampled = soxr.resample(interleaved, source_rate, target_rate, quality=SOXR_QUALITY)
    return np.ascontiguousarray(resampled.T, dtype=np.float32)


def downmix(pcm: Pcm, target_channels: int) -> Pcm:
    """Downmix to ``target_channels`` with equal weights.

    Source channels are assigned to output channels round-robin and each group
    is averaged, so a 5.1 stream (L R C LFE Ls Rs) folds to ``(L C Ls)`` and
    ``(R LFE Rs)`` rather than to two unrelated halves. Every contributing
    channel carries the same weight, per Section 1.3 step 2.

    The input is never modified (INV-3); a request for the channel count the
    input already has returns it unchanged.

    Args:
        pcm: Planar float32 PCM shaped ``(channels, samples)``.
        target_channels: Desired channel count; at most ``pcm.shape[0]``.

    Returns:
        Downmixed planar PCM shaped ``(target_channels, samples)``.

    Raises:
        ValueError: When ``pcm`` is not planar, or ``target_channels`` is not in
            ``1..pcm.shape[0]``.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    channels = pcm.shape[0]
    if not 1 <= target_channels <= channels:
        raise ValueError(f"cannot downmix {channels} channels to {target_channels}")
    if target_channels == channels:
        return pcm

    mixed = np.empty((target_channels, pcm.shape[1]), dtype=np.float32)
    for out in range(target_channels):
        mixed[out] = pcm[out::target_channels].mean(axis=0, dtype=np.float64)
    return mixed


def to_channels(pcm: Pcm, target_channels: int) -> Pcm:
    """Conform PCM to ``target_channels``, folding down or duplicating up.

    Folding down averages with equal weights (see ``downmix``). Folding up
    repeats source channels cyclically, so a mono source fills both sides of the
    stereo variant rather than leaving one silent.

    Args:
        pcm: Planar float32 PCM shaped ``(channels, samples)``.
        target_channels: Desired channel count.

    Returns:
        Planar float32 PCM shaped ``(target_channels, samples)``.

    Raises:
        ValueError: When ``pcm`` is not planar or ``target_channels`` is not positive.
    """
    if pcm.ndim != 2:
        raise ValueError(f"expected planar PCM shaped (channels, samples), got {pcm.shape}")
    if target_channels < 1:
        raise ValueError(f"channel count must be positive, got {target_channels}")

    channels = pcm.shape[0]
    if target_channels == channels:
        return pcm
    if target_channels < channels:
        return downmix(pcm, target_channels)
    return np.ascontiguousarray(pcm[np.arange(target_channels) % channels], dtype=np.float32)
