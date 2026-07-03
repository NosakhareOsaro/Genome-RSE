import { getSnapshot } from '@jbrowse/mobx-state-tree'
import { describe, expect, it } from 'vitest'

import svArcRendererConfigSchema from '../src/SvArcRenderer/configSchema.js'
import svJsonAdapterConfigSchema from '../src/SvJsonAdapter/configSchema.js'

/**
 * Regression test for a real bug found in end-to-end testing: JBrowse's
 * ConfigurationSchema collapses a config snapshot to `{}` -- dropping even
 * `type` -- when every slot value matches its schema default. If a config
 * schema's own `defaultValue` happened to equal a value a real config
 * actually uses, the adapter/renderer would silently fail to load in
 * jbrowse-web with "could not determine adapter type from adapter config
 * snapshot {}", even though unit tests that construct the adapter/renderer
 * class directly (bypassing JBrowse's config snapshot machinery) would
 * never catch it.
 */
function expectSnapshotSurvivesRealisticUsage(configSchema, realisticSnapshot) {
  const node = configSchema.create(realisticSnapshot)
  const snap = getSnapshot(node)
  expect(snap.type).toBe(configSchema.create({}).type)
  for (const [key, value] of Object.entries(realisticSnapshot)) {
    expect(snap[key]).toEqual(value)
  }
}

describe('config schema defaults never collide with realistic usage', () => {
  it('SvJsonAdapter: type survives when svEndpoint is set to a real-looking URL', () => {
    // This exact value is what demo/config.json and plugin/config.json use.
    // If it ever again matched svEndpoint's schema default, this test would
    // fail the same way loading the real plugin in jbrowse-web did.
    expectSnapshotSurvivesRealisticUsage(svJsonAdapterConfigSchema, {
      svEndpoint: 'http://localhost:5000/api/svs',
    })
  })

  it('SvArcRenderer: type survives when arcHeight is customized', () => {
    expectSnapshotSurvivesRealisticUsage(svArcRendererConfigSchema, {
      arcHeight: 120,
    })
  })

  it('SvArcRenderer: an all-default config is still handled safely even though it collapses to {}', () => {
    // Unlike the adapter, SvArcRendering.js has an explicit `|| 80` fallback
    // (see SvArcRendering.test.js) for exactly this case, so an all-default
    // renderer config collapsing to {} is a non-issue -- documented here so
    // the asymmetry with the adapter test above isn't mistaken for an
    // oversight.
    const node = svArcRendererConfigSchema.create({})
    expect(getSnapshot(node)).toEqual({})
  })
})
