/**
 * UI state — ARCHITECTURE.md Section 4.4, Phase 2.
 *
 * Kept separate from the score store so that opening a drawer or selecting a note
 * cannot invalidate score selectors and trigger a re-render of the notation.
 */

import type { RenderTarget } from "@audiosheet/schema";

/** What the UI is showing and what the user has selected. */
export interface UiState {
  readonly view: RenderTarget;
  readonly selectedNoteId: string | null;
  readonly diagnosticsOpen: boolean;
  readonly showGhostNotes: boolean;
  readonly soloStems: readonly string[];
}

/**
 * Create the store.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function createUiStore(): never {
  throw new Error("unimplemented: the UI store lands in Phase 2");
}
