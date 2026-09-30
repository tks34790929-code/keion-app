import { defineConfig } from "vite";

export default defineConfig({
  server: {
    // コンテナの外（PC のブラウザ）からアクセスできるようにする
    host: true,
    port: 5173,
    strictPort: true,
    // Windows のフォルダをマウントすると変更を検知できないことがあるため、ポーリングで検知する
    watch: { usePolling: true },
    // /api へのリクエストを backend コンテナに転送する（CORS 設定が不要になる）
    proxy: {
      "/api": "http://backend:8000",
    },
  },
});
