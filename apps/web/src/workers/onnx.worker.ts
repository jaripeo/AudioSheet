/**
 * ONNX worker — ARCHITECTURE.md Section 4.2, browser target, Phase 8.
 *
 * The browser build has no Demucs: WASM separation is ~10-20x realtime and blows
 * the memory budget. It transcribes the full mix directly with basic-pitch and warns
 * the user that accuracy is reduced (W_SEPARATION_SKIPPED).
 *
 * Models are read from the Service Worker's precache, never fetched (INV-1).
 */

/** Execution providers, in preference order, for onnxruntime-web. */
export const EXECUTION_PROVIDERS = ["wasm"] as const;

/** Models the browser target ships (Section 4.2). */
export const BROWSER_MODELS = ["basic-pitch", "crepe-tiny", "beat-downbeat"] as const;

/**
 * Install the message handler.
 *
 * @throws Always in Phase 0; lands in Phase 8.
 */
export function registerWorker(): void {
  throw new Error("unimplemented: the browser ONNX worker lands in Phase 8");
}
