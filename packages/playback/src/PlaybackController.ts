/**
 * Transport state — ARCHITECTURE.md Section 4.4.
 *
 * The controller owns position in SECONDS. Both renderers ask it for ticks, and
 * every seconds/ticks conversion goes through the timing grid (INV-5). This is why
 * the cursor does not jump when the difficulty slider moves mid-playback: the
 * position is preserved in seconds and re-mapped.
 */

import type { TimingGrid } from "@audiosheet/schema";

/** Transport states. */
export type TransportState = "stopped" | "playing" | "paused";

/**
 * Convert seconds to ticks through the tempo map.
 *
 * @param grid - The timing grid.
 * @param seconds - Absolute seconds.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function secondsToTick(grid: TimingGrid, seconds: number): number {
  throw new Error("unimplemented: playback transport lands in Phase 2");
}

/**
 * Convert ticks to seconds through the tempo map.
 *
 * @param grid - The timing grid.
 * @param tick - Position in ticks.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function tickToSeconds(grid: TimingGrid, tick: number): number {
  throw new Error("unimplemented: playback transport lands in Phase 2");
}

/** Owns transport state and drives both cursors. */
export class PlaybackController {
  private state: TransportState = "stopped";
  private positionSeconds = 0;

  /** Return the current transport state. */
  getState(): TransportState {
    return this.state;
  }

  /** Return the current position in seconds. */
  getPositionSeconds(): number {
    return this.positionSeconds;
  }

  /**
   * Start or resume playback.
   *
   * @throws Always in Phase 0; lands in Phase 2.
   */
  play(): void {
    throw new Error("unimplemented: playback transport lands in Phase 2");
  }

  /**
   * Pause playback, keeping the position.
   *
   * @throws Always in Phase 0; lands in Phase 2.
   */
  pause(): void {
    throw new Error("unimplemented: playback transport lands in Phase 2");
  }

  /**
   * Seek to an absolute position.
   *
   * @param seconds - Target position in seconds.
   * @throws Always in Phase 0; lands in Phase 2.
   */
  seek(seconds: number): void {
    throw new Error("unimplemented: playback transport lands in Phase 2");
  }
}
