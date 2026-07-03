import FeatureRendererType from '@jbrowse/core/pluggableElementTypes/renderers/FeatureRendererType'

// Mirrors JBrowse2's own official "arc" plugin: ArcRenderer is a trivial
// FeatureRendererType subclass, all the real logic lives in the
// ReactComponent (SvArcRendering.js).
export default class SvArcRenderer extends FeatureRendererType {}
