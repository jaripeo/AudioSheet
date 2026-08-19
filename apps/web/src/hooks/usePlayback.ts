/**
 * Transport binding. Playback position is kept in seconds and re-mapped to ticks through the timing grid (INV-5), so the cursor never jumps when the difficulty changes.
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3).
 */

/**
 * Return transport state and controls.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function usePlayback(): never {
  throw new Error("unimplemented: usePlayback lands in Phase 2");
}
