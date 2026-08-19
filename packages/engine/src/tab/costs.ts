/**
 * Fretboard node and transition costs — ARCHITECTURE.md Sections 2.3.2 and 2.3.3.
 *
 * `position(f) = max(0, f - 3)` models the index finger anchoring a four-fret box.
 * Open strings inherit the previous position, so they never force a shift.
 */

import type { DifficultyProfile, TabWeights } from "@audiosheet/schema";
import weightData from "./weights.json" with { type: "json" };

/** The normative per-level weights (Section 2.3.4). */
export const TAB_WEIGHTS = weightData.weights as unknown as Record<string, TabWeights>;

/** Frets above this are awkward to reach; `k_high` penalises them. */
export const HIGH_FRET_THRESHOLD = 17;

/** Highest fret the optimiser will consider. */
export const MAX_FRET = 24;

/** Floor on the inter-note gap used by the time-pressure term, in seconds. */
export const MIN_GAP_S = 0.05;

/** One candidate placement of a pitch. */
export interface TabNode {
  readonly string: number;
  readonly fret: number;
}

/**
 * Return the hand position implied by a fret.
 *
 * @param fret - The fret, where 0 is open.
 * @returns The fret under the index finger.
 */
export function position(fret: number): number {
  return Math.max(0, fret - 3);
}

/**
 * Return the standing cost of a placement.
 *
 * @param node - The candidate placement.
 * @param profile - Supplies the weights.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function nodeCost(node: TabNode, profile: DifficultyProfile): number {
  throw new Error("unimplemented: fretboard node costs land in Phase 7");
}

/**
 * Return the cost of moving between two placements.
 *
 * @param from - The previous placement.
 * @param to - The next placement.
 * @param gapSeconds - Time between the two onsets.
 * @param profile - Supplies the weights.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function edgeCost(
  from: TabNode,
  to: TabNode,
  gapSeconds: number,
  profile: DifficultyProfile,
): number {
  throw new Error("unimplemented: fretboard edge costs land in Phase 7");
}
