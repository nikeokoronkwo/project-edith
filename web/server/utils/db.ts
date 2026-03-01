import pg from 'pg'

const config = useRuntimeConfig()

let pool: pg.Pool | null = null

export function getDbPool() {
  if (!pool) {
    pool = new pg.Pool({
      connectionString: config.postgresUrl,
    })
  }
  return pool
}

export async function query<T>(text: string, params?: unknown[]): Promise<T[]> {
  const pool = getDbPool()
  const result = await pool.query(text, params)
  return result.rows as T[]
}

export async function queryOne<T>(text: string, params?: unknown[]): Promise<T | null> {
  const rows = await query<T>(text, params)
  return rows[0] || null
}

export async function initDatabase() {
  const pool = getDbPool()
  
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      email VARCHAR(255) UNIQUE NOT NULL,
      name VARCHAR(255),
      password_hash VARCHAR(255) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `)

  await pool.query(`
    CREATE TABLE IF NOT EXISTS sessions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID REFERENCES users(id) ON DELETE CASCADE,
      token VARCHAR(512) UNIQUE NOT NULL,
      expires_at TIMESTAMP NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `)

  await pool.query(`
    CREATE TABLE IF NOT EXISTS reports (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID REFERENCES users(id) ON DELETE SET NULL,
      hero_name VARCHAR(255) NOT NULL,
      description TEXT,
      affected_resources TEXT[],
      affected_locations TEXT[],
      report_ids UUID[],
      time_started TIMESTAMP,
      metadata_encrypted TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `)

  await pool.query(`
    CREATE TABLE IF NOT EXISTS events (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name VARCHAR(255) NOT NULL,
      description TEXT,
      priority VARCHAR(50) NOT NULL,
      started_at TIMESTAMP,
      report_ids UUID[],
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `)

  await pool.query(`
    CREATE TABLE IF NOT EXISTS analytics_data (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      resource VARCHAR(255) NOT NULL,
      sector VARCHAR(255) NOT NULL,
      value DECIMAL(10, 2) NOT NULL,
      country VARCHAR(255),
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `)

  console.log('Database tables initialized')
}
