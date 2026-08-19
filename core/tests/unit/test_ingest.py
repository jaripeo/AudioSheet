"""S0 ingestion — limits (Section 1.3 step 2) and container sniffing (step 1).

Gate G1 also lands sample-accurate alignment assertions in this file once
decoding exists; for now it covers the two pieces that have no audio behind them.
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from audiosheet.config import limits
from audiosheet.ingest.sniff import (
    ID3_MAGIC,
    MP3_FRAME_SYNC,
    RIFF_MAGIC,
    SNIFF_BYTES,
    WAVE_MAGIC,
    WAVE_OFFSET,
    sniff_bytes,
    sniff_file,
)
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode

#: The frame syncs ARCHITECTURE.md Section 1.3 enumerates by name.
NORMATIVE_FRAME_SYNC = (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa")


def wav_header(riff_size: int = 36, tail: bytes = b"fmt ") -> bytes:
    """Return a RIFF/WAVE header with the given declared size and following chunk."""
    return RIFF_MAGIC + struct.pack("<I", riff_size) + WAVE_MAGIC + tail


def id3_header(payload: bytes = b"") -> bytes:
    """Return a minimal ID3v2.3 tag header followed by ``payload``."""
    return ID3_MAGIC + b"\x03\x00\x00" + b"\x00\x00\x00\x00" + payload


# ---------------------------------------------------------------------------
# Limits — ARCHITECTURE.md Section 1.3, step 2 (Normative)
# ---------------------------------------------------------------------------


def test_limits_are_the_normative_values() -> None:
    assert limits.MAX_FILE_SIZE_BYTES == 120 * 1024 * 1024
    assert limits.MAX_DURATION_S == 600.0
    assert limits.MIN_DURATION_S == 1.0
    assert limits.MAX_CHANNELS == 2


def test_limits_have_the_declared_types() -> None:
    """Sizes and channel counts are exact integers; durations are seconds."""
    assert isinstance(limits.MAX_FILE_SIZE_BYTES, int)
    assert isinstance(limits.MAX_CHANNELS, int)
    assert isinstance(limits.MAX_DURATION_S, float)
    assert isinstance(limits.MIN_DURATION_S, float)


def test_the_duration_window_is_non_empty() -> None:
    assert 0.0 < limits.MIN_DURATION_S < limits.MAX_DURATION_S


def test_the_stage_memory_ceiling_matches_section_4_3() -> None:
    assert limits.MAX_STAGE_MEMORY_BYTES == 4 * 1024 * 1024 * 1024


# ---------------------------------------------------------------------------
# Sniffing — ARCHITECTURE.md Section 1.3, step 1
# ---------------------------------------------------------------------------


def test_the_normative_frame_syncs_are_all_declared() -> None:
    """Section 1.3 names 0xFFFB / 0xFFF3 / 0xFFFA explicitly."""
    assert set(NORMATIVE_FRAME_SYNC) <= set(MP3_FRAME_SYNC)


@pytest.mark.parametrize("sync", MP3_FRAME_SYNC)
def test_a_frame_sync_at_offset_zero_is_mp3(sync: bytes) -> None:
    assert sniff_bytes(sync + b"\x90\x64" + b"\x00" * 100) == "mp3"


def test_an_id3_tag_is_mp3() -> None:
    assert sniff_bytes(id3_header(b"\x00" * 64)) == "mp3"


def test_a_riff_wave_header_is_wav() -> None:
    assert sniff_bytes(wav_header()) == "wav"


def test_the_riff_size_field_is_not_inspected() -> None:
    """Only RIFF and WAVE are magic; the four bytes between them are a length."""
    assert sniff_bytes(wav_header(riff_size=0)) == "wav"
    assert sniff_bytes(wav_header(riff_size=0xFFFFFFFF)) == "wav"


def test_a_bare_riff_wave_with_no_chunks_is_still_wav() -> None:
    assert sniff_bytes(wav_header(tail=b"")) == "wav"


@pytest.mark.parametrize(
    ("name", "head"),
    [
        ("empty", b""),
        ("one byte", b"\xff"),
        ("truncated frame sync", b"\xff"),
        ("truncated riff", RIFF_MAGIC),
        ("riff without wave", RIFF_MAGIC + struct.pack("<I", 36) + b"AVI "),
        ("riff truncated before wave", RIFF_MAGIC + struct.pack("<I", 36) + b"WAV"),
        ("wave without riff", b"XXXX" + struct.pack("<I", 36) + WAVE_MAGIC),
        ("invalid sync 0xFFFF", b"\xff\xff\x90\x64"),
        ("invalid sync 0xFFE0", b"\xff\xe0\x90\x64"),
        ("plain text", b"this is not audio at all, not even a little bit"),
        ("ogg", b"OggS\x00\x02" + b"\x00" * 32),
        ("flac", b"fLaC\x00\x00\x00\x22"),
        ("mp4", b"\x00\x00\x00\x20ftypM4A "),
        ("zeros", b"\x00" * 512),
    ],
)
def test_unrecognised_bytes_are_rejected(name: str, head: bytes) -> None:
    with pytest.raises(AudioSheetError) as excinfo:
        sniff_bytes(head)
    assert excinfo.value.code is ErrorCode.E_INGEST_FORMAT, name


def test_magic_deeper_in_the_file_is_not_a_container() -> None:
    """Anchored at offset 0: a coincidental sync inside a payload proves nothing."""
    for magic in (ID3_MAGIC, RIFF_MAGIC + struct.pack("<I", 36) + WAVE_MAGIC, *MP3_FRAME_SYNC):
        with pytest.raises(AudioSheetError) as excinfo:
            sniff_bytes(b"\x00" * 8 + magic + b"\x00" * 64)
        assert excinfo.value.code is ErrorCode.E_INGEST_FORMAT


def test_wave_at_the_wrong_offset_is_rejected() -> None:
    with pytest.raises(AudioSheetError) as excinfo:
        sniff_bytes(RIFF_MAGIC + struct.pack("<I", 36) + b"\x00" + WAVE_MAGIC)
    assert excinfo.value.code is ErrorCode.E_INGEST_FORMAT
    assert WAVE_OFFSET == 8


def test_the_rejection_quotes_the_leading_bytes() -> None:
    """The diagnostic carries evidence, and carries it JSON-safely."""
    with pytest.raises(AudioSheetError) as excinfo:
        sniff_bytes(b"\xde\xad\xbe\xef" + b"\x00" * 4096)
    detail = excinfo.value.detail
    assert detail["leading_bytes"] == "deadbeef" + "00" * 12
    assert excinfo.value.as_dict()["code"] == "E_INGEST_FORMAT"


# ---------------------------------------------------------------------------
# Sniffing files on disk
# ---------------------------------------------------------------------------


def test_sniff_file_reads_a_wav(tmp_path: Path) -> None:
    path = tmp_path / "take.wav"
    path.write_bytes(wav_header() + b"\x00" * 1024)
    assert sniff_file(path) == "wav"


def test_sniff_file_reads_an_mp3(tmp_path: Path) -> None:
    path = tmp_path / "take.mp3"
    path.write_bytes(id3_header() + b"\xff\xfb\x90\x64" + b"\x00" * 1024)
    assert sniff_file(path) == "mp3"


def test_the_extension_is_never_trusted(tmp_path: Path) -> None:
    """Section 1.3: sniff by magic bytes, never by extension or supplied MIME."""
    mislabelled_wav = tmp_path / "song.wav"
    mislabelled_wav.write_bytes(b"\xff\xfb\x90\x64" + b"\x00" * 64)
    assert sniff_file(mislabelled_wav) == "mp3"

    mislabelled_mp3 = tmp_path / "song.mp3"
    mislabelled_mp3.write_bytes(wav_header() + b"\x00" * 64)
    assert sniff_file(mislabelled_mp3) == "wav"

    liar = tmp_path / "song.mp3"
    liar.write_bytes(b"definitely not audio")
    with pytest.raises(AudioSheetError) as excinfo:
        sniff_file(liar)
    assert excinfo.value.code is ErrorCode.E_INGEST_FORMAT


def test_an_empty_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "empty.wav"
    path.write_bytes(b"")
    with pytest.raises(AudioSheetError) as excinfo:
        sniff_file(path)
    assert excinfo.value.code is ErrorCode.E_INGEST_FORMAT
    assert excinfo.value.detail["path"] == "empty.wav"


def test_sniff_file_reads_only_the_head(tmp_path: Path) -> None:
    """A 120 MiB upload must not be pulled into RAM to identify its container."""
    path = tmp_path / "big.wav"
    path.write_bytes(wav_header() + b"\x00" * (SNIFF_BYTES * 4))
    assert SNIFF_BYTES == 4096
    assert sniff_file(path) == "wav"


def test_a_missing_file_raises_os_error(tmp_path: Path) -> None:
    """Absence is the caller's bug, not a container-format verdict."""
    with pytest.raises(FileNotFoundError):
        sniff_file(tmp_path / "nope.wav")
