import Plugin from '@jbrowse/core/Plugin'

/**
 * Registers pluggable elements only -- no custom Track or Display type.
 *
 * External (UMD-loaded) plugins can't statically import base classes like
 * `BaseLinearDisplay`/`BaseLinearDisplayComponent` from
 * `@jbrowse/plugin-linear-genome-view`: JBrowse's `jbrequire` mechanism
 * only re-exports packages listed in `@jbrowse/core/ReExports/list`, and
 * that plugin isn't one of them (it's only accessible to code bundled
 * directly into jbrowse-web itself). So instead of a custom Display, this
 * plugin reuses JBrowse's stock `FeatureTrack` + `LinearBasicDisplay` and
 * plugs in a custom adapter and renderer via config -- see
 * plugin/config.json and demo/config.json for the
 * `"renderer": { "type": "SvArcRenderer" }` wiring.
 */
export default class SvTracksPlugin extends Plugin {
  name = 'SvTracksPlugin'

  install(_pluginManager) {}

  configure() {}
}
