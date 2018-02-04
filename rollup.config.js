/* eslint-env node */

import babel from 'rollup-plugin-babel';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import replace from 'rollup-plugin-replace';
import uglify from 'rollup-plugin-uglify';

import pkg from './package.json';

const NODE_ENV = JSON.stringify(process.env.NODE_ENV || 'development');

const commonjsGotchas = {
  namedExports: {
    'node_modules/react/index.js': ['Component', 'Children', 'createElement'],
    'node_modules/react-dom/index.js': ['render', 'findDOMNode'],
  },
};

const browser = {
  input: 'src/index.js',
  output: [
    { file: pkg.frappe, name: pkg.name, format: 'iife', sourcemap: true },
  ],
  plugins: [
    resolve({ browser: true }),
    replace({ __ENV__: NODE_ENV, 'process.env.NODE_ENV': NODE_ENV }),
    babel({ exclude: 'node_modules/**', runtimeHelpers: true }),
    commonjs(commonjsGotchas),
  ],
};

let config = [browser];

if (NODE_ENV === '"production"') {
  browser.output.push({
    file: pkg.browser,
    name: pkg.name,
    format: 'iife',
    sourcemap: false,
  });
  browser.plugins.push(uglify());
  const bundles = Object.assign({}, browser, {
    output: [
      { file: pkg.main, name: pkg.name, format: 'cjs', sourcemap: false },
      { file: pkg.module, name: pkg.name, format: 'es', sourcemap: false },
    ],
    plugins: [
      resolve({ browser: true }),
      babel({ exclude: 'node_modules/**' }),
      commonjs(commonjsGotchas),
    ],
  });
  config = [...config, bundles];
}

export default config;
