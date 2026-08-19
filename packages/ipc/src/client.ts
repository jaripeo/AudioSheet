/**
 * Typed client for the local service — ARCHITECTURE.md Section 5.2.
 *
 * The service is loopback-only and bearer-token protected. INV-1: the client talks
 * to 127.0.0.1 and nothing else, and the desktop shell's CSP has no `connect-src`
 * beyond `self`, so a stray external request cannot even be attempted.
 */

import type { ScoreDocument } from "@audiosheet/schema";

/** The only host the client will talk to. */
export const SERVICE_HOST = "127.0.0.1";

/** A per-stage progress event from the SSE stream. */
export interface ProgressEvent {
  readonly stage: string;
  readonly progress: number;
  readonly message: string;
}

/** The wire form of every non-2xx response. */
export interface ServiceError {
  readonly code: string;
  readonly message: string;
  readonly detail: Record<string, unknown>;
}

/** Connection parameters the shell reads from the sidecar's runtime directory. */
export interface ClientConfig {
  readonly port: number;
  readonly token: string;
}

/**
 * Submit an audio file and return the job id.
 *
 * @param config - Connection parameters.
 * @param file - The audio file to transcribe.
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function createJob(config: ClientConfig, file: Blob): Promise<string> {
  throw new Error("unimplemented: the service client lands in Phase 1");
}

/**
 * Subscribe to a job's progress stream.
 *
 * @param config - Connection parameters.
 * @param jobId - The job to watch.
 * @param listener - Called for each progress event.
 * @returns An unsubscribe function.
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function watchJob(
  config: ClientConfig,
  jobId: string,
  listener: (event: ProgressEvent) => void,
): () => void {
  throw new Error("unimplemented: the service client lands in Phase 1");
}

/**
 * Fetch a finished document.
 *
 * @param config - Connection parameters.
 * @param jobId - The completed job.
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function getDocument(config: ClientConfig, jobId: string): Promise<ScoreDocument> {
  throw new Error("unimplemented: the service client lands in Phase 1");
}

/**
 * Request cancellation of a running job.
 *
 * @param config - Connection parameters.
 * @param jobId - The job to cancel.
 * @throws Always in Phase 0; lands in Phase 1.
 */
export function cancelJob(config: ClientConfig, jobId: string): Promise<void> {
  throw new Error("unimplemented: the service client lands in Phase 1");
}
