import { describe, expect, it } from 'vitest'

import {
  colorForSvType,
  getBezierArcPath,
  isSameContigSv,
  SV_TYPE_COLORS,
} from '../src/util/arcGeometry.js'

describe('getBezierArcPath', () => {
  it('builds a cubic bezier path peaking at the given height', () => {
    expect(getBezierArcPath(10, 50, 80)).toBe('M 10 0 C 10 80, 50 80, 50 0')
  })

  it('handles left/right being reversed without erroring', () => {
    expect(getBezierArcPath(50, 10, 80)).toBe('M 50 0 C 50 80, 10 80, 10 0')
  })
})

describe('colorForSvType', () => {
  it.each(Object.entries(SV_TYPE_COLORS))('returns the mapped color for %s', (svType, color) => {
    expect(colorForSvType(svType)).toBe(color)
  })

  it('falls back to grey for an unrecognized type', () => {
    expect(colorForSvType('CNV')).toBe('#999999')
  })

  it('falls back to grey for undefined', () => {
    expect(colorForSvType(undefined)).toBe('#999999')
  })
})

describe('isSameContigSv', () => {
  it('is true when refName and mateRefName match', () => {
    expect(isSameContigSv({ refName: 'ctgA', mateRefName: 'ctgA' })).toBe(true)
  })

  it('is false when refName and mateRefName differ', () => {
    expect(isSameContigSv({ refName: 'ctgA', mateRefName: 'ctgB' })).toBe(false)
  })
})
