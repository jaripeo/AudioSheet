"""Decoding and the S0 output payload — ARCHITECTURE.md Section 1.3.

MP3 decoding strips the encoder delay reported in the LAME/Xing header, falling
back to ``MP3_FALLBACK_TRIM_SAMPLES`` so that every later timestamp stays aligned
to the audio the user hears.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import numpy.typing as npt

from audiosheet.ingest.sniff import SourceFormat
from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.stage import StageContext, StageWarning

#: Planar float32 PCM, shaped (channels, samples).
Pcm = npt.NDArray[np.float32]


@dataclass(frozen=True)
class PcmVariant:
    """One resampled view of the input audio.

    Attributes:
        name: Variant key from ``PCM_VARIANTS``.
        sample_rate: Sample rate in Hz.
        channels: Channel count.
        path: Memory-mapped ``.npy`` backing file in the project cache.
    """

    name: str
    sample_rate: int
    channels: int
    path: Path

    def load(self) -> Pcm:
        """Memory-map the backing file.

        Returns:
            Planar float32 PCM shaped ``(channels, samples)``.

        Raises:
            NotImplementedError: Phase 1.
        """
        raise NotImplementedError("PCM memory-mapping lands in Phase 1")


@dataclass(frozen=True)
class AudioBundle:
    """The S0 output — ARCHITECTURE.md Section 1.3, step 6.

    Attributes:
        sha256: Digest of the original file bytes.
        filename: Original file name, recorded in ScoreDocument.source.
        source_format: Detected container.
        duration_s: Duration of the decoded audio.
        source_sample_rate: Sample rate of the source file.
        channels: Channel count after any downmix.
        variants: Resampled views, keyed by variant name.
        gain_db: Loudness-normalisation gain applied.
        trim_samples: Encoder-delay samples stripped.
        leading_silence_s: Detected, but deliberately not trimmed.
        warnings: Non-fatal conditions raised during ingestion.
    """

    sha256: str
    filename: str
    source_format: SourceFormat
    duration_s: float
    source_sample_rate: int
    channels: int
    variants: dict[str, PcmVariant]
    gain_db: float
    trim_samples: int
    leading_silence_s: float
    warnings: list[StageWarning] = field(default_factory=list)

    def content_hash(self) -> str:
        """Return a stable fingerprint for cache keying (see ``Fingerprintable``).

        The audio digest and the ingestion parameters fully determine the bundle,
        so the large PCM payloads are never hashed.
        """
        return blake3_hex(
            self.sha256.encode("utf-8"),
            f"{self.trim_samples}:{self.gain_db}:{self.channels}".encode(),
        )


def decode(path: Path, ctx: StageContext) -> AudioBundle:
    """Decode, validate, resample and loudness-normalise an input file.

    Args:
        path: The audio file to ingest.
        ctx: Ambient stage services.

    Returns:
        The populated ``AudioBundle``.

    Raises:
        AudioSheetError: ``E_INGEST_FORMAT``, ``E_INGEST_LIMIT`` or
            ``E_INGEST_DECODE`` per Section 1.3.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("S0 decoding lands in Phase 1")


def lame_encoder_delay(head: bytes) -> int | None:
    """Return the encoder delay from a LAME/Xing header, or ``None`` if absent.

    Args:
        head: Leading bytes of an MP3 file.

    Returns:
        Delay in samples, or ``None`` when no header is present.

    Raises:
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("LAME/Xing header parsing lands in Phase 1")
