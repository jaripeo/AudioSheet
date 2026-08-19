/**
 * Application shell — ARCHITECTURE.md Sections 4.1 and 5.3, Phase 2.
 *
 * Layout: dropzone and progress until a document exists, then the score and tab
 * views with the transport bar, the difficulty slider, the waveform strip and the
 * note inspector.
 *
 * Accessibility is a Phase 8 gate, not an afterthought: full keyboard control of
 * transport and slider, ARIA-labelled score regions, prefers-reduced-motion,
 * prefers-color-scheme, and a screen-reader summary per measure.
 */

/**
 * Render the application shell.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function App(): never {
  throw new Error("unimplemented: the application shell lands in Phase 2");
}
