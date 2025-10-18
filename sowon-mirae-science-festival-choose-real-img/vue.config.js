const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath:
    process.env.NODE_ENV === "production" ? "/sowon-choose-img/" : "/",
  devServer: {
    host: "0.0.0.0",
    allowedHosts: 'all',  // 또는 ['festival2.ga111o.com']

    // 클라이언트가 올바른 WebSocket URL 사용하도록 설정
    client: {
      webSocketURL: {
        protocol: 'wss',  // HTTPS이므로 wss 사용
        hostname: 'festival2.ga111o.com',
        port: 443,  // HTTPS 기본 포트
        pathname: '/ws'
      }
    },
  }
});
