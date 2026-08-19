/**
 * Preload bridge — ARCHITECTURE.md Section 4.1, Phase 8.
 *
 * Exposes the smallest possible surface over contextBridge: the sidecar's port and
 * token, and a file-open dialog. Nothing else. The renderer never gets `require`,
 * `child_process`, or arbitrary IPC.
 */

/** The only members the renderer may see. */
export interface AudioSheetBridge {
  /** Connection parameters for the loopback service. */
  readonly service: { readonly port: number; readonly token: string };
  /** Open a native file picker limited to .mp3 and .wav. */
  readonly pickAudioFile: () => Promise<string | null>;
  /** Read a vendored model or soundfont from the app bundle. */
  readonly readResource: (relativePath: string) => Promise<Uint8Array>;
}

/** Extensions the file picker accepts (Section 1.3). */
export const ACCEPTED_EXTENSIONS = ["mp3", "wav"] as const;

/**
 * Install the bridge on `window.audiosheet`.
 *
 * @throws Always in Phase 0; lands in Phase 8.
 */
export function exposeBridge(): void {
  throw new Error("unimplemented: the preload bridge lands in Phase 8");
}
