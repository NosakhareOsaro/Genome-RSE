# jbrowse2-sv-tracks

A JBrowse2 custom track plugin that renders structural-variant (SV) arcs
from VCF data, backed by a small Flask REST API. Phase 3 of the
GenomeRSE portfolio project.

## Architecture

```
Flask backend (backend/)          JBrowse2 plugin (plugin/)
  pysam parses a VCF's SV    -->    SvJsonAdapter fetches /api/svs
  records (DEL/DUP/INV/BND)         and builds JBrowse Features
  into JSON over /api/svs                    |
                                              v
                                     SvArcRenderer draws an SVG
                                     bezier arc between each SV's
                                     two breakpoints (same-contig),
                                     or a marker + label pointing at
                                     the mate contig (cross-contig
                                     BND -- one linear view can't
                                     show both ends as a single arc)
```

- [`backend/`](backend) — Flask API; see [`backend/README.md`](backend/README.md).
- [`plugin/`](plugin) — the JBrowse2 plugin itself (plain JavaScript, Rollup-built UMD bundle).
- [`demo/`](demo) — GitHub Pages demo assembly (see below).
- [`workflow/`](workflow) — Dockstore-compatible WDL workflow for preparing VCF/BAM data.
- [`docs/blog-post.md`](docs/blog-post.md) — technical write-up.

## Local development

```bash
# Terminal 1: backend
cd backend && pip install -e ".[dev]" && FLASK_APP=app.py flask run

# Terminal 2: plugin build + serve
cd plugin && npm install && npm run dev   # rollup --watch + serve on :9000

# Terminal 3: static-serve the sample reference data referenced by plugin/config.json
npx serve backend/data --cors --listen 8082
```

Then use `@jbrowse/cli` (or any jbrowse-web checkout) with
`plugin/config.json` to preview the track locally.

## Three real bugs only found by testing against a real jbrowse-web

All unit tests passed and the Rollup build succeeded, but the plugin
still failed to render when actually loaded in jbrowse-web. In order
found:

1. **`FeatureRendererType` default-import mismatch.** Against the
   local `@jbrowse/core` npm package (unit tests), a default import
   unwraps correctly. Against a real jbrowse-web build,
   `window.JBrowseExports` wraps that specific module as
   `{ default: FeatureRendererType }` — unlike e.g. `@jbrowse/core/Plugin`,
   which JBrowse unwraps to the bare class. This crashed the whole page
   (`Class extends value #<Object> is not a constructor or null`).
2. **`SimpleFeature` imported from the wrong subpath.**
   `@jbrowse/core/util/simpleFeature` resolves fine against the local
   npm package but isn't one of the paths JBrowse re-exports for
   external plugins — `undefined` at runtime. Fixed by importing it
   from the `@jbrowse/core/util` barrel instead.
3. **A config schema default that coincided with real usage.** JBrowse's
   `ConfigurationSchema` collapses a config snapshot to `{}` (dropping
   even `type`) when every slot matches its schema default. The
   `svEndpoint` default was set to the same URL the demo configs
   actually use, so the adapter's config silently collapsed and it
   failed with "could not determine adapter type from adapter config
   snapshot {}". Every built-in JBrowse adapter avoids this by using an
   obviously-nonfunctional placeholder default; fixed the same way.

Bugs 1 and 2 are specifically about `window.JBrowseExports` shape
mismatches that only exist when a plugin runs as an external UMD bundle
inside real jbrowse-web — no unit test against the local `@jbrowse/core`
npm package can catch them. That's why this plugin's verification
includes a non-optional end-to-end step: assemble a real jbrowse-web
via `@jbrowse/cli`, load the built plugin in headless Chromium via
Puppeteer, and assert on the actual rendered DOM (not just "no console
errors"). See `docs/images/sv-arcs-e2e-screenshot.png` for the result.
`test/configSchema.test.js` now also asserts realistic config values
survive snapshotting, which would have caught bug 3 without a browser.

## Sample data

See [`backend/data/DATA_SOURCE.md`](backend/data/DATA_SOURCE.md) — a mix
of real public data (the JBrowse2 project's own "volvox" demo genome)
and hand-authored synthetic SV records, documented unambiguously.

## Live demo

TBD — see `demo/README.md` once the GitHub Pages workflow lands.
