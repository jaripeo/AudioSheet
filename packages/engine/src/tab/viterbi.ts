/**
 * Shortest path over the fretboard DAG — ARCHITECTURE.md Section 2.3.5.
 *
 * Viterbi, not greedy: O(sum |L_i| * |L_i+1|) with |L| <= 6, about 36 edge
 * evaluations per note. Position segments shorter than
 * `MIN_SEGMENT_NOTES` are re-run with a doubled shift cost to try to absorb them
 * into a neighbour.
 */

import type { DifficultyProfile } from "@audiosheet/schema";
import type { TabNode } from "./costs";
import type { TabLayer } from "./graph";

/** A position holding for at least this many notes earns a position marker. */
export const POSITION_MARKER_MIN_NOTES = 4;

/** Segments shorter than this are re-run with `k_shift` doubled. */
export const MIN_SEGMENT_NOTES = 3;

/** A run of notes sharing one hand position. */
export interface PositionSegment {
  readonly position: number;
  readonly startIndex: number;
  readonly endIndex: number;
}

/** The optimiser's output. */
export interface TabPath {
  readonly nodes: readonly TabNode[];
  readonly segments: readonly PositionSegment[];
  readonly totalCost: number;
}

/**
 * Find the cheapest placement path through the graph.
 *
 * @param layers - The layered graph.
 * @param profile - Supplies the cost weights.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function optimisePath(
  layers: readonly TabLayer[],
  profile: DifficultyProfile,
): TabPath {
  throw new Error("unimplemented: fretboard path optimisation lands in Phase 7");
}
