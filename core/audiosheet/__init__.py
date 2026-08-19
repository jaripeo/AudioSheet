"""AudioSheet DSP/ML core.

Turns an uploaded .mp3/.wav into a ScoreDocument (ARCHITECTURE.md Section 3),
which the TypeScript difficulty engine and renderers consume.

Nothing in this package may open a network socket (INV-1).
"""

from audiosheet.version import APP_VERSION, SCHEMA_VERSION

__all__ = ["APP_VERSION", "SCHEMA_VERSION"]
