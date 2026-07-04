# WP1: JBrowse2 upstream issue — `window.JBrowseExports` shape inconsistency

**Status:** Filed, awaiting maintainer response.
**Artifact:** [GMOD/jbrowse-components#5594](https://github.com/GMOD/jbrowse-components/issues/5594)
**Filed:** 2026-07-04, by [github.com/NosakhareOsaro](https://github.com/NosakhareOsaro)

## Summary

While building [`plugins/jbrowse2-sv-tracks`](../plugins/jbrowse2-sv-tracks) in
Phase 3, a defensive workaround was added for a runtime error
(`Class extends value #<Object> is not a constructor or null`) when extending
`FeatureRendererType`, a base class re-exported by JBrowse2 for external
plugins. At the time this was documented as a plugin-side gotcha (see
`plugins/jbrowse2-sv-tracks/docs/blog-post.md`). Phase 5 revisited it to
determine whether it's a genuine, still-current, reportable bug in JBrowse2
itself, rather than something specific to how our own plugin was written.

## Investigation process

1. **Searched existing prior art first.** `gh search issues --repo
   GMOD/jbrowse-components` for `JBrowseExports`, `postProcessSnapshot
   default`, and `ReExports external plugin` turned up one related-but-different
   closed issue ([#5002](https://github.com/GMOD/jbrowse-components/issues/5002),
   a re-export naming bug fixed by a maintainer in May 2025) and nothing for
   the specific modules involved here — evidence the maintainers are
   responsive to this category of bug, and evidence this specific gap hadn't
   already been reported.

2. **Confirmed no version drift.** The currently published `@jbrowse/core` is
   still `4.3.0` — the exact version Phase 3 tested against — so there was no
   risk of investigating a bug that had already been silently fixed in a
   newer release.

3. **Re-verified directly against a fresh build, not our own (already-fixed)
   plugin code.** Assembled a brand-new `jbrowse-web` v4.3.0 via `npx
   @jbrowse/cli create`, served it with a minimal `config.json`, and used
   Puppeteer to evaluate `window.JBrowseExports` directly in a real browser —
   deliberately not exercising our plugin's own defensive workaround, since
   that would trivially "pass" regardless of whether the underlying platform
   behavior was still broken.

4. **Mapped the full scope**, not just the one module Phase 3 happened to hit:
   `FeatureRendererType`, `ServerSideRendererType`, `BoxRendererType`, and
   `RendererType` are all wrapped as `{ default: Class }`; `ViewType`,
   `AdapterType`, `DisplayType`, `TrackType`, `WidgetType`, `Plugin`, and even
   the sibling renderer `CircularChordRendererType` are all bare
   classes/functions. This is a broader, more precise finding than Phase 3's
   original single-module observation.

5. **Ruled out an obvious explanation before reporting anything.** Compared
   the actual JBrowse2 source of the wrapped `FeatureRendererType.ts` against
   the unwrapped `CircularChordRendererType.tsx` on GitHub — both use the
   identical `export default class X extends Y` pattern, so the difference
   isn't in how individual modules are authored; it has to be in how
   `window.JBrowseExports` itself gets assembled for jbrowse-web.

6. **Confirmed this affects the officially recommended tooling, not an
   unsupported approach.** Read `jbrowse-plugin-template`'s own
   `rollup.config.mjs` (the template JBrowse's own docs point plugin authors
   to) and confirmed it maps every `@jbrowse/core/ReExports/list` entry
   directly onto `JBrowseExports["<module path>"]` via
   `rollup-plugin-external-globals`, with no unwrapping logic of its own —
   meaning any plugin author following the template's own conventions to
   build a custom Renderer hits this.

7. **Checked whether the related documentation gap already had coverage.**
   `website/docs/developer_guides/config_model.md` shows the "obviously
   nonfunctional placeholder default" convention (`/path/to/my.bam`) by
   example, but never explains *why* — the `ConfigurationSchema
   postProcessSnapshot` collapse-to-`{}` behavior that motivates it isn't
   mentioned anywhere in the docs. A documentation PR is drafted for this
   (see "Next steps" below) but deliberately not filed yet.

## What was filed

The full issue title and body are preserved verbatim in
[GMOD/jbrowse-components#5594](https://github.com/GMOD/jbrowse-components/issues/5594).
In summary, it reports:

- The exact shape mismatch above, with a minimal, self-contained reproduction
  (assemble a stock jbrowse-web, open the console, inspect
  `window.JBrowseExports`).
- The concrete impact on real plugin authors using the official template
  (build succeeds, unit tests against the real npm package pass, and it only
  fails at runtime in a browser).
- A secondary, lower-priority observation from the same investigation:
  `@jbrowse/core/util/simpleFeature` isn't on the ReExports list at all
  (`SimpleFeature` is reachable via the `@jbrowse/core/util` barrel instead),
  flagged as possibly intentional rather than asserted as a bug.

## Next steps

- Watch for a maintainer response on #5594.
- The drafted documentation PR for `config_model.md` (explaining the
  `postProcessSnapshot` rationale for placeholder defaults) is intentionally
  being held until either a maintainer responds to #5594, or a reasonable
  waiting period passes with no response — in case their reply changes how
  the docs fix should be framed.
