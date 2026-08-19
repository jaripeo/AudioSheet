"""S4 percussion transcription — ARCHITECTURE.md Section 1.7.

The goal is a readable reduced drum staff and a metronomic reference, not a
forensic transcription. Runs only when the drums stem passed the presence gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import RawNote
from audiosheet.separation.demucs_runner import Stem

#: Onset-detection bands, in Hz: kick, snare/tom, cymbals.
ONSET_BANDS_HZ: Final[tuple[tuple[float, float], ...]] = (
    (20.0, 120.0),
    (120.0, 1500.0),
    (3000.0, 20000.0),
)

#: Adaptive-median threshold multiplier.
THRESHOLD_LAMBDA: Final[float] = 1.35

#: Median window for adaptive thresholding, in seconds.
THRESHOLD_WINDOW_S: Final[float] = 0.100

#: Half-width of the log-mel patch handed to the classifier, in seconds.
CLASSIFIER_CONTEXT_S: Final[float] = 0.080

#: Log-mel patch shape (mel bins, frames).
CLASSIFIER_PATCH_SHAPE: Final[tuple[int, int]] = (64, 15)

#: General MIDI percussion key map for the classes we transcribe.
GM_PERCUSSION_MAP: Final[dict[str, int]] = {
    "kick": 36,
    "snare": 38,
    "closed_hat": 42,
    "open_hat": 46,
    "ride": 51,
    "crash": 49,
    "tom_hi": 48,
    "tom_mid": 45,
    "tom_lo": 41,
}


@dataclass(frozen=True)
class RawDrumSet:
    """The S4 output.

    Attributes:
        notes: Percussion events, pitched by the GM key map.
        classes: Which kit pieces were detected at all.
        used_fallback: True when the heuristic classifier ran instead of the CNN.
    """

    notes: list[RawNote]
    classes: list[str]
    used_fallback: bool = False
    warnings: list[str] = field(default_factory=list)

    def ids(self) -> set[str]:
        """Return every note id, for the strict form of validator V-5."""
        return {note.id for note in self.notes}

    def content_hash(self) -> str:
        """Return a stable fingerprint for cache keying."""
        payload = "|".join(f"{n.id}:{n.onset_s:.6f}:{n.midi}" for n in self.notes)
        return blake3_hex(b"drums", payload.encode("utf-8"))


def transcribe_drums(stem: Stem, ctx: StageContext) -> RawDrumSet:
    """Detect and classify percussion onsets.

    Args:
        stem: The drums stem.
        ctx: Ambient stage services.

    Returns:
        The percussion event set.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("S4 drum transcription lands in Phase 5")


def classify_onset_heuristic(band_energies: tuple[float, float, float]) -> str:
    """Classify one onset from band energy ratios, when the CNN is unavailable.

    Args:
        band_energies: Energy in the three ``ONSET_BANDS_HZ`` bands.

    Returns:
        A key of ``GM_PERCUSSION_MAP``.

    Raises:
        NotImplementedError: Phase 5.
    """
    raise NotImplementedError("heuristic drum classification lands in Phase 5")
