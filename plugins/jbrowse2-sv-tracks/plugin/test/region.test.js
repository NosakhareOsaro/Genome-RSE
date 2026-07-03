import { describe, expect, it } from 'vitest'

import { recordOverlapsRegion } from '../src/util/region.js'

const REGION = { refName: 'ctgA', start: 10000, end: 20000 }

describe('recordOverlapsRegion', () => {
  it('is true when the record is fully inside the region', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 12000, end: 13000 }, REGION)).toBe(
      true,
    )
  })

  it('is true when the record partially overlaps the start boundary', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 9000, end: 10001 }, REGION)).toBe(true)
  })

  it('is true when the record partially overlaps the end boundary', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 19999, end: 21000 }, REGION)).toBe(true)
  })

  it('is false when the record ends exactly at the region start (half-open, no overlap)', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 9000, end: 10000 }, REGION)).toBe(false)
  })

  it('is false when the record starts exactly at the region end (half-open, no overlap)', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 20000, end: 21000 }, REGION)).toBe(
      false,
    )
  })

  it('is false when the record is entirely before the region', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 0, end: 100 }, REGION)).toBe(false)
  })

  it('is false when the record is entirely after the region', () => {
    expect(recordOverlapsRegion({ refName: 'ctgA', start: 30000, end: 31000 }, REGION)).toBe(
      false,
    )
  })

  it('is false when the refName differs, even with matching coordinates', () => {
    expect(recordOverlapsRegion({ refName: 'ctgB', start: 12000, end: 13000 }, REGION)).toBe(
      false,
    )
  })
})
