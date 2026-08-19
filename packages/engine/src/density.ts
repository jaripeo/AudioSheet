/**
 * Budgeted note pruning — ARCHITECTURE.md Section 2.1.1.
 *
 * Density is controlled per measure, not globally, so dense passages thin out
 * while sparse ones stay intact. Dropped notes are retained with
 * `flags.dropped = true` and `render = false` so the slider can restore them
 * monotonically and the UI can ghost them.
 */

import type { DifficultyProfile, Note, TimingGrid } from "@audiosheet/schema";

/** Every measure that had content keeps at least this many notes. */
export const MIN_NOTES_PER_MEASURE = 1;

/** Half-width, in beats, of the window that protects a beat anchor. */
export const ANCHOR_WINDOW_BEATS = 0.5;

/** Melodic leap, in semitones, that the continuity constraint refuses to create. */
export const MAX_INDUCED_LEAP_SEMITONES = 12;

/**
 * Prune notes against the profile's per-second budget.
 *
 * @param notes - Notes of one part, carrying salience.
 * @param grid - The timing grid, for measure windows.
 * @param profile - Supplies `note_budget_nps`; null means unrestricted.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function reduceDensity(
  notes: readonly Note[],
  grid: TimingGrid,
  profile: DifficultyProfile,
): Note[] {
  throw new Error("unimplemented: density budgeting lands in Phase 2");
}
