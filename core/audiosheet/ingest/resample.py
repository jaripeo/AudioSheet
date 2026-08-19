"""Resampling — ARCHITECTURE.md Section 1.3, step 4.

Resampling happens exactly once, here. No downstream stage may resample.
"""

from __future__ import annotations

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
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("S0 resampling lands in Phase 1")


def downmix(pcm: Pcm, target_channels: int) -> Pcm:
    """Downmix to ``target_channels`` with equal weights.

    Args:
        pcm: Planar float32 PCM shaped ``(channels, samples)``.
        target_channels: Desired channel count.

    Returns:
        Downmixed planar PCM.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("S0 downmixing lands in Phase 1")
