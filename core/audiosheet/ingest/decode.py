"""Decoding and the S0 output payload — ARCHITECTURE.md Section 1.3.

MP3 decoding strips the encoder delay reported in the LAME/Xing header, falling
back to ``MP3_FALLBACK_TRIM_SAMPLES`` so that every later timestamp stays aligned
to the audio the user hears.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, cast

import numpy as np
import numpy.typing as npt
import soundfile

from audiosheet.config.constants import (
    MP3_FALLBACK_TRIM_SAMPLES,
    PCM_VARIANTS,
)
from audiosheet.config.limits import (
    MAX_CHANNELS,
    MAX_DURATION_S,
    MAX_FILE_SIZE_BYTES,
    MIN_DURATION_S,
)
from audiosheet.config.paths import repo_root
from audiosheet.ingest.loudness import detect_edge_silence, normalise
from audiosheet.ingest.resample import resample, to_channels
from audiosheet.ingest.sniff import SourceFormat, sniff_file
from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode, WarningCode
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

#: Stage name under which PCM variants are cached.
STAGE_NAME: Final[str] = "S0.ingest"

#: Environment variable that overrides the vendored ffmpeg binary.
FFMPEG_ENV: Final[str] = "AUDIOSHEET_FFMPEG"

#: Vendored ffmpeg location, relative to the repository root.
FFMPEG_VENDOR_PATH: Final[tuple[str, ...]] = ("vendor", "ffmpeg", "ffmpeg")

#: Flags every ffmpeg invocation carries (Section 1.3, step 3). Input options
#: precede ``-i``; stream selection and encoding follow it.
FFMPEG_INPUT_FLAGS: Final[tuple[str, ...]] = ("-nostdin", "-hide_banner")
FFMPEG_OUTPUT_FLAGS: Final[tuple[str, ...]] = (
    "-vn",
    "-map",
    "0:a:0",
    "-c:a",
    "pcm_f32le",
    "-f",
    "wav",
)

#: Un-normalised 44.1 kHz stereo copy. Section 1.3 step 5 forbids applying the
#: loudness gain to the waveform display, and the normative variant table gives
#: waveform display and Demucs the same row -- so the display gets its own copy.
DISPLAY_VARIANT: Final[str] = "pcm_44k_stereo_display"

#: Bytes read past a leading ID3v2 tag when looking for the LAME/Xing frame.
MP3_HEAD_BYTES: Final[int] = 4096

#: Characters of ffmpeg stderr retained in an E_INGEST_DECODE diagnostic.
FFMPEG_STDERR_CHARS: Final[int] = 2000


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


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file, read in chunks.

    Args:
        path: The file to digest.

    Returns:
        The digest as lowercase hex.

    Raises:
        OSError: When the file cannot be read.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffmpeg_binary() -> Path:
    """Resolve the vendored ffmpeg binary.

    ``AUDIOSHEET_FFMPEG`` overrides the vendored location. The system ``PATH``
    is deliberately not consulted: an arbitrary build would decode differently
    from the one the gates were measured against (INV-2).

    Returns:
        Path to an executable ffmpeg.

    Raises:
        AudioSheetError: ``E_INGEST_DECODE`` when no executable is found.
    """
    override = os.environ.get(FFMPEG_ENV)
    candidate = (
        Path(override).expanduser() if override else repo_root().joinpath(*FFMPEG_VENDOR_PATH)
    )
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise AudioSheetError(
            ErrorCode.E_INGEST_DECODE,
            f"ffmpeg is not available at {candidate}",
            detail={"path": str(candidate), "override": FFMPEG_ENV},
        )
    return candidate


def ffmpeg_command(binary: Path, source: Path, destination: Path) -> list[str]:
    """Build the ffmpeg invocation that decodes ``source`` to a float32 WAV.

    ffmpeg applies the LAME gapless delay and padding itself, so the decoded
    audio is already aligned to what the listener hears; ``trim_samples`` records
    the same figure for provenance rather than driving a second trim.

    Args:
        binary: The ffmpeg executable.
        source: The input audio file.
        destination: Where to write the decoded WAV.

    Returns:
        The argument vector.
    """
    return [
        str(binary),
        *FFMPEG_INPUT_FLAGS,
        "-i",
        str(source),
        *FFMPEG_OUTPUT_FLAGS,
        "-y",
        str(destination),
    ]


def read_pcm(path: Path) -> tuple[Pcm, int]:
    """Read a sound file into planar float32 PCM via libsndfile.

    Args:
        path: A file libsndfile can open.

    Returns:
        Planar float32 PCM shaped ``(channels, samples)``, and the sample rate.

    Raises:
        AudioSheetError: ``E_INGEST_DECODE`` when libsndfile cannot read it.
    """
    try:
        samples, sample_rate = soundfile.read(path, dtype="float32", always_2d=True)
    except soundfile.LibsndfileError as exc:
        raise AudioSheetError(
            ErrorCode.E_INGEST_DECODE,
            f"libsndfile could not decode {path.name}",
            detail={"path": path.name, "error": str(exc)},
        ) from exc
    return np.ascontiguousarray(samples.T, dtype=np.float32), int(sample_rate)


def ffmpeg_decode(path: Path) -> tuple[Pcm, int]:
    """Decode a file through ffmpeg into planar float32 PCM.

    ffmpeg writes a float32 WAV into a temporary directory, which libsndfile
    then reads: a seekable file carries the sample rate and channel count that a
    raw pipe would not.

    Args:
        path: The input audio file.

    Returns:
        Planar float32 PCM shaped ``(channels, samples)``, and the sample rate.

    Raises:
        AudioSheetError: ``E_INGEST_DECODE`` when ffmpeg is missing or fails.
    """
    binary = ffmpeg_binary()
    with tempfile.TemporaryDirectory(prefix="audiosheet-ingest-") as workspace:
        destination = Path(workspace) / "decoded.wav"
        completed = subprocess.run(  # fixed argv, never a shell
            ffmpeg_command(binary, path, destination),
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0 or not destination.is_file():
            stderr = completed.stderr.decode("utf-8", "replace")[-FFMPEG_STDERR_CHARS:]
            raise AudioSheetError(
                ErrorCode.E_INGEST_DECODE,
                f"ffmpeg failed to decode {path.name}",
                detail={
                    "path": path.name,
                    "returncode": completed.returncode,
                    "stderr": stderr,
                },
            )
        return read_pcm(destination)


def mp3_trim_samples(path: Path) -> int:
    """Return the encoder delay recorded for an MP3, for provenance.

    ffmpeg performs the actual trim. This figure lands in
    ``AudioBundle.trim_samples`` so the provenance shows how many samples the
    encoder prepended, falling back to ``MP3_FALLBACK_TRIM_SAMPLES`` when the
    file carries no LAME/Xing header.

    Args:
        path: The MP3 file.

    Returns:
        The encoder delay in samples.

    Raises:
        OSError: When the file cannot be read.
    """
    with path.open("rb") as handle:
        prefix = handle.read(ID3_HEADER_BYTES)
        head = prefix + handle.read(id3v2_length(prefix) + MP3_HEAD_BYTES)
    delay = lame_encoder_delay(head)
    return MP3_FALLBACK_TRIM_SAMPLES if delay is None else delay


def _variant_path(ctx: StageContext, sha256: str, name: str) -> Path:
    """Return the cache path backing one PCM variant.

    Args:
        ctx: Ambient stage services.
        sha256: Digest of the original file bytes.
        name: Variant name.

    Returns:
        The ``.npy`` path inside the stage cache.
    """
    fingerprint = blake3_hex(sha256.encode("utf-8"), name.encode("utf-8"))
    return ctx.cache.blob_path(STAGE_NAME, fingerprint, ".npy")


def write_variant(
    ctx: StageContext,
    sha256: str,
    name: str,
    pcm: Pcm,
    source_rate: int,
    target_rate: int,
    target_channels: int,
) -> PcmVariant:
    """Conform, resample and persist one PCM variant.

    Channels are folded down before resampling and duplicated up afterwards, so
    the resampler never runs over redundant copies of the same signal.

    Args:
        ctx: Ambient stage services.
        sha256: Digest of the original file bytes.
        name: Variant name.
        pcm: Planar float32 PCM at ``source_rate``.
        source_rate: Sample rate of ``pcm``.
        target_rate: Sample rate of the variant.
        target_channels: Channel count of the variant.

    Returns:
        The persisted variant.
    """
    work = pcm
    if target_channels < work.shape[0]:
        work = to_channels(work, target_channels)
    work = resample(work, source_rate, target_rate)
    work = to_channels(work, target_channels)

    path = _variant_path(ctx, sha256, name)
    np.save(path, work)
    return PcmVariant(name=name, sample_rate=target_rate, channels=target_channels, path=path)


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
        OSError: When the input file cannot be read.
    """
    ctx.check_cancelled(STAGE_NAME)
    size_bytes = path.stat().st_size
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise AudioSheetError(
            ErrorCode.E_INGEST_LIMIT,
            f"{path.name} is {size_bytes} bytes; the limit is {MAX_FILE_SIZE_BYTES}",
            detail={"bytes": size_bytes, "limit": MAX_FILE_SIZE_BYTES},
        )

    source_format = sniff_file(path)
    sha256 = sha256_file(path)

    ctx.report_progress(STAGE_NAME, 0.2, "decoding")
    pcm, source_rate = read_pcm(path) if source_format == "wav" else ffmpeg_decode(path)
    ctx.check_cancelled(STAGE_NAME)

    duration_s = pcm.shape[1] / source_rate
    if not MIN_DURATION_S <= duration_s <= MAX_DURATION_S:
        raise AudioSheetError(
            ErrorCode.E_INGEST_LIMIT,
            f"{path.name} is {duration_s:.3f} s; the accepted range is "
            f"{MIN_DURATION_S}-{MAX_DURATION_S} s",
            detail={"duration_s": duration_s, "min_s": MIN_DURATION_S, "max_s": MAX_DURATION_S},
        )

    warnings: list[StageWarning] = []
    source_channels = pcm.shape[0]
    if source_channels > MAX_CHANNELS:
        pcm = to_channels(pcm, MAX_CHANNELS)
        message = f"downmixed {source_channels} channels to {MAX_CHANNELS} with equal weights"
        warnings.append(StageWarning(code=WarningCode.W_INGEST_DOWNMIX, message=message))
        ctx.warn(WarningCode.W_INGEST_DOWNMIX, message)

    trim_samples = mp3_trim_samples(path) if source_format == "mp3" else 0

    ctx.report_progress(STAGE_NAME, 0.5, "normalising")
    normalised, gain_db = normalise(pcm, source_rate)
    leading_silence_s, _ = detect_edge_silence(normalised, source_rate)

    ctx.report_progress(STAGE_NAME, 0.7, "resampling")
    variants: dict[str, PcmVariant] = {}
    for name, (rate, channels) in PCM_VARIANTS.items():
        ctx.check_cancelled(STAGE_NAME)
        variants[name] = write_variant(ctx, sha256, name, normalised, source_rate, rate, channels)

    display_rate, display_channels = PCM_VARIANTS["pcm_44k_stereo"]
    variants[DISPLAY_VARIANT] = write_variant(
        ctx, sha256, DISPLAY_VARIANT, pcm, source_rate, display_rate, display_channels
    )

    return AudioBundle(
        sha256=sha256,
        filename=path.name,
        source_format=source_format,
        duration_s=duration_s,
        source_sample_rate=source_rate,
        channels=pcm.shape[0],
        variants=variants,
        gain_db=gain_db,
        trim_samples=trim_samples,
        leading_silence_s=leading_silence_s,
        warnings=warnings,
    )


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
