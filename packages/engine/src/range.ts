/**
 * Range constraint — ARCHITECTURE.md Section 2.1.5.
 *
 * Whole phrases are transposed by octaves, never individual notes: an octave jump
 * inside a legato line is worse than a wide range.
 */

import type { DifficultyProfile, Note } from "@audiosheet/schema";

/** Rests of at least this length, in beats, separate phrases. */
export const PHRASE_BREAK_BEATS = 1.0;

/**
 * Fold phrases into the profile's pitch window.
 *
 * @param notes - Notes of one staff, in onset order.
 * @param profile - Supplies `pitch_range_semitones`; null means unrestricted.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function constrainRange(notes: readonly Note[], profile: DifficultyProfile): Note[] {
  throw new Error("unimplemented: range constraint lands in Phase 2");
}
