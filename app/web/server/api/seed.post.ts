import { betterAuth } from 'better-auth'
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { getDbPool, initDatabase } from '../utils/db'

export default defineEventHandler(async (event) => {
  const pool = getDbPool()
  
  await initDatabase()
  
  const auth = betterAuth({
    database: drizzleAdapter(pool, {
      type: 'pg',
    }),
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: false,
    },
    advanced: {
      generateId: () => crypto.randomUUID()
    }
  })

  const users = [
    { email: 'nick.fury@shield.gov', name: 'Nick Fury', password: 'shield123' },
    { email: 'steve.rogers@shield.gov', name: 'Steve Rogers', password: 'shield123' },
    { email: 'bruce.banner@shield.gov', name: 'Bruce Banner', password: 'shield123' },
    { email: 'natasha.romanoff@shield.gov', name: 'Natasha Romanoff', password: 'shield123' },
    { email: 'sam.wilson@shield.gov', name: 'Sam Wilson', password: 'shield123' },
  ]

  const results = []

  for (const user of users) {
    try {
      await auth.api.signUp.email({
        email: user.email,
        password: user.password,
        name: user.name,
      })
      results.push({ email: user.email, status: 'created' })
    } catch (e) {
      results.push({ email: user.email, status: 'exists' })
    }
  }

  return { success: true, results }
})
