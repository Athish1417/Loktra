# Loktra AI — Phase 5.2 Official-Only UI + India Location System

## Goal
Keep fallback only as hidden backend safety, but remove all fallback wording from the UI and operational dashboards.

## Important Rule
Do NOT delete backend safety fallback logic completely.
It may remain internally to prevent crashes.

But the UI must never show:
- Sample Dataset
- Sample Fallback Dataset
- Fallback Dataset
- Sample Context

Use only:
- Official Government Dataset
- No Official Dataset Match

## 1. Dataset Display Rules

If official dataset match exists, show:

Dataset Mode: Official Government Dataset

Matched datasets:
- Census
- LGD
- NFHS
- PIN

If no official match exists, show:

Dataset Mode: No Official Dataset Match

Never show fallback wording in any UI.

## 2. MP Dashboard

MP dashboard should show only official-dataset-backed complaints.

Hide complaints with No Official Dataset Match.

Critical Issues section must also show only official-backed complaints.

Sort by highest priority first.

Add helper text:

Showing official-dataset-backed complaints only.

## 3. Officer Dashboard

Officer dashboard should show only assigned official-dataset-backed complaints.

Hide No Official Dataset Match complaints.

Status updates must still sync everywhere.

## 4. Admin Dashboard

Admin can view all complaints.

Add dataset mode filter:

- All
- Official Government Dataset
- No Official Dataset Match

Admin cards must clearly show dataset mode.

## 5. Citizen Portal

Citizens can submit from any location.

If official data matches:
- show Official Government Dataset

If official data does not match:
- show No Official Dataset Match

Do not show fallback wording.

## 6. India-Wide Location Selection

Replace hardcoded Maharashtra/Telangana dropdowns.

Use imported official datasets to populate:

- State
- District
- Constituency / City
- Ward / Village

Use LGD, PIN, Census, NFHS, or imported official records.

Dropdowns must be searchable.

Flow:

State → District → Constituency/City → Ward/Village

No long scrolling lists.

## 7. Submission Rules

Citizen complaint should still submit even if no official match exists.

For unmatched locations:
- dataset_mode = No Official Dataset Match
- matched_datasets = empty

Do not invent sample values.

Do not expose backend fallback values.

## 8. Remove Sample UI

Remove/hide sample dataset editor from Admin Dataset page.

Remove all fallback/sample badges from:
- Citizen dashboard
- MP dashboard
- Officer dashboard
- Admin dashboard
- Complaint detail page
- Track report page

## 9. Preserve Existing Features

Do not break:
- Auth
- AI guard
- Dataset import
- Official dataset scoring
- Complaint submission
- Status updates
- Track report
- Dashboards

## 10. Testing

Verify:
- frontend builds
- backend imports
- auth works
- AI guard rejects cricket/movie/joke posts
- official dataset import still works
- official complaint shows Official Government Dataset
- unmatched complaint shows No Official Dataset Match
- MP dashboard hides unmatched complaints
- Officer dashboard hides unmatched complaints
- Admin filter works
- location dropdowns are searchable
- hardcoded Maharashtra/Telangana sample dependency is removed
- no UI contains fallback/sample wording

## Output

After implementation, provide:
- files modified
- summary of changes
- test results
- remaining limitations