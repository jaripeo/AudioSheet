#!/usr/bin/env python3
"""Synthesise test audio from known MIDI so fixtures have exact ground truth.

ARCHITECTURE.md Section 5.3, Phase 1, step 3 and Appendix 5.6: the ``synth/``
fixture family is the backbone of every accuracy gate, because the ground truth is
the MIDI the audio was rendered from rather than a human annotation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
FIXTURE_DIR: Final[Path] = REPO_ROOT / "core" / "tests" / "fixtures"


def render_midi_to_wav(midi_path: Path, wav_path: Path, soundfont: Path) -> Path:
    """Render a MIDI file to WAV with the vendored soundfont.

    Args:
        midi_path: Source MIDI.
        wav_path: Destination WAV.
        soundfont: Vendored SoundFont2 bank.

    Returns:
        The path written.

    Raises:
        NotImplementedError: Phase 1 (ARCHITECTURE.md Section 5.3).
    """
    raise NotImplementedError("fixture synthesis lands in Phase 1")


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit status.

    Raises:
        NotImplementedError: Phase 1.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=FIXTURE_DIR / "synth")
    parser.parse_args(argv)
    raise NotImplementedError("fixture synthesis lands in Phase 1")


if __name__ == "__main__":
    raise SystemExit(main())
