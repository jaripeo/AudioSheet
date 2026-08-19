/**
 * Key simplification — ARCHITECTURE.md Section 2.1.6.
 *
 * For guitar parts the transposition is preferably expressed as a capo, which
 * preserves the sounding key while simplifying the fingering. A silently
 * transposed score is a bug, so the result is always recorded in
 * `document.transposition` and shown in the UI header.
 */

import type { DifficultyProfile, ScoreDocument } from "@audiosheet/schema";

/** Transpositions within this many semitones are preferred. */
export const MAX_PREFERRED_SHIFT_SEMITONES = 3;

/** Capo positions the engine is willing to ask for. */
export const CAPO_RANGE: readonly [number, number] = [1, 5];

/**
 * Transpose the score if its key carries more accidentals than the profile allows.
 *
 * @param doc - The document to simplify.
 * @param profile - Supplies `max_accidentals_in_key` and `prefer_capo`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function simplifyKey(doc: ScoreDocument, profile: DifficultyProfile): ScoreDocument {
  throw new Error("unimplemented: key simplification lands in Phase 2");
}
