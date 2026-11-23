# Progressive Login Rate Limiting – Testing Instructions

**CS2413 – Information Security | Fall 2026**

## 1. Overview

This implementation improves the authentication endpoint (`POST /rest/user/login`) in OWASP Juice Shop by adding progressive login rate limiting and temporary account lockouts.

The original system allowed unlimited consecutive failed login attempts against any account, leaving it vulnerable to automated brute-force and credential-stuffing attacks. The modified implementation tracks consecutive failed attempts per account email (falling back to client IP when no email is provided), enforces a temporary lockout starting on the 5th failed attempt, escalates the lockout duration on subsequent failures, and resets the counter upon a successful login.

| Failed Attempts | Standard Lockout Duration | Demo Mode Duration (`RATE_LIMIT_DEMO=true`) |
| ----- | ----- | ----- |
| 1 – 4 | None | None |
| 5 | 1 minute (60s) | 5 seconds |
| 6 | 5 minutes (300s) | 10 seconds |
| 7 | 15 minutes (900s) | 20 seconds |
| 8+ | 60 minutes (3600s) | 30 seconds |

## 2. Requirements

* Node.js and npm
* OWASP Juice Shop project source code
* Web browser
* Terminal (PowerShell, Bash, or zsh) for running the server and optional automated verification requests

## 3. Running the Application

1. Clone the group repository and switch to the `feat/login-rate-limiting` branch.
2. Open a terminal in the project directory.
3. Install dependencies:

   ```bash
   npm install
   ```

4. Build the server:

   ```bash
   npm run build:server
   ```

5. Start Juice Shop:

   * **Standard mode (Apple-style timings: 1m → 5m → 15m → 60m):**

     ```bash
     npm start
     ```

   * **Demo mode (accelerated timings: 5s → 10s → 20s → 30s for live testing):**

     ```powershell
     # PowerShell
     $env:RATE_LIMIT_DEMO="true"; npm start
     ```

     ```bash
     # Bash / zsh
     RATE_LIMIT_DEMO=true npm start
     ```

6. Open `http://localhost:3000` in a browser.

> **Note:** Both Juice Shop's SQLite database and the in-memory rate-limiting store reset whenever the server restarts. Use disposable test accounts and avoid restarting the server mid-test.

## 4. Test 1 – Account Setup, Valid Login, and Attempts Below the Threshold

1. Navigate to `http://localhost:3000/#/login`, click **Not yet a customer?**, and register a disposable test account.
2. Log in using the test account's email and valid password to confirm normal authentication works.
3. Log out and return to `http://localhost:3000/#/login`.
4. Enter the test account's email with an incorrect password and click **Log in**.
5. Repeat until 4 consecutive failed attempts have been submitted.

**Expected results:**

* **Valid login:** Authentication succeeds (`HTTP 200`) and logs the user into the application.
* **Failed attempts 1 – 4:** Each attempt is rejected with `HTTP 401` and displays `Invalid email or password.` without locking the account.

## 5. Test 2 – Initial Lockout and Progressive Escalation

1. Immediately submit a 5th login attempt for the same test account using an incorrect password.
2. Submit another login attempt immediately while the lockout is still active.
3. Wait for the Tier 1 lockout period to expire (`5s` in demo mode / `60s` in standard mode), then submit another incorrect password (6th failed attempt).
4. Wait for the Tier 2 lockout period to expire (`10s` in demo mode / `300s` in standard mode), then submit another incorrect password (7th failed attempt).
5. Wait for the Tier 3 lockout period to expire (`20s` in demo mode / `900s` in standard mode), then submit another incorrect password (8th failed attempt).

**Expected results:**

* **5th failed attempt (Tier 1):** Rejected with `HTTP 429 Too Many Requests`, a `Retry-After` response header (`60` standard / `5` demo), and an error banner showing the lockout countdown.
* **Attempt while locked:** Blocked prior to database authentication with `HTTP 429` and the remaining countdown in seconds.
* **6th failed attempt (Tier 2):** Lockout escalates to 5 minutes (`Retry-After: 300` standard / `10` demo).
* **7th failed attempt (Tier 3):** Lockout escalates to 15 minutes (`Retry-After: 900` standard / `20` demo).
* **8th+ failed attempt (Tier 4):** Lockout caps at 60 minutes (`Retry-After: 3600` standard / `30` demo).

> **Testing note:** Running the server in demo mode (`RATE_LIMIT_DEMO=true`) is recommended so all four escalation tiers can be verified without waiting an hour. An automated Node.js script (`node test-rate-limit.mjs`) can also be used to inspect the `Retry-After` headers precisely.

## 6. Implementation Details

The following files were added or modified:

* `lib/loginRateLimiter.ts` – Added an in-memory progressive lockout tracker exporting `getRateLimitKey`, `checkLockout`, `recordFailedAttempt`, and `recordSuccessfulAttempt`, supporting both standard Apple-style intervals (`60s`, `300s`, `900s`, `3600s`) and accelerated `RATE_LIMIT_DEMO=true` intervals (`5s`, `10s`, `20s`, `30s`).
* `routes/login.ts` – Added a pre-query lockout check that short-circuits locked accounts with `HTTP 429` and a `Retry-After` header, recorded failed authentication attempts in the failure branch, and cleared the counter on valid password verification (including accounts that proceed to TOTP verification).

The implementation uses TypeScript, Express, and Node.js.

## 7. Observed Results

* The modified backend compiled cleanly with `npm run build:server` without TypeScript errors.
* New test accounts registered and authenticated normally, and failed attempts 1–4 returned `HTTP 401` (`Invalid email or password.`).
* On the 5th failed attempt, the server returned `HTTP 429` with the `Retry-After` header and displayed the lockout countdown in the login UI; subsequent post-expiry failures escalated across Tiers 1–4 as expected.

## 8. Security Considerations

* Use only disposable test accounts during testing, and avoid exposing JWTs, passwords, or private configuration details in screenshots or reports.
* Because failed-attempt records are stored in process memory (`Map`), restarting the server clears active lockouts; a production deployment should persist counters in a shared store such as Redis.
* Progressive rate limiting slows credential guessing against individual accounts, but it should be paired with parameterized queries (to prevent SQL injection) and IP-level throttling (to mitigate distributed password spraying across many distinct accounts).

**Contributor:** Md Imtiaz Ahmed – Progressive Login Rate Limiting