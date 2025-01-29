'use strict'

// const port = process.env.port || process.env.npm_config_port || 8080


module.exports = {
  publicPath: '/ac',
  lintOnSave: false,
  // assetsDir: './',
  // lintOnSave: process.env.NODE_ENV === 'development',
  productionSourceMap: false,
  pwa: {
    iconPaths: {
      favicon32: "icon.svg",
      favicon16: "icon.svg",
      appleTouchIcon: "icon.svg",
      maskIcon: "icon.svg",
      msTileImage: "icon.svg",
    }
  },
  devServer: {
    // port: port,
    // open: true,
    // overlay: {
    //   warnings: false,
    //   errors: true
    // },
    proxy: {
      '/getInstruction': {
        // target: 'http://192.168.202.124:6873/dialog',
        // target: 'http://127.0.0.1:5000/',
        target: 'http://localhost:7778',
        changeOrigin: true,
        pathRewrite: {
          '^/getInstruction': ''
        },
        timeout:10*60*1000
      },
      '/operateDrone': {
        // target: 'http://192.168.202.124:6873/dialog',
        target: 'http://127.0.0.1:5000/operate_drone',
        changeOrigin: true,
        pathRewrite: {
          '^/operateDrone': ''
        },
        timeout:10*60*1000
      },
    }
  },
  // configureWebpack: config => {
  //   config.module.rules.push({
  //     test: /\.worker.js$/,
  //     use: {
  //       loader: 'worker-loader',
  //       options: { inline: true, name: 'workerName.[hash].js' }
  //     }
  //   })
  // },
  // parallel: false,
  // chainWebpack: config => {
  //   config.output.globalObject('this')
  // }
  configureWebpack: config => {
    config.module.rules.push({
      test: /\.worker.js$/,
      use: {
        loader: 'worker-loader',
        options: { inline: true, name: 'workerName.[hash].js' }
      }
    })
  },
  parallel: false,
  chainWebpack: config => {
    config.output.globalObject('this')
  }
}
