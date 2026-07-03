import * as FeatureRendererTypeModule from '@jbrowse/core/pluggableElementTypes/renderers/FeatureRendererType'

// A defensive namespace import + manual .default unwrap is required here:
// verified against a real jbrowse-web build that window.JBrowseExports
// wraps this particular module as { default: FeatureRendererType } (unlike
// e.g. @jbrowse/core/Plugin, which JBrowse unwraps to the bare class). A
// plain default import would silently work against the local @jbrowse/core
// npm package (real ESM interop unwraps it) while still being `{ default }`
// -- i.e. broken -- against the actual runtime target, which unit tests
// alone can't catch since they never go through window.JBrowseExports.
const FeatureRendererType =
  FeatureRendererTypeModule.default ?? FeatureRendererTypeModule

// Mirrors JBrowse2's own official "arc" plugin: ArcRenderer is a trivial
// FeatureRendererType subclass, all the real logic lives in the
// ReactComponent (SvArcRendering.js).
export default class SvArcRenderer extends FeatureRendererType {}
