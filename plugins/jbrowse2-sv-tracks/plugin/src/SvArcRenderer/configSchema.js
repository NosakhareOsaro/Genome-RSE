import { ConfigurationSchema } from '@jbrowse/core/configuration'

/**
 * #config SvArcRenderer
 */
export default ConfigurationSchema(
  'SvArcRenderer',
  {
    /**
     * #slot
     */
    arcHeight: {
      type: 'number',
      defaultValue: 80,
      description:
        'Peak height in pixels of the bezier arc connecting two same-contig breakpoints',
    },
  },
  { explicitlyTyped: true },
)
