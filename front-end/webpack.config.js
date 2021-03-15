const path = require('path')
const { env } = require('process')
const webpack = require('webpack')

module.exports = {
  entry: {
    main: './src/js/main.js',
    page: './src/js/page.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'www'),
  },
  plugins: [
    new webpack.DefinePlugin({
      __API__: `'${process.env['npm_package_config_api']}'`
    })
  ],
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
}
