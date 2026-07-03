import { ConfigurationSchema } from '@jbrowse/core/configuration'

/**
 * #config SvJsonAdapter
 *
 * `defaultValue` is deliberately an obviously-nonfunctional placeholder,
 * not a real-looking endpoint. JBrowse's ConfigurationSchema collapses a
 * config snapshot to `{}` (dropping even `type`) when every slot's value
 * matches its schema default -- if this default were a real endpoint URL
 * and a user's config happened to set the same value, the adapter would
 * silently fail to load with "could not determine adapter type from
 * adapter config snapshot {}". A placeholder that no real config would
 * ever intentionally match avoids the collision entirely. (Found by
 * hitting exactly this failure in end-to-end testing against a real
 * jbrowse-web build -- every other JBrowse core adapter's configSchema
 * uses obviously-fake placeholder defaults for the same reason.)
 */
export default ConfigurationSchema(
  'SvJsonAdapter',
  {
    /**
     * #slot
     */
    svEndpoint: {
      type: 'string',
      defaultValue: '/path/to/sv-tracks-backend/api/svs',
      description:
        'Base URL of the sv-tracks-backend /api/svs endpoint (refName/start/end query params are appended)',
    },
  },
  { explicitlyTyped: true },
)
