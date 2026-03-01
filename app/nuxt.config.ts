export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: true },
  
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
  ],

  app: {
    head: {
      title: 'Sentinel - SHIELD Economic Dashboard',
      meta: [
        { name: 'description', content: 'SHIELD Economic Analysis and Forecasting Dashboard' }
      ]
    }
  },

  runtimeConfig: {
    jwtSecret: process.env.JWT_SECRET || 'shield-secret-key-change-in-production',
    postgresUrl: process.env.DATABASE_URL || 'postgresql://edith_user:edith_password@localhost:5432/edith_db',
    rabbitmqUrl: process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672',
    public: {
      appName: 'Sentinel'
    }
  },

  nitro: {
    experimental: {
      websocket: true
    }
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.js',
  }
})
