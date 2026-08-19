/**
 * Service Worker — ARCHITECTURE.md Section 4.2, Phase 8.
 *
 * Two jobs:
 *   1. precache every model and asset so the PWA target works with no network;
 *   2. return 504 for any cross-origin request, which makes INV-1 observable at
 *      runtime instead of merely intended.
 *
 * This is the second of two layers: the Electron shell's CSP is the first. Two
 * independent mechanisms, because "we are offline" is a promise to the user.
 */

/** Cache name; bump to invalidate the precache after a model change. */
export const CACHE_NAME = "audiosheet-v1";

/** Status returned for any request that leaves the origin. */
export const BLOCKED_STATUS = 504;

/** Everything the PWA needs on disk before it can work offline. */
export const PRECACHE_PATHS: readonly string[] = [
  "./",
  "./index.html",
  "./models/manifest.json",
  "./models/basic_pitch/nmp.onnx",
  "./models/crepe/crepe_tiny.onnx",
  "./models/beat/beat_downbeat.onnx",
  "./models/soundfont/gm.sf2",
];

/**
 * Return whether a request is allowed to proceed.
 *
 * @param requestUrl - The request URL.
 * @param originUrl - The service worker's own origin.
 * @returns True only for same-origin requests.
 */
export function isSameOrigin(requestUrl: string, originUrl: string): boolean {
  try {
    return new URL(requestUrl, originUrl).origin === new URL(originUrl).origin;
  } catch {
    return false;
  }
}

/**
 * Install the fetch, install and activate handlers.
 *
 * @throws Always in Phase 0; lands in Phase 8.
 */
export function registerHandlers(): void {
  throw new Error("unimplemented: the offline Service Worker lands in Phase 8");
}
