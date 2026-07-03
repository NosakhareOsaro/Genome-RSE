import AdapterType from '@jbrowse/core/pluggableElementTypes/AdapterType'

import configSchema from './configSchema.js'
import SvJsonAdapter from './SvJsonAdapter.js'

export default function SvJsonAdapterF(pluginManager) {
  pluginManager.addAdapterType(
    () =>
      new AdapterType({
        name: 'SvJsonAdapter',
        configSchema,
        AdapterClass: SvJsonAdapter,
      }),
  )
}
