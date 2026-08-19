"""S5.4 voice separation — ARCHITECTURE.md Section 1.8.

No voice may contain overlapping notes (validator V-2). Voice 1 takes the highest
pitch and ascending voice numbers take descending pitches; a voice silent for more
than ``VOICE_RETIREMENT_BARS`` bars is retired and re-opened lazily.
"""

from __future__ import annotations

from typing import Final

from audiosheet.schema import DifficultyProfile, Note

#: Bars of silence after which a voice is retired.
VOICE_RETIREMENT_BARS: Final[int] = 2


def assign_voices(notes: list[Note], profile: DifficultyProfile) -> list[Note]:
    """Split simultaneous notes into monophonic voices.

    Args:
        notes: Notes of one staff, in onset order.
        profile: Difficulty profile supplying ``max_voices``.

    Returns:
        New notes with ``voice`` assigned.

    Raises:
        NotImplementedError: Phase 6.
    """
    raise NotImplementedError("S5.4 voice separation lands in Phase 6")
