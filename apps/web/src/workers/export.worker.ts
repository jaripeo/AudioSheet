/**
 * Export worker — ARCHITECTURE.md Section 4.3, Phase 2.
 *
 * MusicXML serialisation runs off the main thread so a long export never blocks
 * the score view or the playback cursor.
 */

import type { ScoreDocument } from "@audiosheet/schema";

/** Formats the worker can produce. */
export type ExportFormat = "musicxml" | "mxl" | "midi" | "practice-midi";

/** Request sent to the worker. */
export interface ExportRequest {
  readonly document: ScoreDocument;
  readonly format: ExportFormat;
}

/**
 * Install the message handler.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function registerWorker(): void {
  throw new Error("unimplemented: the export worker lands in Phase 2");
}
