/**
 * Merge, tie and cleanup — ARCHITECTURE.md Section 2.1.4.
 */

import type { DifficultyProfile, Note, TimingGrid } from "@audiosheet/schema";

/** Same-pitch notes closer than this merge into one, in seconds. */
export const MERGE_GAP_S = 0.03;

/**
 * Merge adjacent same-pitch notes and re-tie across barlines.
 *
 * @param notes - Notes of one voice, quantised.
 * @param grid - The timing grid, for barline positions.
 * @param profile - Supplies the ornament policy and repeat-sign preference.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function mergeAndTie(
  notes: readonly Note[],
  grid: TimingGrid,
  profile: DifficultyProfile,
): Note[] {
  throw new Error("unimplemented: merge and tie lands in Phase 2");
}

/**
 * Split a note that crosses a barline into a tied pair.
 *
 * @param note - The note to split.
 * @param barlineTick - The barline it crosses.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function splitAtBarline(note: Note, barlineTick: number): [Note, Note] {
  throw new Error("unimplemented: barline splitting lands in Phase 2");
}
