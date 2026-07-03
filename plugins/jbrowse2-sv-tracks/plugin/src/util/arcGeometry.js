/**
 * Pure geometry/styling helpers for SvArcRendering, deliberately kept free
 * of @jbrowse/core and React imports so they're trivial to unit test.
 */

/**
 * A cubic bezier arc path (SVG `d` attribute) connecting two x-coordinates
 * at y=0, peaking at `height`. Same curve shape JBrowse2's own official
 * "arc" plugin uses for its LinearArcDisplay.
 */
export function getBezierArcPath(leftPx, rightPx, height) {
  return `M ${leftPx} 0 C ${leftPx} ${height}, ${rightPx} ${height}, ${rightPx} 0`
}

/** Colors keyed by SV type; falls back to grey for unrecognized types. */
export const SV_TYPE_COLORS = {
  DEL: '#e41a1c',
  DUP: '#377eb8',
  INV: '#4daf4a',
  BND: '#984ea3',
}

export function colorForSvType(svType) {
  return SV_TYPE_COLORS[svType] ?? '#999999'
}

/**
 * True if both breakpoints of an SV are on the same reference sequence, and
 * so can be drawn as a single arc within one linear view. Takes a plain
 * {refName, mateRefName} shape rather than a JBrowse Feature so it stays
 * framework-agnostic.
 */
export function isSameContigSv({ refName, mateRefName }) {
  return refName === mateRefName
}
