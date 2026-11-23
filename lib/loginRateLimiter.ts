// lib/loginRateLimiter.ts

interface AttemptRecord {
  failedAttempts: number
  lockoutUntil: number 
}

// Set env var RATE_LIMIT_DEMO=true to use shorter durations (5s, 10s, 20s, 30s) for live testing.
const LOCKOUT_SCHEDULE_SECONDS = process.env.RATE_LIMIT_DEMO === 'true'
  ? [5, 10, 20, 30]
  : [60, 300, 900, 3600]

const LOCKOUT_THRESHOLD = 5

const attemptsStore = new Map<string, AttemptRecord>()

export function getRateLimitKey (email?: string, ip?: string): string {
  const normalizedEmail = typeof email === 'string' ? email.trim().toLowerCase() : ''
  return normalizedEmail !== '' ? `email:${normalizedEmail}` : `ip:${ip ?? 'unknown'}`
}

export function checkLockout (key: string): { locked: boolean, retryAfterSeconds: number, failedAttempts: number } {
  const record = attemptsStore.get(key)
  if (!record) {
    return { locked: false, retryAfterSeconds: 0, failedAttempts: 0 }
  }

  const now = Date.now()
  if (record.lockoutUntil > now) {
    const retryAfterSeconds = Math.ceil((record.lockoutUntil - now) / 1000)
    return { locked: true, retryAfterSeconds, failedAttempts: record.failedAttempts }
  }

  return { locked: false, retryAfterSeconds: 0, failedAttempts: record.failedAttempts }
}

export function recordFailedAttempt (key: string): { locked: boolean, retryAfterSeconds: number, failedAttempts: number } {
  const existing = attemptsStore.get(key) ?? { failedAttempts: 0, lockoutUntil: 0 }
  const failedAttempts = existing.failedAttempts + 1

  let lockoutUntil = 0
  let retryAfterSeconds = 0

  if (failedAttempts >= LOCKOUT_THRESHOLD) {
    const tierIndex = Math.min(
      failedAttempts - LOCKOUT_THRESHOLD,
      LOCKOUT_SCHEDULE_SECONDS.length - 1
    )
    retryAfterSeconds = LOCKOUT_SCHEDULE_SECONDS[tierIndex]
    lockoutUntil = Date.now() + retryAfterSeconds * 1000
  }

  attemptsStore.set(key, { failedAttempts, lockoutUntil })

  return {
    locked: retryAfterSeconds > 0,
    retryAfterSeconds,
    failedAttempts
  }
}

export function recordSuccessfulAttempt (key: string): void {
  attemptsStore.delete(key)
}