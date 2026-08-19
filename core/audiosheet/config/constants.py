"""Normative global constants — ARCHITECTURE.md Reading Contract and Section 1.

Every value here is normative: it appears in the architecture document as a
hard-coded constant and MUST appear in the codebase exactly once, here.
"""

from __future__ import annotations

from typing import Final

# --- INV-2 (Determinism) ---------------------------------------------------

#: Every source of randomness in the pipeline is seeded from this constant.
AUDIOSHEET_SEED: Final[int] = 20240101

# --- INV-5 (Time is dual-encoded) -----------------------------------------

#: Pulses per quarter note for every tick value in the system.
PPQ: Final[int] = 960

#: Tolerance for the tick <-> seconds round-trip through the tempo map (V-6).
TICK_SECONDS_ROUNDTRIP_TOLERANCE_S: Final[float] = 0.002

# --- S0 ingestion (Section 1.3) ------------------------------------------

#: Rate/channel variants produced exactly once by S0, keyed by variant name.
PCM_VARIANTS: Final[dict[str, tuple[int, int]]] = {
    "pcm_44k_stereo": (44100, 2),
    "pcm_22k_mono": (22050, 1),
    "pcm_16k_mono": (16000, 1),
}

#: Integrated loudness target (ITU-R BS.1770-4).
TARGET_LUFS: Final[float] = -18.0

#: True-peak ceiling applied after loudness normalisation.
TRUE_PEAK_CEILING_DBTP: Final[float] = -1.0

#: Fallback MP3 encoder-delay trim at 44.1 kHz when no LAME/Xing header exists.
MP3_FALLBACK_TRIM_SAMPLES: Final[int] = 1105

#: Level below which audio counts as silence for leading/trailing detection.
SILENCE_FLOOR_DBFS: Final[float] = -60.0

#: Minimum span of sub-floor audio reported as leading/trailing silence.
SILENCE_MIN_SPAN_S: Final[float] = 0.250

#: Abort ingestion when more than this fraction of the file fails to decode.
MAX_CORRUPT_FRACTION: Final[float] = 0.02

#: Mid-file decode gaps shorter than this are zero-filled rather than fatal.
MAX_ZERO_FILL_GAP_S: Final[float] = 0.500

# --- S3 transcription (Section 1.6) --------------------------------------

#: basic-pitch frame hop, in samples at 22050 Hz.
BASIC_PITCH_HOP_SAMPLES: Final[int] = 256

#: basic-pitch time resolution, recorded in ScoreDocument.diagnostics.stats.
TRANSCRIPTION_FRAME_MS: Final[float] = 11.61

# --- S2 separation (Section 1.5) -----------------------------------------

#: Stems more than this far below the loudest stem are marked absent.
STEM_PRESENCE_GATE_DB: Final[float] = 32.0

# --- Difficulty engine (Section 2) ---------------------------------------

#: Notes below this confidence get DifficultyFlags.confidence_low.
LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.35

#: LRU size for memoised reduce() results (Section 2.4).
DIFFICULTY_MEMO_SIZE: Final[int] = 8
