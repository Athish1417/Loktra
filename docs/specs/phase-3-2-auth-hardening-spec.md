# Loktra AI — Phase 3.2 Auth Hardening Spec

## Context

AI Civic Guard is now working.

Current auth problem:
The app can still open in demo mode / direct demo login flow. This makes the authentication look weak.

## Goal

Make authentication production-style and remove demo bypass behavior.

Do not rewrite the full app.
Do not break existing backend, dashboards, complaint submission, or AI guard.

## Required Fixes

### 1. Remove Demo Auto Login

Remove any direct demo login behavior from the UI.

The app must not automatically log in as:
- Demo Citizen
- Demo MP
- Demo Officer
- Demo Admin

No one-click demo login should exist.

### 2. Login Must Require Credentials

Login flow must be:

1. Select role
2. Enter email
3. Enter password
4. Submit
5. Backend verifies credentials
6. Redirect based on authenticated user role

No route should enter the app without a valid JWT token.

### 3. Enforce Role Match

If user selects Citizen but the account is MP/Admin, login must fail.

Show:

"This account is not registered as Citizen. Please choose the correct role."

Backend account role is the source of truth.

### 4. Protect App Routes

Routes under `/app/*` must require authentication.

If no valid token exists:
- redirect to `/login`

If role is not allowed:
- show access denied or redirect to correct dashboard.

### 5. Logout Must Clear Everything

Logout must clear:
- access token
- user object
- role
- local/session storage auth data

After logout, user should not be able to use browser back button to access dashboard.

### 6. Demo Credentials

Demo accounts may remain only as seeded backend users.

Do not show demo-login buttons.

Optional small text is okay:

"Use demo credentials from README for testing."

### 7. Registration

Citizen registration should remain available.

MP/Admin, Officer, and Super Admin public registration should not be allowed unless already intentionally implemented.

These roles should come from seed data or Super Admin creation.

### 8. Forgot Password

Keep forgot password UI and placeholder endpoint.

### 9. Testing

Verify:

- `/app/submit` redirects to login when logged out.
- Login with wrong email fails.
- Login with wrong password fails.
- Login with correct email but wrong selected role fails.
- Citizen login opens Citizen pages only.
- MP/Admin login opens MP/Admin dashboard only.
- Officer login opens Officer dashboard only.
- Super Admin login opens Super Admin dashboard only.
- Logout clears session fully.
- No demo auto-login remains.

## Important Rules

- Analyze existing codebase first.
- Do not delete working features.
- Do not redesign full UI.
- Only harden auth flow.
- Keep code modular.
- After implementation, provide changed files summary and test results.