/**
 * Guitar voicing — ARCHITECTURE.md Section 2.2.2.
 *
 * Enumerate then score: the search space is small enough that enumeration is
 * exact. Ties break by lower mean fret, then by lower string indices, so the
 * result is deterministic (INV-2).
 */

import type { DifficultyProfile, Tuning, Voicing } from "@audiosheet/schema";
import type { ChordFrame } from "../polyphony";
import shapeData from "./shapes.json" with { type: "json" };

/** Standard six-string tuning; index 0 is string 1 (highest). */
export const STANDARD_TUNING: readonly number[] = [64, 59, 55, 50, 45, 40];

/** Scoring coefficients (Section 2.2.2, step 4). */
export const VOICING_SCORE = {
  span: 1.0,
  frettedCount: 0.6,
  meanFret: 0.4,
  stringSkips: 2.0,
  openStringBonus: -1.2,
  commonShapeBonus: -0.8,
  positionContinuity: 3.0,
  missingChordTone: 5.0,
} as const;

/** Above this fret the span limit is relaxed by one, because frets narrow. */
export const SPAN_RELAXATION_FRET = 12;

/** Fretted notes allowed without a barre. */
export const MAX_FRETTED_WITHOUT_BARRE = 4;

/** Common shapes the `is_common_shape` scoring term recognises. */
export const COMMON_SHAPES = shapeData.shapes;

/**
 * Return every (string, fret) that sounds a pitch in the given window.
 *
 * @param midi - The sounding pitch.
 * @param tuning - The part's tuning, including capo.
 * @param window - Inclusive [lo, hi] fret bounds.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function candidatePositions(
  midi: number,
  tuning: Tuning,
  window: readonly [number, number],
): { string: number; fret: number }[] {
  throw new Error("unimplemented: candidate enumeration lands in Phase 7");
}

/**
 * Enumerate and score playable voicings, returning the best.
 *
 * @param frame - The frame to voice.
 * @param tuning - The part's tuning.
 * @param profile - Supplies the window, span, string and barre limits.
 * @param previousPosition - Previous hand position, for the continuity term.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function voiceGuitar(
  frame: ChordFrame,
  tuning: Tuning,
  profile: DifficultyProfile,
  previousPosition: number | null,
): Voicing {
  throw new Error("unimplemented: guitar voicing lands in Phase 7");
}
