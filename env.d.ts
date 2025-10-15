/// <reference types="vite/client" />

// Extend or declare any additional env types here if needed
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  // add other VITE_ env vars here as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
