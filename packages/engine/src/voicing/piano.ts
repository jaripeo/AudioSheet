/**
 * Piano voicing — ARCHITECTURE.md Section 2.2.2.
 *
 * The transcribed bass note wins over the theoretical root: the engine never
 * invents a bass note that contradicts the audio.
 */

import type { DifficultyProfile } from "@audiosheet/schema";
import type { Voicing } from "@audiosheet/schema";
import type { ChordFrame } from "../polyphony";

/** Maximum hand span, in semitones, by level. */
export const MAX_HAND_SPAN = { medium: 10, complex: 12 } as const;

/** Intervals narrower than this are muddy in the bottom octave. */
export const MIN_LOW_INTERVAL_SEMITONES = 3;

/** Below this pitch, narrow intervals get folded up an octave. */
export const LOW_REGISTER_CEILING_MIDI = 48;

/**
 * Voice a chord frame for two hands.
 *
 * @param frame - The frame to voice.
 * @param profile - Supplies the level and hand-span limit.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function voicePiano(frame: ChordFrame, profile: DifficultyProfile): Voicing {
  throw new Error("unimplemented: piano voicing lands in Phase 7");
}
