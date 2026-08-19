/**
 * Fingering assignment — ARCHITECTURE.md Section 2.3.5, step 3.
 *
 * Fingers follow the fret offset from the position anchor, overridden by barre
 * logic and by a small DP that avoids reusing one finger on consecutive frets.
 */

import type { Finger } from "@audiosheet/schema";
import type { TabNode } from "./costs";
import type { PositionSegment } from "./viterbi";

/** Offset-from-anchor to finger, per Section 2.3.5. Index 3 covers offset >= 3. */
export const OFFSET_TO_FINGER: readonly Finger[] = [1, 2, 3, 4];

/**
 * Return the default finger for a fret within a position.
 *
 * @param fret - The fret, where 0 is open.
 * @param anchor - The position's anchor fret.
 * @returns The finger, or null for an open string.
 */
export function defaultFinger(fret: number, anchor: number): Finger {
  if (fret === 0) {
    return null;
  }
  const offset = Math.max(0, Math.min(3, fret - anchor));
  return OFFSET_TO_FINGER[offset] ?? 4;
}

/**
 * Assign fingers across a position segment.
 *
 * @param nodes - Placements in the segment.
 * @param segment - The segment being fingered.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function assignFingers(
  nodes: readonly TabNode[],
  segment: PositionSegment,
): Finger[] {
  throw new Error("unimplemented: fingering assignment lands in Phase 7");
}
