import { ConfigurationSchema } from '@jbrowse/core/configuration'

/**
 * #config SvJsonAdapter
 */
export default ConfigurationSchema(
  'SvJsonAdapter',
  {
    /**
     * #slot
     */
    svEndpoint: {
      type: 'string',
      defaultValue: 'http://localhost:5000/api/svs',
      description:
        'Base URL of the sv-tracks-backend /api/svs endpoint (refName/start/end query params are appended)',
    },
  },
  { explicitlyTyped: true },
)
