#!/usr/bin/env python3
"""Enforce the performance budgets of ARCHITECTURE.md Section 4.3.

Budgets, measured on the reference machine of Appendix 5.6:

    full analysis of a 4-minute track   <= 150 s
    slider re-render (p95)              <= 400 ms
    first paint after analysis          <= 1.5 s
    peak resident memory                <= 6 GiB

The Linux CI target is allowed a 3x wall-clock multiplier but must meet every
accuracy gate identically.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Final

#: Wall-clock ceiling for a full 4-minute analysis, in seconds.
FULL_ANALYSIS_BUDGET_S: Final[float] = 150.0

#: p95 ceiling for a difficulty-slider re-render, in milliseconds (INV-7).
SLIDER_BUDGET_MS: Final[float] = 400.0

#: Ceiling for first paint of the score after analysis, in seconds.
FIRST_PAINT_BUDGET_S: Final[float] = 1.5

#: Peak resident memory ceiling, in bytes.
PEAK_RSS_BUDGET_BYTES: Final[int] = 6 * 1024 * 1024 * 1024

#: Wall-clock multiplier permitted on the CPU-only CI target.
CI_WALL_CLOCK_MULTIPLIER: Final[float] = 3.0


@dataclass(frozen=True)
class BenchResult:
    """One measured budget."""

    name: str
    measured: float
    budget: float
    unit: str

    @property
    def passed(self) -> bool:
        """Return whether the measurement is within budget."""
        return self.measured <= self.budget


def run_benchmarks(ci: bool) -> list[BenchResult]:
    """Measure every budget in Section 4.3.

    Args:
        ci: Whether to apply ``CI_WALL_CLOCK_MULTIPLIER`` to wall-clock budgets.

    Returns:
        One result per budget.

    Raises:
        NotImplementedError: Phase 8 (ARCHITECTURE.md Section 5.3).
    """
    raise NotImplementedError("performance benchmarks land in Phase 8")


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Command-line arguments; ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit status.

    Raises:
        NotImplementedError: Phase 8.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ci", action="store_true", help="apply the CI wall-clock multiplier"
    )
    args = parser.parse_args(argv)
    run_benchmarks(args.ci)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
