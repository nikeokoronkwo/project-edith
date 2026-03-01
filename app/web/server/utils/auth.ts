import { betterAuth } from 'better-auth'
import { jwt } from "better-auth/plugins"
import { Pool } from "pg";

export const auth = betterAuth({
  emailAndPassword: { 
    enabled: true, 
  },
  plugins: [
    jwt()
  ],
  database: new Pool({
      // connection options
      connectionString: process.env.DATABASE_URL || 'postgresql://edith_user:edith_password@localhost:5432/edith_db',
  }),
})