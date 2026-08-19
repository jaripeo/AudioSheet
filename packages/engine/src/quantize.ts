/**
 * Rhythmic quantisation — ARCHITECTURE.md Section 2.1.3.
 *
 * A dynamic program over grid positions, solved with Viterbi and bounded to
 * `SEARCH_WINDOW_BEATS` around each raw onset. Ties break toward the earlier grid
 * position, which keeps the result deterministic (INV-2).
 *
 * This module and `core/audiosheet/symbolic/quantize.py` implement the same DP
 * for different runtimes. They MUST agree on every vector in
 * `core/tests/golden/quantize/`; that shared suite is what stops them drifting.
 */

import type { DifficultyProfile, Note, TimingGrid } from "@audiosheet/schema";

/** Search half-width around a raw onset, in beats. */
export const SEARCH_WINDOW_BEATS = 1.0;

/** The outcome of quantising one voice. */
export interface QuantizeResult {
  readonly notes: Note[];
  readonly meanShiftTicks: number;
  readonly droppedIds: readonly string[];
}

/**
 * Snap onsets, then durations, to the profile's grid.
 *
 * @param notes - Notes of a single voice, in onset order.
 * @param grid - The timing grid.
 * @param profile - Supplies the grid divisions and the cost weights.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function quantize(
  notes: readonly Note[],
  grid: TimingGrid,
  profile: DifficultyProfile,
): QuantizeResult {
  throw new Error("unimplemented: quantisation lands in Phase 2");
}

/**
 * Return the legal onset lattice for a profile, in ticks.
 *
 * @param grid - The timing grid.
 * @param profile - Supplies `grid_divisions` and `allow_tuplets`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function legalPositions(grid: TimingGrid, profile: DifficultyProfile): number[] {
  throw new Error("unimplemented: grid construction lands in Phase 2");
}
