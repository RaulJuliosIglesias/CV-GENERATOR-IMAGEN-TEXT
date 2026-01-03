import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    // Load env file based on `mode` in the current working directory.
    // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
    // We need to look in the current directory (frontend root)
    const env = loadEnv(mode, process.cwd(), '')

    // Default to 8001 if variable not set (fallback)
    const target = env.VITE_API_TARGET || 'http://127.0.0.1:8001'

    console.log(`[Vite Config] Proxying /api requests to: ${target}`)

    return {
        plugins: [react()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src'),
            },
        },
        server: {
            port: 5173,
            proxy: {
                '/api': {
                    target: target,
                    changeOrigin: true,
                    secure: false,
                },
                '/pdf': {
                    target: target,
                    changeOrigin: true,
                },
                '/html': {
                    target: target,
                    changeOrigin: true,
                },
                '/avatars': {
                    target: target,
                    changeOrigin: true,
                },
                '/assets': {
                    target: target,
                    changeOrigin: true,
                }
            },
        },
    }
})
