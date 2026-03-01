import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  
  modules: [
    '@nuxt/a11y',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxtjs/color-mode',
    '@nuxtjs/device',
    '@nuxtjs/seo',
    'shadcn-nuxt',
  ],

  nitro: {
    experimental: {
      tasks: true
    }
  },
  
  css: ['./app/assets/css/tailwind.css'],

  vite: {
    plugins: [
      tailwindcss(),
    ],
  },

  shadcn: {
    componentDir: './app/components/ui',
  },

  runtimeConfig: {
    jwtSecret: process.env.JWT_SECRET || 'shield-secret-key-change-in-production',
    postgresUrl: process.env.DATABASE_URL || 'postgresql://edith_user:edith_password@localhost:5432/edith_db',
    rabbitmqUrl: process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672',
    betterAuthUrl: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
    externalBackendUrl: process.env.EXTERNAL_BACKEND_URL || 'http://localhost:8080',
    public: {
      appName: 'Sentinel'
    }
  },
})