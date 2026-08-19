/**
 * Duration table — ARCHITECTURE.md Appendix 5.5 (Normative).
 *
 * The only legal source of `notated_type` and `dots`. Any duration not in this
 * table MUST be expressed either as a tuplet or as a tied chain of table values,
 * longest first, left-aligned to the strongest metric position.
 */

import type { Dots, NotatedType } from "@audiosheet/schema";

/** One notatable duration. */
export interface DurationEntry {
  readonly ticks: number;
  readonly type: NotatedType;
  readonly dots: Dots;
}

/** The normative table, longest first (Appendix 5.5). */
export const DURATION_TABLE: readonly DurationEntry[] = [
  { ticks: 3840, type: "whole", dots: 0 },
  { ticks: 2880, type: "half", dots: 1 },
  { ticks: 1920, type: "half", dots: 0 },
  { ticks: 1680, type: "quarter", dots: 2 },
  { ticks: 1440, type: "quarter", dots: 1 },
  { ticks: 960, type: "quarter", dots: 0 },
  { ticks: 840, type: "eighth", dots: 2 },
  { ticks: 720, type: "eighth", dots: 1 },
  { ticks: 480, type: "eighth", dots: 0 },
  { ticks: 420, type: "16th", dots: 2 },
  { ticks: 360, type: "16th", dots: 1 },
  { ticks: 240, type: "16th", dots: 0 },
  { ticks: 180, type: "32nd", dots: 1 },
  { ticks: 120, type: "32nd", dots: 0 },
  { ticks: 60, type: "64th", dots: 0 },
];

/** Look up a duration by exact tick count. */
export function durationFor(ticks: number): DurationEntry | undefined {
  return DURATION_TABLE.find((entry) => entry.ticks === ticks);
}

/** Return whether a tick count is directly notatable. */
export function isNotatable(ticks: number): boolean {
  return durationFor(ticks) !== undefined;
}

/**
 * Decompose a duration into a tied chain of notatable values, longest first.
 *
 * @param ticks - The duration to decompose.
 * @returns The chain, or an empty array when `ticks` is not decomposable.
 */
export function tiedChain(ticks: number): DurationEntry[] {
  const chain: DurationEntry[] = [];
  let remaining = ticks;
  for (const entry of DURATION_TABLE) {
    while (remaining >= entry.ticks) {
      chain.push(entry);
      remaining -= entry.ticks;
    }
    if (remaining === 0) {
      break;
    }
  }
  return remaining === 0 ? chain : [];
}
