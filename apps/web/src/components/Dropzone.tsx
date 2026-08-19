/**
 * File dropzone. Accepts .mp3 and .wav only, and rejects by magic bytes rather than extension once the sidecar has sniffed the file (Section 1.3). Surfaces E_INGEST_FORMAT and E_INGEST_LIMIT with the specific limit that was exceeded.
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3). The file exists now so
 * the Section 5.1 tree is complete.
 */

/**
 * Render the component.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function Dropzone(): never {
  throw new Error("unimplemented: Dropzone lands in Phase 2");
}
