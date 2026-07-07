# Loktra AI — Phase 3.1 AI Guard Bug Fix + Dataset Foundation

## Context

Phase 3 AI layer was added, but civic relevance guard is weak.

Current bug:
A user submitted: "Who won yesterday's cricket match?"
The system accepted it as a complaint with category "Others" and priority score.

This is wrong.

Irrelevant content must be rejected before saving.

## Goal

Fix the AI Civic Relevance Guard and prepare the project for real government dataset integration.

Do not rewrite the full project.
Do not break auth, dashboards, complaint submission, or existing UI.

---

## 1. Civic Relevance Guard Must Be A Hard Gate

Complaint submission flow must be:

1. User submits complaint
2. Backend runs civic relevance guard
3. If civic-related, continue AI analysis and save
4. If not civic-related, reject immediately
5. Do not save rejected complaint in database

Return a clear API error:

"This platform accepts only civic and public governance related issues."

Frontend must show:

"Post Failed. This platform accepts only civic and public governance related issues."

---

## 2. Strong Irrelevant Content Blocking

Reject examples:

- Who won yesterday's cricket match?
- Tell me movie names
- Suggest me a good movie
- Sing a song
- Tell me a joke
- Best phone under 20000
- I love Virat Kohli
- How to play Free Fire
- Dating advice
- Random chat
- Celebrity news
- Sports scores
- Shopping requests

These must never be saved as complaints.

---

## 3. Allowed Civic Issues

Allow examples:

- Road potholes
- Drainage overflow
- Drinking water problem
- Power cut
- Street light not working
- Garbage not collected
- Hospital bed shortage
- School building damage
- Flooding
- Fire hazard
- Bridge crack
- Live electric wire
- Sewage issue
- Public transport issue
- Government service issue

---

## 4. Remove Weak "Others" Acceptance

If category is "Others", do not automatically allow.

"Others" should be allowed only when the description is clearly civic/public governance related.

Example allowed:
"Government office is not issuing certificates properly."

Example rejected:
"Who won the cricket match?"

---

## 5. Improve AI Service Logic

Claude Code should inspect current AI service and strengthen it.

Use a layered approach:

- civic keyword detection
- irrelevant keyword detection
- question intent detection
- entertainment/sports/shopping detection
- governance context check

If irrelevant signals are strong, reject.

Backend must not rely only on category detection.

---

## 6. Add Tests

Add or update tests for civic guard.

Must pass:

Rejected:
- cricket match
- movie suggestion
- song request
- joke request
- celebrity question
- shopping question
- game question

Accepted:
- road pothole
- water issue
- garbage issue
- drainage issue
- hospital issue
- school issue
- electricity issue
- public safety issue

---

## 7. Clean Existing Bad Data

Provide a safe script or admin utility to delete previously accepted irrelevant demo complaints.

Do not delete valid complaints.

At minimum, allow deleting complaint ID LOK-2026-000018 or any complaint containing cricket/movie/song/joke test content.

---

## 8. Real Government Dataset Foundation

Current dataset is sample data.

Keep it labelled as:
"Sample Government-Style Dataset"

But add import-ready support for real datasets.

Create a dataset import module that can accept CSV files later with fields like:

- state
- district
- constituency
- ward
- population
- schools_count
- hospitals_count
- road_access_score
- water_availability_score
- literacy_rate optional
- health_centres optional

Add backend structure for:

- importing CSV dataset
- validating required columns
- storing dataset records
- replacing sample data safely
- showing dataset source label

Do not hardcode fake data as real data.

---

## 9. Dataset Source Display

Dashboard/admin dataset page should clearly show:

Dataset Mode:
- Sample Data

Later it should support:
- Real Government Dataset Imported

Add fields:
- dataset_name
- source_name
- source_url optional
- imported_at
- is_official boolean

For now, set is_official = false.

---

## 10. Priority Score Must Use Dataset Safely

If real dataset is not available, use sample dataset.

If dataset value is missing, do not crash.

Priority scoring should handle missing population/schools/hospitals safely.

---

## 11. Acceptance Criteria

After implementation:

- Cricket complaint is rejected
- Movie complaint is rejected
- Valid road complaint is accepted
- Valid water complaint is accepted
- Rejected complaints are not saved
- Frontend shows proper post failed message
- Existing auth still works
- Existing dashboards still work
- Dataset is clearly labelled as sample
- CSV import foundation exists
- App builds without errors
- Backend tests pass

## Important Rules

- Analyze existing codebase first
- Do not rewrite full app
- Do not break current UI
- Do not integrate real dataset yet unless a real CSV is already provided
- Do not claim sample data is official
- Keep code modular
- Provide summary of changed files and test results