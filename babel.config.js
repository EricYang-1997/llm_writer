// babel.config.js
module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset' // 如果是 Vue CLI 项目
    // 或 ['@babel/preset-env', { ... }] 其他项目
  ],
  plugins: [
    '@babel/plugin-transform-private-methods' // 👈 添加这一行
  ]
}