import { firstValueFrom } from 'rxjs'
import { toArray } from 'rxjs/operators'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import configSchema from '../src/SvJsonAdapter/configSchema.js'
import SvJsonAdapter from '../src/SvJsonAdapter/SvJsonAdapter.js'

const SAMPLE_RECORDS = [
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
    id: 'sv4_bnd_1',
    refName: 'ctgA',
    start: 39999,
    end: 40000,
    mateRefName: 'ctgB',
    mateStart: 2999,
    mateEnd: 3000,
    svType: 'BND',
  },
]

function makeAdapter(endpoint = 'http://localhost:5000/api/svs') {
  const config = configSchema.create({ svEndpoint: endpoint })
  return new SvJsonAdapter(config)
}

describe('SvJsonAdapter', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('builds the SV endpoint URL with region query params', () => {
    const adapter = makeAdapter()
    const url = adapter.buildUrl('ctgA', 100, 200)
    expect(url).toBe('http://localhost:5000/api/svs?refName=ctgA&start=100&end=200')
  })

  it('always reports having data for a ref name', async () => {
    const adapter = makeAdapter()
    await expect(adapter.hasDataForRefName('anything')).resolves.toBe(true)
  })

  it('returns no known ref names upfront', async () => {
    const adapter = makeAdapter()
    await expect(adapter.getRefNames()).resolves.toEqual([])
  })

  it('converts each backend record into a SimpleFeature', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(SAMPLE_RECORDS),
    })
    const adapter = makeAdapter()

    const features = await firstValueFrom(
      adapter.getFeatures({ refName: 'ctgA', start: 0, end: 50001 }).pipe(toArray()),
    )

    expect(features).toHaveLength(2)
    expect(features[0].id()).toBe('sv1_del')
    expect(features[0].get('svType')).toBe('DEL')
    expect(features[0].get('mateRefName')).toBe('ctgA')
    expect(features[1].id()).toBe('sv4_bnd_1')
    expect(features[1].get('mateRefName')).toBe('ctgB')
  })

  it('filters out records the endpoint returns that do not overlap the requested region', async () => {
    // Simulates a static-file endpoint (e.g. the GitHub Pages demo) that
    // can't filter server-side and just returns everything.
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(SAMPLE_RECORDS),
    })
    const adapter = makeAdapter()

    const features = await firstValueFrom(
      adapter.getFeatures({ refName: 'ctgA', start: 0, end: 15000 }).pipe(toArray()),
    )

    expect(features.map(f => f.id())).toEqual(['sv1_del'])
  })

  it('requests the region passed to getFeatures', async () => {
    fetch.mockResolvedValue({ ok: true, json: () => Promise.resolve([]) })
    const adapter = makeAdapter()

    await firstValueFrom(
      adapter.getFeatures({ refName: 'ctgB', start: 10, end: 20 }).pipe(toArray()),
    )

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:5000/api/svs?refName=ctgB&start=10&end=20',
    )
  })

  it('errors the observable when the response is not ok', async () => {
    fetch.mockResolvedValue({ ok: false, status: 500 })
    const adapter = makeAdapter()

    await expect(
      firstValueFrom(
        adapter.getFeatures({ refName: 'ctgA', start: 0, end: 100 }).pipe(toArray()),
      ),
    ).rejects.toThrow('sv-tracks-backend request failed: 500')
  })

  it('errors the observable when fetch itself rejects', async () => {
    fetch.mockRejectedValue(new Error('network down'))
    const adapter = makeAdapter()

    await expect(
      firstValueFrom(
        adapter.getFeatures({ refName: 'ctgA', start: 0, end: 100 }).pipe(toArray()),
      ),
    ).rejects.toThrow('network down')
  })

  it('freeResources is a no-op that does not throw', () => {
    const adapter = makeAdapter()
    expect(() => adapter.freeResources()).not.toThrow()
  })
})
