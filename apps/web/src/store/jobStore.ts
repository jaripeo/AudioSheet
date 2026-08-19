/**
 * Job state — ARCHITECTURE.md Section 5.2, Phase 1.
 *
 * Mirrors the sidecar's per-stage SSE progress so the UI can show which of the nine
 * stages is running. Demucs dominates wall-clock and must report at >= 2 Hz, or the
 * UI looks frozen (Section 1.5).
 */

import type { ProgressEvent } from "@audiosheet/ipc";

/** Lifecycle of a transcription job. */
export type JobState = "idle" | "uploading" | "running" | "done" | "failed" | "cancelled";

/** What the store holds. */
export interface JobStoreState {
  readonly state: JobState;
  readonly jobId: string | null;
  readonly events: readonly ProgressEvent[];
  readonly error: { readonly code: string; readonly message: string } | null;
}

/**
 * Create the store.
 *
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function createJobStore(): never {
  throw new Error("unimplemented: the job store lands in Phase 1");
}
