"""Resampling — ARCHITECTURE.md Section 1.3, step 4.

Resampling happens exactly once, here. No downstream stage may resample.
"""

from __future__ import annotations

import numpy as np

from audiosheet.ingest.decode import Pcm


def resample(pcm: Pcm, source_rate: int, target_rate: int) -> Pcm:
    """Resample planar PCM with a polyphase, SoX-quality (VHQ) filter.

    Args:
        pcm: Planar float32 PCM shaped ``(channels, samples)``.
        source_rate: Input sample rate in Hz.
        target_rate: Output sample rate in Hz.

    Returns:
        Resampled planar PCM.

    Raises:
        NotImplementedError: Phase 1 — blocked on the ``soxr`` dependency.
    """
    raise NotImplementedError("S0 resampling lands in Phase 1")


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
