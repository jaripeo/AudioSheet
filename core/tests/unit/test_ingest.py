"""S0 ingestion — limits (Section 1.3 step 2) and container sniffing (step 1).

Gate G1 also lands sample-accurate alignment assertions in this file once
decoding exists; for now it covers the two pieces that have no audio behind them.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pytest

from audiosheet.config import limits
from audiosheet.config.constants import (
    MP3_FALLBACK_TRIM_SAMPLES,
    SILENCE_FLOOR_DBFS,
    SILENCE_MIN_SPAN_S,
)
from audiosheet.ingest import decode
from audiosheet.ingest.loudness import dbfs_to_amplitude, detect_edge_silence
from audiosheet.ingest.resample import downmix
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


# ---------------------------------------------------------------------------
# ID3v2 framing — ARCHITECTURE.md Section 1.3, step 3
# ---------------------------------------------------------------------------


def synchsafe(size: int) -> bytes:
    """Encode ``size`` as the four seven-bit bytes of an ID3v2 length field."""
    return bytes((size >> shift) & 0x7F for shift in (21, 14, 7, 0))


def id3v2_tag(size: int, *, footer: bool = False) -> bytes:
    """Return an ID3v2.3 tag of ``size`` payload bytes, optionally with a footer."""
    flags = decode.ID3_FOOTER_FLAG if footer else 0x00
    header = b"ID3" + b"\x03\x00" + bytes([flags]) + synchsafe(size)
    return header + b"\x00" * size


def test_no_id3_tag_means_the_frame_starts_at_zero() -> None:
    assert decode.id3v2_length(b"\xff\xfb\x90\x64" + b"\x00" * 64) == 0


def test_an_id3_tag_is_measured_past_its_header() -> None:
    assert decode.id3v2_length(id3v2_tag(100)) == 110


def test_the_id3_size_field_is_synchsafe() -> None:
    """Seven significant bits per byte: 0x7F 0x7F is 16383, not 32639."""
    header = b"ID3" + b"\x03\x00\x00" + b"\x00\x00\x7f\x7f"
    assert decode.id3v2_length(header) == 10 + 16383


def test_an_id3_footer_is_counted() -> None:
    assert decode.id3v2_length(id3v2_tag(100, footer=True)) == 120


def test_a_truncated_id3_header_is_not_a_tag() -> None:
    assert decode.id3v2_length(b"ID3\x03") == 0


# ---------------------------------------------------------------------------
# MPEG frame headers
# ---------------------------------------------------------------------------


def mpeg_header(*, mpeg1: bool = True, mono: bool = False, layer: int = 0b01) -> bytes:
    """Return a four-byte Layer III frame header with a valid bitrate/rate pair."""
    version = 0b11 if mpeg1 else 0b10
    byte1 = 0xE0 | (version << 3) | (layer << 1) | 0b1
    mode = 0b11 if mono else 0b00
    return bytes([0xFF, byte1, 0x90, mode << 6])


def test_an_mpeg1_stereo_header_is_recognised() -> None:
    assert decode.mpeg_frame_shape(mpeg_header()) == (True, False)


def test_an_mpeg1_mono_header_is_recognised() -> None:
    assert decode.mpeg_frame_shape(mpeg_header(mono=True)) == (True, True)


def test_an_mpeg2_header_is_recognised() -> None:
    assert decode.mpeg_frame_shape(mpeg_header(mpeg1=False)) == (False, False)


@pytest.mark.parametrize(
    ("name", "header"),
    [
        ("too short", b"\xff\xfb\x90"),
        ("no sync", b"\x00\x00\x00\x00"),
        ("partial sync", b"\xff\x0b\x90\x00"),
        ("reserved version", bytes([0xFF, 0xE0 | (0b01 << 3) | (0b01 << 1) | 1, 0x90, 0x00])),
        ("layer II", mpeg_header(layer=0b10)),
        ("layer I", mpeg_header(layer=0b11)),
        ("reserved layer", mpeg_header(layer=0b00)),
        ("invalid bitrate index", bytes([0xFF, 0xFB, 0xF0, 0x00])),
        ("reserved sample rate", bytes([0xFF, 0xFB, 0x9C, 0x00])),
    ],
)
def test_a_malformed_frame_header_is_rejected(name: str, header: bytes) -> None:
    assert decode.mpeg_frame_shape(header) is None, name


def test_the_side_info_table_covers_every_shape() -> None:
    """Xing sits past the side information, whose size depends on the shape."""
    assert decode.SIDE_INFO_BYTES == {
        (True, True): 17,
        (True, False): 32,
        (False, True): 9,
        (False, False): 17,
    }


# ---------------------------------------------------------------------------
# LAME/Xing encoder delay — ARCHITECTURE.md Section 1.3, step 3
# ---------------------------------------------------------------------------


def xing_frame(
    delay: int,
    padding: int,
    *,
    magic: bytes = b"Xing",
    flags: int = 0x0F,
    encoder: bytes = b"LAME3.100",
    mpeg1: bool = True,
    mono: bool = False,
    id3_size: int | None = None,
) -> bytes:
    """Return an MP3 head whose first frame carries a LAME/Xing tag."""
    body = bytearray()
    if id3_size is not None:
        body += id3v2_tag(id3_size)
    body += mpeg_header(mpeg1=mpeg1, mono=mono)
    body += b"\x00" * decode.SIDE_INFO_BYTES[(mpeg1, mono)]
    body += magic
    body += flags.to_bytes(4, "big")
    if flags & 0x1:
        body += (1000).to_bytes(4, "big")  # frame count
    if flags & 0x2:
        body += (200000).to_bytes(4, "big")  # byte count
    if flags & 0x4:
        body += bytes(range(100))  # seek table
    if flags & 0x8:
        body += (78).to_bytes(4, "big")  # VBR quality
    body += encoder
    body += b"\x00" * (decode.LAME_DELAY_OFFSET - len(encoder))
    body += (((delay & 0xFFF) << 12) | (padding & 0xFFF)).to_bytes(3, "big")
    body += b"\x00" * 64
    return bytes(body)


def test_a_typical_lame_delay_is_read() -> None:
    assert decode.lame_delay_and_padding(xing_frame(576, 1800)) == (576, 1800)
    assert decode.lame_encoder_delay(xing_frame(576, 1800)) == 576


@pytest.mark.parametrize(
    ("delay", "padding"),
    [(0, 0), (1, 1), (576, 1800), (1105, 0), (4095, 4095), (2048, 4095)],
)
def test_delay_and_padding_round_trip(delay: int, padding: int) -> None:
    assert decode.lame_delay_and_padding(xing_frame(delay, padding)) == (delay, padding)


def test_the_info_spelling_is_read_like_xing() -> None:
    """A constant-bitrate file writes 'Info' where a VBR file writes 'Xing'."""
    assert decode.lame_encoder_delay(xing_frame(576, 1800, magic=b"Info")) == 576


@pytest.mark.parametrize("encoder", [b"LAME3.100", b"LAME3.99r", b"Lavc58.13", b"Lavf58.29"])
def test_known_encoder_signatures_are_accepted(encoder: bytes) -> None:
    assert decode.lame_encoder_delay(xing_frame(576, 1800, encoder=encoder)) == 576


@pytest.mark.parametrize("flags", [0x00, 0x01, 0x03, 0x07, 0x0B, 0x0F])
def test_the_optional_xing_fields_are_skipped_by_flag(flags: int) -> None:
    """The LAME extension sits after whichever optional fields the flags declare."""
    assert decode.lame_encoder_delay(xing_frame(576, 1800, flags=flags)) == 576


@pytest.mark.parametrize(
    ("mpeg1", "mono"),
    [(True, False), (True, True), (False, False), (False, True)],
)
def test_the_tag_is_found_for_every_frame_shape(mpeg1: bool, mono: bool) -> None:
    head = xing_frame(576, 1800, mpeg1=mpeg1, mono=mono)
    assert decode.lame_encoder_delay(head) == 576


def test_the_tag_is_found_behind_an_id3_tag() -> None:
    assert decode.lame_encoder_delay(xing_frame(576, 1800, id3_size=2048)) == 576


@pytest.mark.parametrize(
    ("name", "head"),
    [
        ("empty", b""),
        ("no frame", b"\x00" * 512),
        ("frame but no xing", mpeg_header() + b"\x00" * 512),
        ("wrong magic", xing_frame(576, 1800, magic=b"Xong")),
        ("unknown encoder", xing_frame(576, 1800, encoder=b"Shine1.0")),
        ("truncated before the tag", xing_frame(576, 1800)[:40]),
        ("truncated inside the delay field", xing_frame(576, 1800)[:-66]),
    ],
)
def test_a_missing_lame_header_returns_none(name: str, head: bytes) -> None:
    assert decode.lame_delay_and_padding(head) is None, name
    assert decode.lame_encoder_delay(head) is None, name


def test_a_missing_header_is_distinct_from_a_zero_delay() -> None:
    """None means 'fall back to MP3_FALLBACK_TRIM_SAMPLES'; 0 means 'trim nothing'."""
    assert decode.lame_encoder_delay(xing_frame(0, 0)) == 0
    assert decode.lame_encoder_delay(b"\x00" * 512) is None


def test_the_fallback_trim_is_the_normative_value() -> None:
    assert MP3_FALLBACK_TRIM_SAMPLES == 1105


# ---------------------------------------------------------------------------
# PCM variants — ARCHITECTURE.md Section 1.3, steps 4 and 6
# ---------------------------------------------------------------------------


def write_variant(path: Path, pcm: npt.NDArray[Any]) -> None:
    """Persist planar PCM in the ``.npy`` form S0 writes into the cache."""
    np.save(path, pcm)


def test_a_variant_memory_maps_its_backing_file(tmp_path: Path) -> None:
    """Section 4.3: PCM is memory-mapped from cache, never held twice in RAM."""
    path = tmp_path / "pcm_44k_stereo.npy"
    pcm = np.linspace(-1.0, 1.0, 2 * 512, dtype=np.float32).reshape(2, 512)
    write_variant(path, pcm)

    variant = decode.PcmVariant("pcm_44k_stereo", 44100, 2, path)
    loaded = variant.load()

    assert isinstance(loaded, np.memmap)
    assert loaded.dtype == np.float32
    assert loaded.shape == (2, 512)
    np.testing.assert_array_equal(loaded, pcm)


def test_a_loaded_variant_is_read_only(tmp_path: Path) -> None:
    """INV-3: a downstream stage must not be able to mutate a shared input."""
    path = tmp_path / "pcm_16k_mono.npy"
    write_variant(path, np.zeros((1, 256), dtype=np.float32))
    loaded = decode.PcmVariant("pcm_16k_mono", 16000, 1, path).load()
    with pytest.raises(ValueError, match="read-only"):
        loaded[0, 0] = 1.0


@pytest.mark.parametrize(
    ("name", "payload"),
    [
        ("wrong dtype", np.zeros((2, 64), dtype=np.float64)),
        ("wrong channel count", np.zeros((1, 64), dtype=np.float32)),
        ("interleaved, not planar", np.zeros(128, dtype=np.float32)),
        ("three dimensions", np.zeros((2, 4, 8), dtype=np.float32)),
    ],
)
def test_a_corrupt_variant_fails_closed(
    tmp_path: Path, name: str, payload: npt.NDArray[Any]
) -> None:
    path = tmp_path / "variant.npy"
    write_variant(path, payload)
    variant = decode.PcmVariant("pcm_44k_stereo", 44100, 2, path)
    with pytest.raises(AudioSheetError) as excinfo:
        variant.load()
    assert excinfo.value.code is ErrorCode.E_CACHE_CORRUPT, name


def test_a_missing_variant_raises_os_error(tmp_path: Path) -> None:
    """Absence is a system error, not a corrupt-cache verdict."""
    variant = decode.PcmVariant("pcm_44k_stereo", 44100, 2, tmp_path / "gone.npy")
    with pytest.raises(FileNotFoundError):
        variant.load()


# ---------------------------------------------------------------------------
# Downmixing — ARCHITECTURE.md Section 1.3, step 2
# ---------------------------------------------------------------------------


def ramp(channels: int, samples: int = 8) -> npt.NDArray[Any]:
    """Return planar PCM whose channel ``c`` is the constant ``c + 1``."""
    return np.stack(
        [np.full(samples, float(c + 1), dtype=np.float32) for c in range(channels)]
    ).astype(np.float32)


def test_stereo_folds_to_mono_with_equal_weights() -> None:
    mono = downmix(ramp(2), 1)
    assert mono.shape == (1, 8)
    np.testing.assert_allclose(mono, 1.5)


def test_the_downmix_output_is_float32() -> None:
    assert downmix(ramp(6), 2).dtype == np.float32


def test_a_five_one_stream_folds_round_robin() -> None:
    """L C Ls carry to the left, R LFE Rs to the right — every weight equal."""
    folded = downmix(ramp(6), 2)
    assert folded.shape == (2, 8)
    np.testing.assert_allclose(folded[0], (1.0 + 3.0 + 5.0) / 3.0)
    np.testing.assert_allclose(folded[1], (2.0 + 4.0 + 6.0) / 3.0)


def test_folding_everything_to_mono_averages_every_channel() -> None:
    np.testing.assert_allclose(downmix(ramp(6), 1), 3.5)


def test_an_unequal_group_still_uses_equal_weights_per_group() -> None:
    """Five channels into two: (1,3,5) and (2,4) — each group's own mean."""
    folded = downmix(ramp(5), 2)
    np.testing.assert_allclose(folded[0], (1.0 + 3.0 + 5.0) / 3.0)
    np.testing.assert_allclose(folded[1], (2.0 + 4.0) / 2.0)


def test_a_no_op_downmix_returns_the_input_unchanged() -> None:
    pcm = ramp(2)
    assert downmix(pcm, 2) is pcm


def test_downmixing_does_not_mutate_the_input() -> None:
    """INV-3: stages return new objects rather than editing their input."""
    pcm = ramp(4)
    before = pcm.copy()
    downmix(pcm, 2)
    np.testing.assert_array_equal(pcm, before)


def test_the_max_channel_limit_is_what_triggers_a_downmix() -> None:
    assert downmix(ramp(6), limits.MAX_CHANNELS).shape[0] == 2


@pytest.mark.parametrize("target", [0, -1, 3, 99])
def test_an_impossible_channel_target_is_rejected(target: int) -> None:
    with pytest.raises(ValueError, match="downmix"):
        downmix(ramp(2), target)


def test_interleaved_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="planar"):
        downmix(np.zeros(64, dtype=np.float32), 1)


# ---------------------------------------------------------------------------
# Edge silence — ARCHITECTURE.md Section 1.3, step 5
# ---------------------------------------------------------------------------

RATE = 1000


def signal(leading_s: float, sounding_s: float, trailing_s: float) -> npt.NDArray[Any]:
    """Return mono PCM: a silent head, a full-scale body, and a silent tail."""
    parts = [
        np.zeros(round(leading_s * RATE), dtype=np.float32),
        np.full(round(sounding_s * RATE), 0.5, dtype=np.float32),
        np.zeros(round(trailing_s * RATE), dtype=np.float32),
    ]
    return np.concatenate(parts).reshape(1, -1)


def test_the_silence_floor_is_the_normative_value() -> None:
    assert SILENCE_FLOOR_DBFS == -60.0
    assert SILENCE_MIN_SPAN_S == 0.250
    assert dbfs_to_amplitude(-60.0) == pytest.approx(0.001)
    assert dbfs_to_amplitude(0.0) == 1.0


def test_leading_and_trailing_silence_are_measured() -> None:
    leading, trailing = detect_edge_silence(signal(1.0, 2.0, 0.5), RATE)
    assert leading == pytest.approx(1.0)
    assert trailing == pytest.approx(0.5)


def test_silence_shorter_than_the_minimum_span_is_not_reported() -> None:
    """Section 1.3: only spans longer than 250 ms count."""
    leading, trailing = detect_edge_silence(signal(0.1, 2.0, 0.2), RATE)
    assert leading == 0.0
    assert trailing == 0.0


def test_the_minimum_span_is_exclusive_at_the_boundary() -> None:
    assert detect_edge_silence(signal(0.250, 1.0, 0.0), RATE)[0] == 0.0
    assert detect_edge_silence(signal(0.251, 1.0, 0.0), RATE)[0] == pytest.approx(0.251)


def test_audio_just_under_the_floor_counts_as_silence() -> None:
    pcm = signal(0.0, 1.0, 0.0)
    pcm[:, : round(0.5 * RATE)] = dbfs_to_amplitude(-61.0)
    assert detect_edge_silence(pcm, RATE)[0] == pytest.approx(0.5)


def test_audio_just_over_the_floor_does_not() -> None:
    pcm = signal(0.0, 1.0, 0.0)
    pcm[:, : round(0.5 * RATE)] = dbfs_to_amplitude(-59.0)
    assert detect_edge_silence(pcm, RATE)[0] == 0.0


def test_silence_is_measured_across_every_channel() -> None:
    """A span is silent only while all channels are below the floor."""
    stereo = np.zeros((2, RATE), dtype=np.float32)
    stereo[0, round(0.4 * RATE) :] = 0.5
    stereo[1, round(0.8 * RATE) :] = 0.5
    assert detect_edge_silence(stereo, RATE)[0] == pytest.approx(0.4)


def test_an_entirely_silent_signal_is_not_counted_twice() -> None:
    silent = np.zeros((1, 2 * RATE), dtype=np.float32)
    assert detect_edge_silence(silent, RATE) == (2.0, 0.0)


def test_a_signal_with_no_silence_reports_nothing() -> None:
    assert detect_edge_silence(signal(0.0, 2.0, 0.0), RATE) == (0.0, 0.0)


def test_silence_detection_does_not_trim(tmp_path: Path) -> None:
    """Trimming would desynchronise playback, so detection is read-only."""
    pcm = signal(1.0, 1.0, 1.0)
    before = pcm.copy()
    detect_edge_silence(pcm, RATE)
    np.testing.assert_array_equal(pcm, before)


def test_an_empty_signal_reports_nothing() -> None:
    assert detect_edge_silence(np.zeros((2, 0), dtype=np.float32), RATE) == (0.0, 0.0)


def test_edge_silence_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="planar"):
        detect_edge_silence(np.zeros(64, dtype=np.float32), RATE)
    with pytest.raises(ValueError, match="sample rate"):
        detect_edge_silence(np.zeros((1, 64), dtype=np.float32), 0)
