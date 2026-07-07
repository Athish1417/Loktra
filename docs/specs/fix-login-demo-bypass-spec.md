# Loktra AI — Fix Login Demo Bypass Spec

## Goal

Improve the login page so authentication looks real and professional.

## Current Problem

The login page has role selection and email/password, but it still shows:

"Explore a demo role"

with buttons like:

- MP
- Officer
- Citizen
- Admin

This makes the login feel like a demo bypass and not real authentication.

## Required Fix

Remove the "Explore a demo role" section from the login page.

Users must login only through:

1. Select role
2. Enter valid email
3. Enter password
4. Click Sign in

No demo role shortcut buttons should be visible on the login page.

## Auth Flow

Login flow must be:

Role Selection Page

↓

Email + Password Page

↓

Backend Login API

↓

Redirect based on actual authenticated user role

## Validation

Frontend must validate:

- email required
- valid email format
- password required
- password minimum 6 characters

Backend must remain the source of truth.

## Demo Credentials

Demo credentials can stay in README only.

Do not show demo login buttons in UI.

Optional:
If needed for hackathon testing, show small text:

"Use the demo credentials provided in README."

But do not provide one-click role buttons.

## Forgot Password

Keep Forgot Password link.

## Register

Keep Create Account link.

## Important Rules

- Do not rewrite the whole app.
- Only fix login/auth UI behavior.
- Do not remove backend auth.
- Do not break existing routes.
- Keep existing premium design.
- After changes, test login for Citizen, MP/Admin, Officer, and Super Admin.

## Expected Result

Login should feel like a real production login system, not a demo role switcher.