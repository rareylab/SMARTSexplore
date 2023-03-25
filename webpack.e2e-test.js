const webpack = require('webpack');
const {merge} = require('webpack-merge');
const common = require('./frontend/webpack.common.js');

const config = merge(common, {
  mode: 'none',
  devtool: 'source-map',
  plugins: [
    new webpack.DefinePlugin({
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: true,
    }),
  ],
  module: {
    rules: [
      {
        resolve: {
          extensions: ['.js'],
        },
        use: {
          loader: 'babel-loader',
          options: {
            plugins: ['istanbul'],
          },
        },
        enforce: 'post',
        exclude: /node_modules/,
      },
    ],
  },
});

module.exports = config;
