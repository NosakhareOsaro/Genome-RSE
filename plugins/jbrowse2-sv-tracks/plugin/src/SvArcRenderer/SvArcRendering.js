import React from 'react'
import { readConfObject } from '@jbrowse/core/configuration'
import { bpSpanPx, bpToPx } from '@jbrowse/core/util'
import { observer } from 'mobx-react'

import {
  colorForSvType,
  getBezierArcPath,
  isSameContigSv,
} from '../util/arcGeometry.js'

const { createElement: h } = React

function SvArcFeature({ feature, region, bpPerPx, peakHeight }) {
  const refName = feature.get('refName')
  const mateRefName = feature.get('mateRefName')
  const svType = feature.get('svType')
  const color = colorForSvType(svType)
  const label = `${svType} ${feature.id()}`

  if (isSameContigSv({ refName, mateRefName })) {
    const start = feature.get('start')
    const mateStart = feature.get('mateStart')
    const [leftPx, rightPx] = bpSpanPx(
      Math.min(start, mateStart),
      Math.max(start, mateStart),
      region,
      bpPerPx,
    )
    return h(
      'path',
      {
        d: getBezierArcPath(leftPx, rightPx, peakHeight),
        stroke: color,
        strokeWidth: 2,
        fill: 'transparent',
        style: { cursor: 'pointer' },
        'data-testid': 'sv-arc-path',
        'data-sv-type': svType,
      },
      h('title', null, label),
    )
  }

  // Cross-contig breakend: one linear view can't show both ends as a single
  // arc, so draw a small marker + label at this feature's own breakpoint
  // instead, pointing at where the mate is.
  const x = bpToPx(feature.get('start'), region, bpPerPx)
  const y = peakHeight - 6
  return h(
    'g',
    { 'data-testid': 'sv-bnd-marker', 'data-sv-type': svType },
    h('circle', { cx: x, cy: y, r: 4, fill: color }),
    h(
      'text',
      { x: x + 6, y: y + 4, fontSize: 10, fill: color },
      `→ ${mateRefName}:${feature.get('mateStart') + 1}`,
    ),
    h('title', null, `${label} (mate on ${mateRefName})`),
  )
}

const SvArcRendering = observer(function SvArcRendering(props) {
  const { features, config, regions, bpPerPx, height = 100, exportSVG } = props
  const region = regions[0]
  const width = (region.end - region.start) / bpPerPx
  const peakHeight = Math.min(readConfObject(config, 'arcHeight') || 80, height)

  const children = [...features.values()].map(feature =>
    h(SvArcFeature, {
      key: feature.id(),
      feature,
      region,
      bpPerPx,
      peakHeight,
    }),
  )

  return exportSVG
    ? h(React.Fragment, null, ...children)
    : h('svg', { width, height, 'data-testid': 'sv-arc-svg' }, ...children)
})

export default SvArcRendering
