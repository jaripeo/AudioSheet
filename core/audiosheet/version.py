"""Version identifiers for the core and the document schema."""

from __future__ import annotations

from typing import Final

#: Version of this application, recorded in ScoreDocument.provenance.app_version.
APP_VERSION: Final[str] = "0.1.0"

#: Version of the ScoreDocument contract. Must match ScoreDocument.schema_version.
SCHEMA_VERSION: Final[str] = "1.0.0"
