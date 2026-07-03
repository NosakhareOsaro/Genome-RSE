import PluginManager from '@jbrowse/core/PluginManager'
import { describe, expect, it } from 'vitest'

import SvTracksPlugin from '../src/index.js'

describe('SvTracksPlugin', () => {
  it('registers SvJsonAdapter and SvArcRenderer with a real PluginManager', () => {
    const pluginManager = new PluginManager([new SvTracksPlugin()])
    pluginManager.createPluggableElements()
    pluginManager.configure()

    const adapterType = pluginManager.getAdapterType('SvJsonAdapter')
    expect(adapterType).toBeDefined()
    expect(adapterType.name).toBe('SvJsonAdapter')

    const rendererType = pluginManager.getRendererType('SvArcRenderer')
    expect(rendererType).toBeDefined()
    expect(rendererType.name).toBe('SvArcRenderer')
  })
})
