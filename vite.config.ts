// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [['babel-plugin-react-compiler']],
      },
    }),
  ],
  server: {
    host: '0.0.0.0', // 👈 允许局域网访问
    port: 5173,      // 可选：指定端口（默认 5173）
    open: false,     // 是否自动打开浏览器
  },
});