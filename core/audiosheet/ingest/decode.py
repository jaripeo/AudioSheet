"""Decoding and the S0 output payload — ARCHITECTURE.md Section 1.3.

MP3 decoding strips the encoder delay reported in the LAME/Xing header, falling
back to ``MP3_FALLBACK_TRIM_SAMPLES`` so that every later timestamp stays aligned
to the audio the user hears.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, cast

import numpy as np
import numpy.typing as npt

from audiosheet.ingest.sniff import SourceFormat
from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode
from audiosheet.pipeline.stage import StageContext, StageWarning

#: Planar float32 PCM, shaped (channels, samples).
Pcm = npt.NDArray[np.float32]

#: Bytes in an ID3v2 header, and in the optional footer of the same size.
ID3_HEADER_BYTES: Final[int] = 10

#: Bit in the ID3v2 flags byte that declares a trailing footer.
ID3_FOOTER_FLAG: Final[int] = 0x10

#: MPEG version field values: 2.5, reserved, 2, 1.
MPEG_VERSION_1: Final[int] = 0b11
MPEG_VERSION_RESERVED: Final[int] = 0b01

#: Layer field value for Layer III, the only layer that carries a Xing tag.
MPEG_LAYER_III: Final[int] = 0b01

#: Channel-mode field value for single-channel audio.
MPEG_MODE_MONO: Final[int] = 0b11

#: Side-information bytes between the frame header and the Xing tag, keyed by
#: ``(is_mpeg1, is_mono)``.
SIDE_INFO_BYTES: Final[dict[tuple[bool, bool], int]] = {
    (True, True): 17,
    (True, False): 32,
    (False, True): 9,
    (False, False): 17,
}

#: Magic that opens a VBR/CBR info frame. ``Info`` is the constant-bitrate spelling.
XING_MAGIC: Final[tuple[bytes, ...]] = (b"Xing", b"Info")

#: Encoder signatures that write the LAME extension fields.
LAME_ENCODERS: Final[tuple[bytes, ...]] = (b"LAME", b"Lavc", b"Lavf")

#: Bytes in the encoder short-version string that opens the LAME extension.
LAME_VERSION_BYTES: Final[int] = 9

#: Offset of the packed delay/padding pair from the start of the LAME extension.
LAME_DELAY_OFFSET: Final[int] = 21

#: Widest delay or padding the 12-bit LAME fields can express.
LAME_MAX_DELAY: Final[int] = 0xFFF


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

        The array is mapped read-only: a variant is written once by S0 and read
        by every downstream stage, and no stage may mutate its input (INV-3).

        Returns:
            Planar float32 PCM shaped ``(channels, samples)``.

        Raises:
            AudioSheetError: ``E_CACHE_CORRUPT`` when the backing file does not
                hold planar float32 PCM of the declared channel count.
            OSError: When the backing file cannot be read.
        """
        array = np.load(self.path, mmap_mode="r")
        if array.dtype != np.float32 or array.ndim != 2 or array.shape[0] != self.channels:
            raise AudioSheetError(
                ErrorCode.E_CACHE_CORRUPT,
                f"PCM variant '{self.name}' is not {self.channels}-channel planar float32",
                detail={
                    "path": str(self.path),
                    "dtype": str(array.dtype),
                    "shape": list(array.shape),
                },
            )
        return cast("Pcm", array)


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
        NotImplementedError: Phase 1 — blocked on the libsndfile/soxr/pyloudnorm
            dependencies and the vendored ffmpeg binary.
    """
    raise NotImplementedError("S0 decoding lands in Phase 1")


def id3v2_length(head: bytes) -> int:
    """Return the byte length of a leading ID3v2 tag, or ``0`` when absent.

    The size is stored as four synchsafe bytes — seven significant bits each, so
    that a size can never contain a false frame sync.

    Args:
        head: Leading bytes of an MP3 file.

    Returns:
        Offset of the first MPEG frame.
    """
    if len(head) < ID3_HEADER_BYTES or not head.startswith(b"ID3"):
        return 0
    size = 0
    for byte in head[6:ID3_HEADER_BYTES]:
        size = (size << 7) | (byte & 0x7F)
    total = ID3_HEADER_BYTES + size
    if head[5] & ID3_FOOTER_FLAG:
        total += ID3_HEADER_BYTES
    return total


def mpeg_frame_shape(header: bytes) -> tuple[bool, bool] | None:
    """Return ``(is_mpeg1, is_mono)`` for a Layer III frame header.

    Only the fields that place the Xing tag are decoded. A header whose version,
    layer, bitrate or sample-rate field is a reserved value is not a frame.

    Args:
        header: At least four bytes starting at a frame boundary.

    Returns:
        The version and channel-mode pair, or ``None`` when this is not a
        Layer III frame header.
    """
    if len(header) < 4 or header[0] != 0xFF or (header[1] & 0xE0) != 0xE0:
        return None
    version = (header[1] >> 3) & 0b11
    layer = (header[1] >> 1) & 0b11
    if version == MPEG_VERSION_RESERVED or layer != MPEG_LAYER_III:
        return None
    if (header[2] >> 4) == 0b1111 or ((header[2] >> 2) & 0b11) == 0b11:
        return None
    is_mono = ((header[3] >> 6) & 0b11) == MPEG_MODE_MONO
    return version == MPEG_VERSION_1, is_mono


def _lame_extension_offset(head: bytes) -> int | None:
    """Return the offset of the LAME extension fields, or ``None`` if absent.

    Args:
        head: Leading bytes of an MP3 file.

    Returns:
        Offset of the nine-byte encoder version string.
    """
    frame = id3v2_length(head)
    shape = mpeg_frame_shape(head[frame : frame + 4])
    if shape is None:
        return None
    xing = frame + 4 + SIDE_INFO_BYTES[shape]
    if head[xing : xing + 4] not in XING_MAGIC:
        return None

    raw_flags = head[xing + 4 : xing + 8]
    if len(raw_flags) < 4:
        return None
    flags = int.from_bytes(raw_flags, "big")
    cursor = xing + 8
    for bit, width in ((0x1, 4), (0x2, 4), (0x4, 100), (0x8, 4)):
        if flags & bit:
            cursor += width

    encoder = head[cursor : cursor + LAME_VERSION_BYTES]
    if not encoder.startswith(LAME_ENCODERS):
        return None
    return cursor


def lame_delay_and_padding(head: bytes) -> tuple[int, int] | None:
    """Return the encoder delay and padding from a LAME/Xing header.

    Both are packed into three bytes as two twelve-bit fields: the samples the
    encoder prepended, and the samples it appended to fill the final frame.

    Args:
        head: Leading bytes of an MP3 file.

    Returns:
        ``(delay, padding)`` in samples, or ``None`` when no header is present.
    """
    offset = _lame_extension_offset(head)
    if offset is None:
        return None
    packed = head[offset + LAME_DELAY_OFFSET : offset + LAME_DELAY_OFFSET + 3]
    if len(packed) < 3:
        return None
    value = int.from_bytes(packed, "big")
    return value >> 12, value & LAME_MAX_DELAY


def lame_encoder_delay(head: bytes) -> int | None:
    """Return the encoder delay from a LAME/Xing header, or ``None`` if absent.

    Args:
        head: Leading bytes of an MP3 file.

    Returns:
        Delay in samples, or ``None`` when no header is present.
    """
    pair = lame_delay_and_padding(head)
    return None if pair is None else pair[0]
