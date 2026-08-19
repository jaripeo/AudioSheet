"""S1.5 key and mode estimation — ARCHITECTURE.md Section 1.4.

A global estimate feeds pitch spelling (S5.3) and key simplification
(Section 2.1.6); a windowed pass produces ``key.regions`` so modulations survive.
"""

from __future__ import annotations

from typing import Final

from audiosheet.analysis.beats import BeatTrack
from audiosheet.ingest.decode import AudioBundle
from audiosheet.schema import KeyEstimate

#: Analysis window for the modulation pass, in bars.
KEY_WINDOW_BARS: Final[int] = 16

#: Hop between modulation windows, in bars.
KEY_HOP_BARS: Final[int] = 4


def estimate_key(bundle: AudioBundle, track: BeatTrack) -> KeyEstimate:
    """Estimate the global key and the per-region keys.

    Args:
        bundle: The S0 output.
        track: The S1.1 beat track, used for beat-synchronous chroma.

    Returns:
        The key estimate, including regions.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("S1.5 key estimation lands in Phase 3")


def fifths_for(tonic_pc: int, mode: str) -> int:
    """Return the MusicXML ``fifths`` value for a tonic pitch class and mode.

    Args:
        tonic_pc: Tonic pitch class, 0..11 with C = 0.
        mode: ``"major"`` or ``"minor"``.

    Returns:
        The key signature as a number of fifths, -7..7.

    Raises:
        NotImplementedError: Phase 3.
    """
    raise NotImplementedError("key signature mapping lands in Phase 3")
