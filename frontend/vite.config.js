import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { webcrypto } from 'crypto'

// Polyfill
globalThis.crypto = webcrypto

// Now define your config
export default defineConfig({
  plugins: [react()],
})