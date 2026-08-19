"""MusicXML 4.0 export — ARCHITECTURE.md Section 1.11.

Tuplets carry both ``<time-modification>`` and ``<notations><tuplet>`` brackets;
missing either causes silent misrendering in most consumers. Beaming is computed
explicitly from meter-aware grouping rather than delegated to the consumer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from audiosheet.schema import ScoreDocument

#: MusicXML ``<divisions>`` value; matches PPQ so durations are integral.
DIVISIONS: Final[int] = 960

#: Root element of the emitted document.
ROOT_ELEMENT: Final[str] = "score-partwise"

#: MusicXML version declared in the output.
MUSICXML_VERSION: Final[str] = "4.0"


def to_musicxml(doc: ScoreDocument) -> str:
    """Serialise a document to MusicXML 4.0 ``score-partwise`` text.

    Args:
        doc: The document to export.

    Returns:
        The MusicXML document as text.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED`` on a serialisation failure.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("MusicXML export lands in Phase 1")


def write_musicxml(doc: ScoreDocument, path: Path, *, compressed: bool = False) -> Path:
    """Write MusicXML to disk, optionally as a compressed ``.mxl``.

    Args:
        doc: The document to export.
        path: Destination path.
        compressed: When True, emit a zipped ``.mxl`` container.

    Returns:
        The path written.

    Raises:
        AudioSheetError: ``E_EXPORT_FAILED``.
        NotImplementedError: Phase 1.
    """
    raise NotImplementedError("MusicXML export lands in Phase 1")
