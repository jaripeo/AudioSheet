/**
 * Per-stage progress for the nine-stage pipeline, driven by the sidecar's SSE stream. Separation dominates wall-clock and reports at >= 2 Hz (Section 1.5).
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3). The file exists now so
 * the Section 5.1 tree is complete.
 */

/**
 * Render the component.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function ProgressPanel(): never {
  throw new Error("unimplemented: ProgressPanel lands in Phase 2");
}
