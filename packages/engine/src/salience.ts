/**
 * Note salience — ARCHITECTURE.md Section 2.1.1.
 *
 * S(n) = w_conf*C + w_metric*M + w_dur*D + w_pitch*P + w_energy*E
 *      + w_contour*L + w_harm*H, with the weights taken from the profile and
 * summing to 1.0 at every level.
 */

import type { ChordEvent, DifficultyProfile, Note, TimingGrid } from "@audiosheet/schema";

/** Metric weights by subdivision depth (Section 2.1.1, term M). */
export const METRIC_WEIGHTS = {
  downbeat: 1.0,
  beat: 0.8,
  halfBeat: 0.5,
  quarterBeat: 0.25,
  finer: 0.1,
} as const;

/**
 * Return the metric weight of a tick position.
 *
 * @param tick - Position in ticks.
 * @param grid - The timing grid.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function metricWeight(tick: number, grid: TimingGrid): number {
  throw new Error("unimplemented: metric weighting lands in Phase 2");
}

/**
 * Attach a salience score to every note.
 *
 * @param notes - Notes of one part, in onset order.
 * @param grid - The timing grid.
 * @param chords - The active chord track, for the harmonic term.
 * @param profile - Supplies `salience_weights`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function scoreSalience(
  notes: readonly Note[],
  grid: TimingGrid,
  chords: readonly ChordEvent[],
  profile: DifficultyProfile,
): Note[] {
  throw new Error("unimplemented: salience scoring lands in Phase 2");
}
