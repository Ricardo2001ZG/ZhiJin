module.exports={
  lintOnSave: false,
  configureWebpack:{
    // plugins:[new NodePolyfillPlugin()]
    resolve: {
      fallback:  {
          "path": require.resolve("path-browserify"), // 如果不需要，那么就直接改为 false 就可以了
      }
  }
  },
  pluginOptions: {
    'style-resources-loader': {
      preProcessor: 'sass',
      patterns: []
    }
  }
}

