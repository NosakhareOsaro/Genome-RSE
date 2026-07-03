import configSchema from './configSchema.js'
import SvArcRenderer from './SvArcRenderer.js'
import SvArcRendering from './SvArcRendering.js'

// A static import (not lazy/dynamic) is required here: rollup can't produce
// a single UMD bundle if any module is dynamically imported (code-splitting
// isn't supported for UMD/IIFE output).
export default function SvArcRendererF(pluginManager) {
  pluginManager.addRendererType(
    () =>
      new SvArcRenderer({
        name: 'SvArcRenderer',
        ReactComponent: SvArcRendering,
        configSchema,
        pluginManager,
      }),
  )
}
