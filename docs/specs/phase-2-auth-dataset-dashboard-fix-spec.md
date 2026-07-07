# Loktra AI — Auth, Dataset, and Dashboard Fix Spec

## Context

The project already has Phase 1 UI and Phase 2 backend started.

Claude Code must inspect the existing codebase first and then improve the current implementation.

Do not delete existing working code.
Do not rewrite the full project.
Improve only the required parts.

## Main Goals

1. Improve authentication flow.
2. Clarify dataset type.
3. Add latitude and longitude support across complaint/dashboard views.
4. Make login/register more realistic and professional.

---

## 1. Dataset Clarification

Check the current dataset implementation.

If the dataset is sample/demo/dummy data, clearly label it everywhere as:

"Sample Government-Style Dataset"

Do not call it real government data unless it is actually imported from official sources like data.gov.in or Census India.

Update README and UI text if needed.

For now, keep dummy/sample data, but structure it so real government datasets can be imported later.

---

## 2. Improved Authentication Flow

Current login is not professional enough.

Update authentication so users first choose their role:

- Citizen
- MP/Admin
- Officer
- Super Admin

After selecting a role, show:

- Email input
- Password input
- Login button
- Forgot Password link

Do not ask only for role and login directly.

---

## 3. Email Validation

Email must be validated properly.

Frontend:
- Email should be required.
- Must follow valid email format.
- Show clear error if invalid.

Backend:
- Validate email using Pydantic EmailStr.
- Reject invalid email format.
- Ensure email is unique during registration.

---

## 4. Password Requirements

Password should be required.

Add basic validation:

- Minimum 6 characters
- Show password toggle
- Clear error message if password is missing or too short

Passwords must be hashed in backend.

---

## 5. Forgot Password Option

Add Forgot Password UI.

For now, MVP behavior is acceptable:

- User clicks Forgot Password
- Opens Forgot Password page/modal
- User enters email
- Validate email format
- Show message:
  "If this email exists, password reset instructions will be sent."

Backend should include placeholder endpoint:

POST /auth/forgot-password

Do not implement real email sending yet.
Keep it ready for future integration.

---

## 6. Register Flow

Citizen registration should ask:

- Full name
- Email
- Password
- Confirm password
- Phone optional
- State
- District
- Constituency
- Ward/Village

MP/Admin registration should not be open publicly unless already allowed.
Officer and MP/Admin users should be created by Super Admin or seed data.

---

## 7. Role-Based Login Rules

After login:

Citizen → Citizen dashboard

MP/Admin → MP dashboard

Officer → Officer dashboard

Super Admin → Super Admin dashboard

User must only access pages allowed for their role.

If unauthorized, redirect or show access denied.

---

## 8. Latitude and Longitude Support

Add latitude and longitude fields to complaints.

Complaint submission should support:

- latitude
- longitude

If browser location is available, add a button:

"Use My Current Location"

This should fill latitude and longitude.

If not available, allow manual entry.

Backend complaint model must store:

- latitude
- longitude

Dashboard should display latitude and longitude for complaints for every role:

- Citizen dashboard
- MP/Admin dashboard
- Officer dashboard
- Super Admin dashboard

Tables/cards should show:

Latitude: value  
Longitude: value

---

## 9. Dashboard Updates

Update complaint cards/tables to include:

- Complaint ID
- Title
- Category
- Status
- Priority Score
- State
- District
- Constituency
- Ward/Village
- Latitude
- Longitude
- Created Date

Make sure role-based filtering still works.

MP/Admin must only see complaints from assigned constituency.

Officer must only see assigned complaints.

Citizen must only see own complaints.

Super Admin can see all.

---

## 10. Backend API Updates

Update schemas, models, and APIs where required.

Ensure these endpoints support the improved auth and complaint data:

- POST /auth/login
- POST /auth/register
- POST /auth/forgot-password
- GET /auth/me
- POST /complaints
- GET /complaints/my
- GET /dashboard/citizen
- GET /dashboard/mp
- GET /dashboard/officer
- GET /dashboard/super-admin

Claude Code may adjust endpoint names if current project already uses different names, but must keep API clean and documented in Swagger.

---

## 11. Seed Users

Update seed users with proper emails and passwords.

Example:

Citizen:
email: citizen@loktra.ai
password: citizen123

MP/Admin:
email: mp@loktra.ai
password: mp123456

Officer:
email: officer@loktra.ai
password: officer123

Super Admin:
email: admin@loktra.ai
password: admin123

Document these in README.

---

## 12. Testing Requirements

After implementation, verify:

- Invalid email is rejected.
- Wrong password does not login.
- Forgot password page accepts valid email only.
- Password is hashed.
- Role-based login redirects correctly.
- Citizen can submit complaint with latitude and longitude.
- Dashboards show latitude and longitude.
- MP cannot see other constituency complaints.
- Officer cannot see unrelated complaints.
- Super Admin can see all complaints.
- Swagger docs open correctly.
- App runs without errors.

---

## Important Rules

- Analyze the existing codebase before changing files.
- Do not remove Phase 1 UI.
- Do not rewrite everything.
- Keep changes modular.
- Keep dummy dataset clearly labeled as sample dataset.
- Do not claim real government dataset integration yet.
- Prepare code so real datasets can be added later.
- After changes, provide summary of files modified and testing steps.

## Final Expected Result

Authentication should feel real and professional.
Dataset should be honestly marked as sample/demo data.
Latitude and longitude should be stored and displayed across dashboards.
Role-based access should work correctly.