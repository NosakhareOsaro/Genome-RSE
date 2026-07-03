import commonjs from '@rollup/plugin-commonjs'
import nodeResolve from '@rollup/plugin-node-resolve'
import replace from '@rollup/plugin-replace'
import terser from '@rollup/plugin-terser'
import JBrowseReExports from '@jbrowse/core/ReExports/list'
import externalGlobals from 'rollup-plugin-external-globals'

const isProd = process.env.NODE_ENV === 'production'

// Plugins must reuse the React/mobx/JBrowse instances JBrowse already loaded
// via window.JBrowseExports -- bundling a second copy causes duplicate-React
// errors. externalGlobals replaces imports of anything in JBrowseReExports
// with inline JBrowseExports[...] references in the compiled code.
function createGlobalsMap(jbrowseGlobals) {
  const globals = {}
  for (const g of jbrowseGlobals) {
    globals[g] = `JBrowseExports["${g}"]`
  }
  return globals
}

const globalsMap = createGlobalsMap(JBrowseReExports)

export default {
  input: 'src/index.js',
  output: {
    // JBrowse reads this off window after the UMD script loads.
    name: 'JBrowsePluginSvTracks',
    file: isProd
      ? 'dist/jbrowse-plugin-sv-tracks.umd.production.min.js'
      : 'dist/out.js',
    format: 'umd',
    // 'named' makes rollup wrap exports as { default: PluginClass } rather
    // than returning the class directly -- JBrowse's plugin loader requires
    // .default.
    exports: 'named',
    sourcemap: true,
  },
  plugins: [
    externalGlobals(globalsMap),
    nodeResolve({ extensions: ['.js', '.jsx'] }),
    commonjs(),
    replace({
      'process.env.NODE_ENV': JSON.stringify(
        process.env.NODE_ENV || 'development',
      ),
      preventAssignment: true,
    }),
    ...(isProd ? [terser()] : []),
  ],
}
