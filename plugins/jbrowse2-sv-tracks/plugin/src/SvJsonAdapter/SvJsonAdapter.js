import { readConfObject } from '@jbrowse/core/configuration'
import { BaseFeatureDataAdapter } from '@jbrowse/core/data_adapters/BaseAdapter'
// SimpleFeature must come from the '@jbrowse/core/util' barrel, not the
// '@jbrowse/core/util/simpleFeature' subpath -- the latter isn't one of
// the paths JBrowse re-exports via window.JBrowseExports for external
// plugins (confirmed by loading this plugin in a real jbrowse-web and
// finding that subpath undefined at runtime, despite resolving fine
// against the local @jbrowse/core npm package in unit tests).
import { SimpleFeature } from '@jbrowse/core/util'
import { ObservableCreate } from '@jbrowse/core/util/rxjs'

/**
 * Fetches SV records from the sv-tracks-backend Flask API and converts them
 * into SimpleFeature objects. Each feature is a single 1bp breakpoint (its
 * own `start`/`end`) plus a `mateRefName`/`mateStart`/`mateEnd` describing
 * the SV's other end -- SvArcRenderer draws an arc between them when both
 * ends share a refName, or a marker when they don't (see SvArcRendering.js).
 */
export default class SvJsonAdapter extends BaseFeatureDataAdapter {
  buildUrl(refName, start, end) {
    const base = readConfObject(this.config, 'svEndpoint')
    const params = new URLSearchParams({
      refName,
      start: String(start),
      end: String(end),
    })
    return `${base}?${params.toString()}`
  }

  async getRefNames(_opts = {}) {
    // Not known ahead of time without an extra backend round trip; see
    // hasDataForRefName override below, which makes this non-blocking.
    return []
  }

  // The base implementation gates getFeatures() behind
  // getRefNames().includes(refName), which would always be false given the
  // empty array above. The backend already returns [] for unknown contigs,
  // so there's no correctness loss in skipping that gate here.
  async hasDataForRefName(_refName, _opts = {}) {
    return true
  }

  getFeatures(region, _opts = {}) {
    const { refName, start, end } = region
    return ObservableCreate(async observer => {
      let response
      try {
        response = await fetch(this.buildUrl(refName, start, end))
      } catch (error) {
        observer.error(error)
        return
      }
      if (!response.ok) {
        observer.error(
          new Error(`sv-tracks-backend request failed: ${response.status}`),
        )
        return
      }
      const records = await response.json()
      for (const record of records) {
        observer.next(
          new SimpleFeature({
            id: record.id,
            data: record,
          }),
        )
      }
      observer.complete()
    })
  }

  freeResources() {}
}
