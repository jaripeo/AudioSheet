/**
 * Job binding: uploads a file, subscribes to the SSE progress stream, and exposes cancellation.
 *
 * Phase 1 implements this (ARCHITECTURE.md Section 5.3).
 */

/**
 * Return the current job state and controls.
 *
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function useJob(): never {
  throw new Error("unimplemented: useJob lands in Phase 1");
}
