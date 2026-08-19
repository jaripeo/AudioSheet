/**
 * Voice leading as min-cost matching — ARCHITECTURE.md Section 2.2.1.
 *
 * Rectangular min-cost bipartite matching (Hungarian / Jonker-Volgenant), exact
 * and O(n^3) for the n <= 6 voices we allow. Greedy frame-by-frame matching can
 * paint itself into a corner, so a beam search of fixed width `BEAM_WIDTH` runs
 * over frames and keeps the cheapest path per measure. The width is normative, to
 * bound cost and preserve determinism (INV-2).
 */

import type { DifficultyProfile, Note } from "@audiosheet/schema";
import type { ChordFrame } from "./polyphony";

/** Assignment cost weights (Section 2.2.1). */
export const VOICE_WEIGHTS = {
  step: 1.0,
  cross: 6.0,
  range: 4.0,
  /** Applied per semitone beyond `LEAP_FREE_SEMITONES`. */
  leap: 0.5,
  rest: 3.0,
  /** Complex only; 0 at Medium. */
  parallel: 2.0,
} as const;

/** Leaps up to this size are not penalised. */
export const LEAP_FREE_SEMITONES = 8;

/** Beam width over frames. Normative. */
export const BEAM_WIDTH = 4;

/**
 * Assign each frame's pitches to voices, minimising total motion.
 *
 * @param frames - Chord frames of one staff, in order.
 * @param profile - Supplies `max_voices` and the level-dependent parallel penalty.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function assignVoices(
  frames: readonly ChordFrame[],
  profile: DifficultyProfile,
): Note[] {
  throw new Error("unimplemented: voice leading lands in Phase 7");
}

/**
 * Return the cost of putting a pitch in a voice.
 *
 * @param lastPitch - The voice's previous pitch, or null when it is resting.
 * @param pitch - The candidate pitch.
 * @param voiceIndex - Zero-based voice index; voice 0 is the highest.
 * @param profile - Supplies the level-dependent weights.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function assignmentCost(
  lastPitch: number | null,
  pitch: number,
  voiceIndex: number,
  profile: DifficultyProfile,
): number {
  throw new Error("unimplemented: voice leading lands in Phase 7");
}
