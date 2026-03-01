import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  
  modules: [
    '@nuxt/a11y',
    '@nuxt/fonts',
    '@nuxt/hints',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxtjs/color-mode',
    '@nuxtjs/device',
    '@nuxtjs/seo',
    '@pinia/nuxt'
  ],

  css: ['./app/assets/css/tailwind.css'],

  vite: {
    plugins: [
      tailwindcss(),
    ],
  },

  runtimeConfig: {
    jwtSecret: process.env.JWT_SECRET || 'shield-secret-key-change-in-production',
    postgresUrl: process.env.DATABASE_URL || 'postgresql://edith_user:edith_password@localhost:5432/edith_db',
    rabbitmqUrl: process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672',
    public: {
      appName: 'Sentinel'
    }
  },
})
