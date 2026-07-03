import { SimpleFeature } from '@jbrowse/core/util'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { describe, expect, it } from 'vitest'

import configSchema from '../src/SvArcRenderer/configSchema.js'
import SvArcRendering from '../src/SvArcRenderer/SvArcRendering.js'

const REGION = { refName: 'ctgA', start: 0, end: 50001 }
const BP_PER_PX = 100

function featureMap(records) {
  return new Map(records.map(r => [r.id, new SimpleFeature({ id: r.id, data: r })]))
}

describe('SvArcRendering', () => {
  it('renders a bezier arc path for a same-contig SV', () => {
    const features = featureMap([
      {
        id: 'sv1_del',
        refName: 'ctgA',
        start: 9999,
        end: 10000,
        mateRefName: 'ctgA',
        mateStart: 11999,
        mateEnd: 12000,
        svType: 'DEL',
      },
    ])

    render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({}),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
      }),
    )

    const path = screen.getByTestId('sv-arc-path')
    expect(path).toBeInTheDocument()
    expect(path.getAttribute('data-sv-type')).toBe('DEL')
    expect(path.getAttribute('d')).toMatch(/^M \d+(\.\d+)? 0 C/)
    expect(screen.queryByTestId('sv-bnd-marker')).not.toBeInTheDocument()
  })

  it('renders a marker (not an arc) for a cross-contig BND', () => {
    const features = featureMap([
      {
        id: 'sv4_bnd_1',
        refName: 'ctgA',
        start: 39999,
        end: 40000,
        mateRefName: 'ctgB',
        mateStart: 2999,
        mateEnd: 3000,
        svType: 'BND',
      },
    ])

    render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({}),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
      }),
    )

    const marker = screen.getByTestId('sv-bnd-marker')
    expect(marker).toBeInTheDocument()
    expect(marker.getAttribute('data-sv-type')).toBe('BND')
    expect(marker.textContent).toContain('ctgB:3000')
    expect(screen.queryByTestId('sv-arc-path')).not.toBeInTheDocument()
  })

  it('renders one element per feature', () => {
    const features = featureMap([
      {
        id: 'sv1_del',
        refName: 'ctgA',
        start: 9999,
        end: 10000,
        mateRefName: 'ctgA',
        mateStart: 11999,
        mateEnd: 12000,
        svType: 'DEL',
      },
      {
        id: 'sv2_dup',
        refName: 'ctgA',
        start: 19999,
        end: 20000,
        mateRefName: 'ctgA',
        mateStart: 22499,
        mateEnd: 22500,
        svType: 'DUP',
      },
    ])

    render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({}),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
      }),
    )

    expect(screen.getAllByTestId('sv-arc-path')).toHaveLength(2)
  })

  it('renders a wrapping svg sized to the region width, unless exportSVG', () => {
    const features = featureMap([])

    const { rerender } = render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({}),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
      }),
    )
    const svg = screen.getByTestId('sv-arc-svg')
    expect(svg.getAttribute('width')).toBe(String((REGION.end - REGION.start) / BP_PER_PX))

    rerender(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({}),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
        exportSVG: true,
      }),
    )
    expect(screen.queryByTestId('sv-arc-svg')).not.toBeInTheDocument()
  })

  it('caps the arc peak height at the display height', () => {
    const features = featureMap([
      {
        id: 'sv1_del',
        refName: 'ctgA',
        start: 0,
        end: 1,
        mateRefName: 'ctgA',
        mateStart: 999,
        mateEnd: 1000,
        svType: 'DEL',
      },
    ])

    render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({ arcHeight: 500 }),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 30,
      }),
    )

    const path = screen.getByTestId('sv-arc-path')
    expect(path.getAttribute('d')).toContain(' 30,')
  })

  it('falls back to the default peak height when arcHeight is falsy', () => {
    const features = featureMap([
      {
        id: 'sv1_del',
        refName: 'ctgA',
        start: 0,
        end: 1,
        mateRefName: 'ctgA',
        mateStart: 999,
        mateEnd: 1000,
        svType: 'DEL',
      },
    ])

    render(
      React.createElement(SvArcRendering, {
        features,
        config: configSchema.create({ arcHeight: 0 }),
        regions: [REGION],
        bpPerPx: BP_PER_PX,
        height: 100,
      }),
    )

    const path = screen.getByTestId('sv-arc-path')
    expect(path.getAttribute('d')).toContain(' 80,')
  })
})
