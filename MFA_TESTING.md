# MFA Replay Protection – Testing Instructions

**CS2413 – Information Security | Fall 2026**

## 1. Overview

This implementation improves the existing two-factor authentication (2FA) system in OWASP Juice Shop by adding replay protection for time-based one-time passwords (TOTP).

The original system verified six-digit authentication codes but did not track previously accepted TOTP time steps. The modified implementation records the last successfully used time step and rejects attempts to reuse it.

## 2. Requirements

- Node.js and npm
- OWASP Juice Shop project source code
- Google Authenticator or another TOTP-compatible authenticator
- Web browser

## 3. Running the Application

1. Clone the group repository and switch to the `feature/mfa` branch.
2. Open a terminal in the project directory.
3. Install dependencies:

   `npm install`

4. Build the server:

   `npm run build:server`

5. Start Juice Shop:

   `npm start`

6. Open `http://localhost:3000` in a browser.

**Note:** The project's current startup configuration resets the SQLite database. Use disposable test accounts and avoid restarting the server during testing.

## 4. Test 1 – MFA Setup

1. Register a test account and log in.
2. Navigate to **Account → Privacy & Security → 2FA Configuration**.
3. Scan the QR code using Google Authenticator.
4. Enter the account password and current six-digit code.
5. Click **Save**.

**Expected result:** The application confirms that two-factor authentication has been enabled.

## 5. Test 2 – Valid MFA Login

1. Log out of Juice Shop.
2. Log back in using the test account's email and password.
3. When prompted, enter the current six-digit code from Google Authenticator.
4. Submit the code.

**Expected result:** Authentication succeeds and the user is logged in.

## 6. Test 3 – Invalid or Expired Code

1. Log out and return to the MFA verification screen.
2. Enter an incorrect or expired six-digit code.
3. Click **Log in**.

**Expected result:** The application rejects the code and displays an invalid-token message.

## 7. Test 4 – TOTP Replay Protection

1. Log in successfully using a valid TOTP code.
2. Log out and begin another login using the same test account.
3. Submit the previously accepted TOTP code while it is still within the server's accepted time window.
4. Observe the response.
5. Wait for a new TOTP time step and try again using a fresh code.

**Expected results:**

- First use of a valid TOTP code: accepted.
- Reuse of the same accepted time step: rejected.
- Fresh code from a newer time step: accepted.

**Testing note:** A controlled replay test is recommended because manually logging out and back in within the code's validity window can be difficult. An expired-code rejection alone does not demonstrate replay protection.

## 8. Implementation Details

The following files were modified:

- `models/user.ts` – Added `lastUsedTotpStep` to track the last accepted TOTP time step.
- `routes/2fa.ts` – Added conditional verification logic to prevent replay of previously accepted time steps.
- `server.ts` – Excluded the replay-tracking field from the generated user API.

The implementation uses `otplib` version 13.6.0, TypeScript, Sequelize, and SQLite.

## 9. Observed Results

MFA setup and login using Google Authenticator were successful. The modified server also compiled without TypeScript errors.

An invalid-code response was observed during testing. The replay-protection mechanism was implemented, but its effectiveness should be confirmed with a controlled same-code replay test.

## 10. Security Considerations

Use only disposable test accounts. Do not include account passwords, authenticator setup secrets, authentication tokens, or unredacted QR codes in screenshots or documentation.

**Contributor:** Amritansh Singh – Multi-Factor Authentication