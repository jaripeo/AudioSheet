/**
 * AlphaSynth bridge — ARCHITECTURE.md Section 4.1.
 *
 * AlphaSynth is the clock master for BOTH views; VexFlow's cursor is a follower
 * drawn on an overlay canvas. Using two playback engines would desynchronise them.
 *
 * The vendored SoundFont2 bank is loaded from disk (INV-1: never fetched).
 */

import type { ScoreDocument } from "@audiosheet/schema";

/** A position report from the synth clock. */
export interface ClockTick {
  readonly seconds: number;
  readonly endSeconds: number;
}

/**
 * Load the vendored General MIDI soundfont.
 *
 * @param soundfontBytes - The bank, read from `models/soundfont/gm.sf2`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function loadSoundfont(soundfontBytes: Uint8Array): void {
  throw new Error("unimplemented: the AlphaSynth bridge lands in Phase 2");
}

/**
 * Load a document for playback.
 *
 * @param doc - The reduced document.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function loadScore(doc: ScoreDocument): void {
  throw new Error("unimplemented: the AlphaSynth bridge lands in Phase 2");
}

/**
 * Subscribe to clock ticks.
 *
 * @param listener - Called on each position report.
 * @returns An unsubscribe function.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function onClockTick(listener: (tick: ClockTick) => void): () => void {
  throw new Error("unimplemented: the AlphaSynth bridge lands in Phase 2");
}
