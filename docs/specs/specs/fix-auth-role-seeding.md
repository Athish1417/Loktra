# Spec: Fix Auth Role Seeding and Dashboard Redirects

## Problem
Admin, MP, and Officer demo logins fail with “Incorrect email or password”.
Newly registered users correctly open the Citizen dashboard, but demo role users must open their correct dashboards.

## Requirements

1. Seed demo users on backend startup if they do not already exist:
   - admin@loktra.ai / admin123 / role: super_admin
   - mp@loktra.ai / mp123 / role: mp
   - officer@loktra.ai / officer123 / role: officer
   - citizen@loktra.ai / citizen123 / role: citizen

2. Use the existing password hashing method used by registration/login.

3. Do not create duplicate users.

4. Registration must create only citizen users by default.

5. After login, redirect based on role:
   - super_admin → existing Super Admin dashboard route
   - mp → existing MP dashboard route
   - officer → existing Officer dashboard route
   - citizen → existing Citizen dashboard route

6. Do not allow public registration as admin, MP, or officer.

7. Keep existing UI and API structure unchanged unless needed.

8. Ensure this works after Railway redeploy.

## Acceptance Test

- admin@loktra.ai / admin123 logs in and opens Super Admin dashboard.
- mp@loktra.ai / mp123 logs in and opens MP dashboard.
- officer@loktra.ai / officer123 logs in and opens Officer dashboard.
- citizen@loktra.ai / citizen123 logs in and opens Citizen dashboard.
- New signup user opens Citizen dashboard only.