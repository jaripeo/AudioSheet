"""Command-line entry point.

``audiosheet transcribe in.mp3 -o out.json`` runs the offline pipeline;
``audiosheet validate out.json`` runs the S6 gate on an existing document.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audiosheet.pipeline.errors import AudioSheetError
from audiosheet.validate import check_invariants
from audiosheet.validate.jsonschema_gate import load_document
from audiosheet.version import APP_VERSION


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(prog="audiosheet", description=__doc__)
    parser.add_argument("--version", action="version", version=APP_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    transcribe = sub.add_parser("transcribe", help="transcribe an audio file")
    transcribe.add_argument("input", type=Path, help="input .mp3 or .wav")
    transcribe.add_argument("-o", "--output", type=Path, required=True, help="output JSON")

    validate = sub.add_parser("validate", help="run the S6 gate on a document")
    validate.add_argument("document", type=Path, help="a ScoreDocument JSON file")

    return parser


def cmd_transcribe(input_path: Path, output_path: Path) -> int:
    """Run the offline pipeline over ``input_path``.

    Args:
        input_path: The audio file.
        output_path: Where to write the resulting document.

    Returns:
        Process exit status.

    Raises:
        NotImplementedError: Phase 1 wires ingestion; Phase 6 completes the chain.
    """
    raise NotImplementedError("the transcribe command is wired up in Phase 1")


def cmd_validate(document_path: Path) -> int:
    """Validate a document against the schema and the invariants.

    Args:
        document_path: A ScoreDocument JSON file.

    Returns:
        0 when the document is valid, 1 otherwise.
    """
    try:
        document = load_document(document_path)
        check_invariants(document)
    except AudioSheetError as exc:
        print(json.dumps(exc.as_dict(), indent=2), file=sys.stderr)
        return 1
    counts = ", ".join(f"{part.id}: {len(part.notes)} notes" for part in document.parts)
    print(f"{document_path} is valid ({counts or 'no parts'})")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit status.
    """
    args = build_parser().parse_args(argv)
    if args.command == "transcribe":
        return cmd_transcribe(args.input, args.output)
    return cmd_validate(args.document)


if __name__ == "__main__":
    raise SystemExit(main())
