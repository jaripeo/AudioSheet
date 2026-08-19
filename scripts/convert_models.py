#!/usr/bin/env python3
"""Convert upstream model weights to ONNX. Development-time only.

ARCHITECTURE.md Section 4.2: runtime inference uses ONNX Runtime, and PyTorch or
TensorFlow appear only in this offline conversion toolchain — never in the shipped
application. The one exception is Demucs, which stays on PyTorch at runtime
(docs/adr/0001-onnx-over-torch.md).

This script is not part of `make bootstrap`; it needs the heavy conversion extras
and is run by hand when a model version is bumped.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def convert_crepe(weights: Path, out: Path) -> Path:
    """Convert published CREPE Keras/TF weights to ONNX.

    Args:
        weights: Upstream weights file.
        out: Destination ``.onnx`` path.

    Returns:
        The path written.

    Raises:
        NotImplementedError: Phase 5 (ARCHITECTURE.md Section 5.3).
    """
    raise NotImplementedError("CREPE conversion lands in Phase 5")


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit status.

    Raises:
        NotImplementedError: Phase 5.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=["crepe"])
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.parse_args(argv)
    raise NotImplementedError("model conversion lands in Phase 5")


if __name__ == "__main__":
    raise SystemExit(main())
