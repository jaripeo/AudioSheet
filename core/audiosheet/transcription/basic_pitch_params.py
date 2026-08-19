"""basic-pitch decoding parameters — ARCHITECTURE.md Section 1.6.1 (Normative).

Per-stem overrides. ``min_freq_hz`` for guitar is D2 rather than E2 so drop-D
tunings are admitted; ``max_freq_hz`` 1318.5 Hz is E6, fret 24 on the high E.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class BasicPitchParams:
    """Decoding thresholds for one stem."""

    onset_threshold: float
    frame_threshold: float
    min_note_len_ms: float
    min_freq_hz: float | None
    max_freq_hz: float | None
    melodia_trick: bool
    multiple_pitch_bends: bool


#: Applied to any stem without an explicit override.
DEFAULT_PARAMS: Final[BasicPitchParams] = BasicPitchParams(
    onset_threshold=0.50,
    frame_threshold=0.30,
    min_note_len_ms=127.70,
    min_freq_hz=None,
    max_freq_hz=None,
    melodia_trick=True,
    multiple_pitch_bends=False,
)

#: Per-stem overrides from the Section 1.6.1 table.
STEM_PARAMS: Final[dict[str, BasicPitchParams]] = {
    "piano": BasicPitchParams(0.50, 0.30, 90.00, 27.5, 4186.0, True, False),
    "guitar": BasicPitchParams(0.45, 0.28, 80.00, 73.4, 1318.5, True, False),
    "other": BasicPitchParams(0.55, 0.35, 127.70, 55.0, 2093.0, True, False),
}

#: Lowest and highest MIDI note the note posteriorgram spans (88 bins, A0..C8).
NOTE_RANGE_MIDI: Final[tuple[int, int]] = (21, 108)

#: Pitch-contour bins per semitone.
CONTOUR_BINS_PER_SEMITONE: Final[int] = 3


def params_for(stem: str) -> BasicPitchParams:
    """Return the decoding parameters for ``stem``.

    Args:
        stem: Stem name.

    Returns:
        The stem's overrides, or ``DEFAULT_PARAMS``.
    """
    return STEM_PARAMS.get(stem, DEFAULT_PARAMS)
