"""Container detection by magic bytes — ARCHITECTURE.md Section 1.3, step 1.

The file extension and the browser-supplied MIME type are never trusted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

#: MP3 frame-sync bytes accepted as evidence of an MPEG audio stream.
MP3_FRAME_SYNC: Final[tuple[bytes, ...]] = (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa", b"\xff\xf2")

#: Bytes that begin an ID3v2 tag.
ID3_MAGIC: Final[bytes] = b"ID3"

#: RIFF/WAVE magic; the four length bytes between them are skipped.
RIFF_MAGIC: Final[bytes] = b"RIFF"
WAVE_MAGIC: Final[bytes] = b"WAVE"

#: How many leading bytes are inspected when sniffing.
SNIFF_BYTES: Final[int] = 4096

SourceFormat = Literal["mp3", "wav"]


def sniff_bytes(head: bytes) -> SourceFormat:
    """Identify the container from the first bytes of a file.

    Args:
        head: At least ``SNIFF_BYTES`` leading bytes, or the whole file if smaller.

    Returns:
        The detected format.

    Raises:
        AudioSheetError: ``E_INGEST_FORMAT`` when the bytes are neither MP3 nor WAV.
        NotImplementedError: Phase 1 (ARCHITECTURE.md Section 5.3).
    """
    raise NotImplementedError("S0 container sniffing lands in Phase 1")


def sniff_file(path: Path) -> SourceFormat:
    """Identify the container of a file on disk.

    Args:
        path: The audio file.

    Returns:
        The detected format.

    Raises:
        AudioSheetError: ``E_INGEST_FORMAT`` when the file is not MP3 or WAV.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("S0 container sniffing lands in Phase 1")
