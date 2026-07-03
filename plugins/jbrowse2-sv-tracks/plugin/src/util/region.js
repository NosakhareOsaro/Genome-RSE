/**
 * True if a record's own span [start, end) overlaps a query region on the
 * same refName. Standard half-open interval overlap check.
 *
 * Applied client-side in SvJsonAdapter regardless of whether the backend
 * already filtered server-side (the Flask API does) -- this makes the
 * adapter work equally well against a static JSON file with no filtering
 * capability at all (e.g. the GitHub Pages demo, which has no backend to
 * query), not just the real Flask API.
 */
export function recordOverlapsRegion(record, region) {
  return (
    record.refName === region.refName &&
    record.start < region.end &&
    record.end > region.start
  )
}
