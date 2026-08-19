/**
 * Play, pause and seek. AlphaSynth is the clock master for both views; position is held in seconds so the cursor survives a difficulty change mid-playback (Section 4.4).
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3). The file exists now so
 * the Section 5.1 tree is complete.
 */

/**
 * Render the component.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function TransportBar(): never {
  throw new Error("unimplemented: TransportBar lands in Phase 2");
}
