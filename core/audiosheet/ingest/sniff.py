"""Container detection by magic bytes — ARCHITECTURE.md Section 1.3, step 1.

The file extension and the browser-supplied MIME type are never trusted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from audiosheet.pipeline.errors import AudioSheetError, ErrorCode

#: MP3 frame-sync bytes accepted as evidence of an MPEG audio stream.
MP3_FRAME_SYNC: Final[tuple[bytes, ...]] = (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa", b"\xff\xf2")

#: Bytes that begin an ID3v2 tag.
ID3_MAGIC: Final[bytes] = b"ID3"

#: RIFF/WAVE magic; the four length bytes between them are skipped.
RIFF_MAGIC: Final[bytes] = b"RIFF"
WAVE_MAGIC: Final[bytes] = b"WAVE"

#: Offset of ``WAVE`` in a RIFF header: ``RIFF`` + four little-endian size bytes.
WAVE_OFFSET: Final[int] = 8

#: How many leading bytes are inspected when sniffing.
SNIFF_BYTES: Final[int] = 4096

#: Leading bytes quoted back in the ``E_INGEST_FORMAT`` diagnostic.
_DETAIL_BYTES: Final[int] = 16

SourceFormat = Literal["mp3", "wav"]


def _detect(head: bytes) -> SourceFormat | None:
    """Return the container implied by leading bytes, or ``None`` if unrecognised.

    Magic is anchored at offset 0: a frame sync or an ``ID3`` tag found deeper in
    the file is a coincidence, not a container, and accepting it would let any
    binary through.

    Args:
        head: Leading bytes of the file.

    Returns:
        The detected format, or ``None``.
    """
    if head.startswith(ID3_MAGIC) or head.startswith(MP3_FRAME_SYNC):
        return "mp3"
    if head.startswith(RIFF_MAGIC) and head[WAVE_OFFSET : WAVE_OFFSET + 4] == WAVE_MAGIC:
        return "wav"
    return None


def _rejected(head: bytes, detail: dict[str, object]) -> AudioSheetError:
    """Build the ``E_INGEST_FORMAT`` failure for bytes that match no container.

    Args:
        head: The inspected leading bytes.
        detail: Extra structured context merged into the error.

    Returns:
        The error to raise.
    """
    return AudioSheetError(
        ErrorCode.E_INGEST_FORMAT,
        "not an MP3 or WAV container",
        detail={**detail, "leading_bytes": head[:_DETAIL_BYTES].hex()},
    )


def sniff_bytes(head: bytes) -> SourceFormat:
    """Identify the container from the first bytes of a file.

    Args:
        head: At least ``SNIFF_BYTES`` leading bytes, or the whole file if smaller.

    Returns:
        The detected format.

    Raises:
        AudioSheetError: ``E_INGEST_FORMAT`` when the bytes are neither MP3 nor WAV.
    """
    detected = _detect(head)
    if detected is None:
        raise _rejected(head, {})
    return detected


def sniff_file(path: Path) -> SourceFormat:
    """Identify the container of a file on disk.

    Only the first ``SNIFF_BYTES`` bytes are read; the rest of the file is the
    decoder's problem.

    Args:
        path: The audio file.

    Returns:
        The detected format.

    Raises:
        AudioSheetError: ``E_INGEST_FORMAT`` when the file is not MP3 or WAV.
        OSError: When the file cannot be opened or read.
    """
    with path.open("rb") as handle:
        head = handle.read(SNIFF_BYTES)
    detected = _detect(head)
    if detected is None:
        raise _rejected(head, {"path": path.name})
    return detected
