const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath:
    process.env.NODE_ENV === "production" ? "/sowon-choose-img/" : "/",
  devServer: {
    host: "0.0.0.0",
    allowedHosts: 'all',  // 또는 ['festival2.ga111o.com']

    // 웹소켓 기반 핫 리로드 비활성화
    hot: false,
    liveReload: false,
  }
});
