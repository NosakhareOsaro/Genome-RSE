# GitHub Pages demo

This directory assembles a live, static demo for GitHub Pages. Unlike
local development, Pages has no server to run the Flask backend, so:

- `build_static_svs.py` generates `sv-demo.json`, a static snapshot of
  every SV record in `backend/data/sv-demo.vcf.gz` (both contigs).
- `config.json`'s `SvJsonAdapter` points at that static file instead of
  a live `/api/svs` endpoint. The adapter's own client-side
  region-overlap filter (`plugin/src/util/region.js`) means this works
  identically from the adapter's point of view — it just receives more
  records than it asked for and filters them locally, exactly as it
  would if a real backend ever returned unfiltered data.
- `config.json` uses a `__PAGES_BASE_URL__` placeholder for the
  `fastaLocation`/`faiLocation`/`svEndpoint` URIs, substituted with the
  real deployed URL by the GitHub Actions workflow
  (`.github/workflows/jbrowse2-sv-tracks-pages.yml`) before deploying.
  **These three must be absolute URLs, not relative paths** — the
  renderer's adapter code can run inside a web worker (depending on
  jbrowse-web's RPC driver), where a relative URL resolves against the
  worker script's own location, not the page's, and 404s. The plugin
  `<script>` URL itself is fine as a relative path since script tags
  always resolve against the page, regardless of RPC driver — both
  behaviors were confirmed empirically via Puppeteer, not assumed.

## Local preview

```bash
# from plugins/jbrowse2-sv-tracks/
cd plugin && npm run build && cd ..
python3 demo/build_static_svs.py

npx @jbrowse/cli create ./_jbrowse-web --tag v4.3.0
cp plugin/dist/*.js* backend/data/volvox.fa backend/data/volvox.fa.fai demo/sv-demo.json ./_jbrowse-web/
sed 's|__PAGES_BASE_URL__|http://localhost:8090|g' demo/config.json > ./_jbrowse-web/config.json

npx serve --cors --listen 8090 ./_jbrowse-web
# open http://localhost:8090/?config=config.json
```

## Live demo

Deployed by `.github/workflows/jbrowse2-sv-tracks-pages.yml` on push to
`main` (requires the repo's Settings > Pages > Source to be set to
"GitHub Actions" once, manually) to:

```
https://<repo-owner>.github.io/<repo-name>/jbrowse2-sv-tracks/
```
