/**
 * Chord-frame collapse — ARCHITECTURE.md Section 2.1.2.
 *
 * A strummed chord is not simultaneous, so onsets within `FRAME_EPSILON_S` group
 * into one frame. The frame's outer voices always survive: the melody at every
 * level, and the bass from Medium upward.
 */

import type { ChordEvent, DifficultyProfile, Note } from "@audiosheet/schema";

/** Onset tolerance that groups notes into one chord frame, in seconds. */
export const FRAME_EPSILON_S = 0.05;

/** Span within which a sequential run is treated as an arpeggio, in seconds. */
export const ARPEGGIO_SPAN_S = 0.3;

/** A set of notes treated as sounding together. */
export interface ChordFrame {
  readonly tick: number;
  readonly notes: readonly Note[];
  readonly chord: ChordEvent | null;
}

/**
 * Group notes into chord frames.
 *
 * @param notes - Notes of one staff, in onset order.
 * @param chords - The chord track, for harmonic labelling.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function buildFrames(
  notes: readonly Note[],
  chords: readonly ChordEvent[],
): ChordFrame[] {
  throw new Error("unimplemented: frame construction lands in Phase 2");
}

/**
 * Reduce each frame to the profile's chord-tone budget.
 *
 * @param frames - Frames from `buildFrames`.
 * @param profile - Supplies `chord_tone_priority` and `chord_max_notes`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function collapsePolyphony(
  frames: readonly ChordFrame[],
  profile: DifficultyProfile,
): Note[] {
  throw new Error("unimplemented: polyphonic simplification lands in Phase 2");
}
