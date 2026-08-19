"""S2 stem isolation — ARCHITECTURE.md Section 1.5 (Normative).

The only module in the shipped application permitted to import ``torch``. Demucs
v4's hybrid transformer exports poorly to ONNX, so PyTorch is accepted here and
nowhere else; keeping it behind this one file makes a future port a one-file
change (docs/adr/0001-onnx-over-torch.md).

``shifts`` MUST be 0: random-shift averaging violates INV-2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

from audiosheet.ingest.decode import AudioBundle, Pcm
from audiosheet.pipeline.cache import blake3_hex
from audiosheet.pipeline.stage import StageContext

#: Default model: six stems, because guitar/piano separation improves tab quality.
DEFAULT_MODEL: Final[str] = "htdemucs_6s"

#: Low-memory fallback, where guitar and piano collapse into "other".
FALLBACK_MODEL: Final[str] = "htdemucs"

#: Native inference window, in seconds.
SEGMENT_S: Final[float] = 7.8

#: Cross-fade between windows; removes seam clicks.
OVERLAP: Final[float] = 0.25

#: Random-shift averaging passes. MUST stay 0 (INV-2).
SHIFTS: Final[int] = 0

#: Device preference order.
DEVICE_ORDER: Final[tuple[str, ...]] = ("cuda", "mps", "cpu")

#: Minimum progress reporting rate during separation, in Hz.
MIN_PROGRESS_HZ: Final[float] = 2.0

StemName = Literal["vocals", "drums", "bass", "guitar", "piano", "other"]

#: Stems produced by each model.
MODEL_STEMS: Final[dict[str, tuple[StemName, ...]]] = {
    DEFAULT_MODEL: ("drums", "bass", "other", "vocals", "guitar", "piano"),
    FALLBACK_MODEL: ("drums", "bass", "other", "vocals"),
}


@dataclass(frozen=True)
class Stem:
    """One separated stem.

    Attributes:
        name: Stem identifier.
        path: Lossless 16-bit FLAC in the project cache.
        loudness_lufs: Integrated loudness, used by the presence gate.
        present: False when the stem is below the presence gate and is skipped.
    """

    name: StemName
    path: Path
    loudness_lufs: float
    present: bool

    def load(self, sample_rate: int, channels: int) -> Pcm:
        """Decode the stem at the rate a downstream model needs.

        Args:
            sample_rate: Target sample rate in Hz.
            channels: Target channel count.

        Returns:
            Planar float32 PCM.

        Raises:
            NotImplementedError: Phase 4.
        """
        raise NotImplementedError("stem loading lands in Phase 4")


@dataclass(frozen=True)
class StemSet:
    """The S2 output.

    Attributes:
        model: Name of the separation model used.
        device: Device the model ran on.
        stems: Separated stems, keyed by name.
        skipped: True when separation was skipped (browser target).
    """

    model: str
    device: str
    stems: dict[StemName, Stem]
    skipped: bool = False
    warnings: list[str] = field(default_factory=list)

    def present_stems(self) -> list[Stem]:
        """Return the stems that passed the presence gate, in a stable order."""
        return [self.stems[name] for name in sorted(self.stems) if self.stems[name].present]

    def content_hash(self) -> str:
        """Return a stable fingerprint for cache keying."""
        parts = [f"{name}:{self.stems[name].loudness_lufs:.3f}" for name in sorted(self.stems)]
        return blake3_hex(self.model.encode("utf-8"), "|".join(parts).encode("utf-8"))


def separate(bundle: AudioBundle, ctx: StageContext, model: str = DEFAULT_MODEL) -> StemSet:
    """Separate the 44.1 kHz stereo mix into stems.

    Args:
        bundle: The S0 output.
        ctx: Ambient stage services; progress is reported at >= 2 Hz.
        model: Separation model name.

    Returns:
        The separated stem set.

    Raises:
        AudioSheetError: ``E_SEPARATION_OOM`` when the model runs out of memory.
        NotImplementedError: Phase 4.
    """
    raise NotImplementedError("S2 separation lands in Phase 4")


def resolve_device() -> str:
    """Return the first available device in ``DEVICE_ORDER``.

    Returns:
        The chosen device name, recorded in provenance.

    Raises:
        NotImplementedError: Phase 4.
    """
    raise NotImplementedError("device resolution lands in Phase 4")
