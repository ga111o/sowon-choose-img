const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath:
    process.env.NODE_ENV === "production" ? "/sowon-choose-img/" : "/",
  devServer: {
    host: true,
    allowedHosts: ['festival2.ga111o.com']
  }
});
