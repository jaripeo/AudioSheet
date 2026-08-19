/** Parts and instruments — ARCHITECTURE.md Section 3.4. */

import type { Note, Rest } from "./note";
import type { ChordEvent } from "./chord";

export type StemName =
  | "vocals"
  | "drums"
  | "bass"
  | "guitar"
  | "piano"
  | "other"
  | "mix";

export type PartKind = "pitched" | "percussion";

export type PartNotation = "standard" | "tab" | "standard+tab" | "percussion";

export type ClefSign = "G" | "F" | "C" | "percussion" | "TAB";

export interface Tuning {
  /** "Standard", "Drop D", "DADGAD", "Bass 4 Standard". */
  name: string;
  /** MIDI pitch of each open string; index 0 = string 1 (highest). @integer @minimum 0 @maximum 127 */
  strings: number[];
  /** Frets; 0 = none. @integer @minimum 0 @maximum 12 */
  capo: number;
}

export interface Clef {
  /** @integer @minimum 1 */
  staff: number;
  sign: ClefSign;
  /** Staff line the clef sits on. @integer @minimum 1 @maximum 5 */
  line: number;
  /** Octave transposition drawn with the clef (guitar treble = -1). @integer @minimum -2 @maximum 2 */
  octave_change: number;
}

export interface Instrument {
  /** General MIDI program. @integer @minimum 0 @maximum 127 */
  midi_program: number;
  /** Drums MUST be channel 9 (0-indexed). @integer @minimum 0 @maximum 15 */
  midi_channel: number;
  tuning: Tuning | null;
  /** @integer @minimum 1 @maximum 12 */
  string_count: number | null;
  /** @integer @minimum 1 @maximum 36 */
  fret_count: number | null;
}

export interface Part {
  id: string;
  name: string;
  abbreviation: string;
  stem: StemName;
  kind: PartKind;
  notation: PartNotation;
  clefs: Clef[];
  /** @integer @minimum 1 @maximum 2 */
  staff_count: number;
  /** Written versus sounding pitch. @integer */
  transpose_semitones: number;
  instrument: Instrument;
  present: boolean;
  loudness_lufs: number;
  notes: Note[];
  rests: Rest[];
  /** Usually populated only on the primary harmonic part. */
  chords: ChordEvent[];
}
