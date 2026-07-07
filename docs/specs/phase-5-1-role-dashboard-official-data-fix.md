# Loktra AI — Phase 5.1 Role Dashboard + Official Dataset Fix

## Goal
Fix role dashboards before MVP polish.

## Current Issues
1. MP dashboard is not showing newly submitted/updated problems properly.
2. Updates/status changes are not reflected across Citizen, MP, Officer, and Admin views.
3. MP and Officer portals still show fallback/sample dataset context.
4. Official dataset mode should be used wherever official data is available.
5. MP dashboard should quickly surface important/critical problems.
6. Maharashtra/Telangana sample fallback should remain only as fallback, not primary mode.

## Requirements

### 1. MP Dashboard Complaint Visibility
MP dashboard must show complaints that belong to the MP’s assigned constituency/state/district.

It must include:
- newly submitted complaints
- verified complaints
- assigned complaints
- work started complaints
- completed complaints
- updated complaints

Do not hide complaints just because status changed.

### 2. Status Sync Across Roles
When status is updated from any role:
- Citizen My Reports must update
- MP dashboard must update
- Officer dashboard must update
- Admin dashboard must update
- Track report page must update

Use backend as the source of truth.

### 3. Official Dataset Context Everywhere
Complaint detail and dashboard cards in:
- Citizen portal
- MP portal
- Officer portal
- Admin portal

must show:
- Dataset Mode: Official Government Dataset
- Matched datasets if available

Only show Sample Fallback Dataset when no official dataset match exists.

### 4. MP Priority Alert Section
Add a section at the top of MP dashboard:

Critical Issues Needing Attention

Show complaints with:
- priority_score >= 85
- urgency Emergency or High
- public safety risk
- official dataset context
- duplicate count if available

Sort by highest priority first.

### 5. Officer Dashboard
Officer dashboard should show assigned complaints and official dataset context.

Officer must see:
- complaint priority
- urgency
- category
- location
- AI reason
- dataset mode
- matched datasets
- status update controls

### 6. Real Dataset Usage
Use official imported datasets for scoring/context wherever possible.

Fallback sample data should only be used when:
- no official match exists
- official datasets are missing
- matching fails safely

### 7. Filtering
Add or fix filters where needed:
- status
- urgency
- category
- priority
- dataset mode
- constituency

### 8. Testing
Verify:
- New citizen complaint appears in MP dashboard
- Status update appears everywhere
- MP critical section shows high priority issues
- Officer dashboard shows assigned complaints
- Dataset mode is official where matched
- Sample fallback only appears for unmatched locations
- AI guard still rejects cricket/movie/joke complaints
- Backend and frontend build successfully

## Important Rules
- Do not rewrite full app.
- Do not break auth.
- Do not break official dataset importer.
- Do not remove sample fallback.
- Do not hardcode only Maharashtra/Telangana.
- Use backend APIs as source of truth.
- Keep changes surgical.
- Provide final summary and test steps.