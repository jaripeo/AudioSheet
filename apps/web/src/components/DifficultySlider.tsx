/**
 * The three-position difficulty slider. Moving it re-runs reduce() in a Web Worker and must repaint within 400 ms p95 (INV-7); it never re-runs a model (INV-6).
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3). The file exists now so
 * the Section 5.1 tree is complete.
 */

/**
 * Render the component.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function DifficultySlider(): never {
  throw new Error("unimplemented: DifficultySlider lands in Phase 2");
}
