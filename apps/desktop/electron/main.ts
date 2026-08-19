/**
 * Electron main process — ARCHITECTURE.md Sections 4.1 and 5.3, Phase 8.
 *
 * Responsibilities:
 *   - spawn the Python core as a sidecar, health-check it, and kill it gracefully
 *     on quit;
 *   - create the window with contextIsolation on, nodeIntegration off, sandbox on;
 *   - install a Content Security Policy with no `connect-src` beyond `self`, which
 *     enforces INV-1 (offline) at the platform level rather than by convention.
 *
 * Phase 8 installs electron and implements this. The file exists now so the
 * Section 5.1 tree is complete and the security posture is recorded where it will
 * be implemented.
 */

/** Loopback host the sidecar is required to bind. */
export const SIDECAR_HOST = "127.0.0.1";

/** How long to wait for the sidecar's /health to answer, in milliseconds. */
export const SIDECAR_HEALTH_TIMEOUT_MS = 15_000;

/** How long to wait for a graceful sidecar exit before SIGKILL, in milliseconds. */
export const SIDECAR_SHUTDOWN_GRACE_MS = 3_000;

/**
 * Content Security Policy for the renderer.
 *
 * `connect-src 'self'` is the platform-level half of INV-1: even a bug that tried
 * to reach the network could not.
 */
export const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "media-src 'self' blob:",
  "connect-src 'self'",
  "object-src 'none'",
  "frame-ancestors 'none'",
  "base-uri 'none'",
].join("; ");

/** Window security flags; every one of these is required (Section 4.1). */
export const WEB_PREFERENCES = {
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: true,
  webSecurity: true,
} as const;

/**
 * Spawn the bundled Python core and wait for it to report healthy.
 *
 * @returns The port and bearer token the renderer should use.
 * @throws Always in Phase 0; lands in Phase 8.
 */
export function startSidecar(): Promise<{ port: number; token: string }> {
  throw new Error("unimplemented: the Electron shell lands in Phase 8");
}

/**
 * Create the application window.
 *
 * @throws Always in Phase 0; lands in Phase 8.
 */
export function createWindow(): void {
  throw new Error("unimplemented: the Electron shell lands in Phase 8");
}
