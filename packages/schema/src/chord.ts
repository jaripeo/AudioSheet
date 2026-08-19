/** Chords and voicings — ARCHITECTURE.md Section 3.3. */

import type { Ticks, Seconds } from "./timing";
import type { Step, Alter, Finger } from "./note";

export type ChordQuality =
  | "maj"
  | "min"
  | "dim"
  | "aug"
  | "sus2"
  | "sus4"
  | "maj6"
  | "min6"
  | "dom7"
  | "maj7"
  | "min7"
  | "min7b5"
  | "dim7"
  | "aug7"
  | "9"
  | "maj9"
  | "min9"
  | "11"
  | "13"
  | "5"
  | "none";

export type ChordSource = "audio" | "symbolic" | "fused";

export type VoicingInstrument = "guitar" | "bass" | "ukulele" | "piano";

export interface BarreSpec {
  /** @integer @minimum 1 @maximum 24 */
  fret: number;
  /** @integer @minimum 1 @maximum 12 */
  from_string: number;
  /** @integer @minimum 1 @maximum 12 */
  to_string: number;
}

export interface Voicing {
  id: string;
  instrument: VoicingInstrument;
  /** Per-string fret; index 0 = string 1 (highest). null = not played, -1 = muted. @integer @minimum -1 @maximum 24 */
  frame: (number | null)[];
  fingering: Finger[];
  /** @integer @minimum 0 @maximum 24 */
  position: number;
  /** max(fretted) - min(fretted). @integer @minimum 0 */
  span: number;
  barre: BarreSpec | null;
  /** @integer @minimum 0 */
  open_strings: number;
  is_common_shape: boolean;
  /** e.g. "E-shape barre", "open C". */
  shape_name: string | null;
  /** From the scoring function in Section 2.2.2. */
  score: number;
  diagram_id: string | null;
  /** Piano only: pitches assigned to the left hand. @integer @minimum 0 @maximum 127 */
  left_hand: number[] | null;
  /** Piano only: pitches assigned to the right hand. @integer @minimum 0 @maximum 127 */
  right_hand: number[] | null;
}

export interface ChordEvent {
  id: string;
  tick_on: Ticks;
  tick_off: Ticks;
  time_on_s: Seconds;
  /** 0..11, C = 0. @integer @minimum 0 @maximum 11 */
  root_pc: number;
  root_step: Step;
  root_alter: Alter;
  quality: ChordQuality;
  /** Slash chord; null if root position. @integer @minimum 0 @maximum 11 */
  bass_pc: number | null;
  /** Scale degrees present, e.g. [9, 11, 13]. @integer @minimum 1 @maximum 13 */
  extensions: number[];
  /** Degrees deliberately dropped by the difficulty engine. @integer @minimum 1 @maximum 13 */
  omissions: number[];
  /** Rendered text, e.g. "Cmaj7/E". */
  label: string;
  /** @minimum 0 @maximum 1 */
  confidence: number;
  source: ChordSource;
  /** Populated for guitar parts. */
  voicing: Voicing | null;
}
