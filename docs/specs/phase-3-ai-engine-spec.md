# Loktra AI — Phase 3 AI Intelligence Layer Spec

## Context

Phase 1 frontend and Phase 2 backend/auth are completed.

Before implementing, Claude Code must inspect the existing codebase and reuse current architecture.

Do not rewrite the full project.
Do not break existing login, registration, dashboards, or complaint submission.

## Goal

Implement the AI Intelligence Layer for Loktra AI.

The platform should not just store complaints. It should understand, validate, prioritize, explain, and route civic issues intelligently.

## Main AI Features

Implement:

1. AI Civic Relevance Guard
2. AI Complaint Analysis
3. Emergency Detection
4. Priority Score Calculation
5. Explainable AI Reasoning
6. Duplicate Complaint Detection foundation
7. Gemini-ready modular AI service with rule-based fallback

## AI Service Architecture

Create or improve AI service modules so the system supports:

- rule-based fallback AI
- future Gemini API integration
- clean service functions
- testable logic

Do not hardcode all AI logic inside routes.

The AI service should expose functions for:

- check_civic_relevance
- detect_category
- detect_urgency
- detect_emergency
- calculate_priority_score
- generate_summary
- generate_reason
- detect_possible_duplicates
- analyze_complaint

## Civic Relevance Guard

Before complaint creation, check whether the complaint is civic/governance-related.

Allowed civic topics:

- roads
- potholes
- water supply
- drinking water
- drainage
- sewage
- electricity
- power cuts
- garbage
- sanitation
- street lights
- healthcare
- hospitals
- schools
- education
- public transport
- public safety
- government services
- flooding
- pollution
- public infrastructure

Blocked irrelevant topics:

- movies
- songs
- celebrities
- games
- dating
- jokes
- random chat
- entertainment
- shopping
- personal promotion
- spam
- abusive content

If irrelevant, complaint submission must fail with a clear message:

"This platform accepts only civic and public governance related issues."

## Complaint Analysis

For valid complaints, AI should generate:

- detected category
- urgency level
- priority score
- short summary
- explanation/reason
- emergency flag

Urgency values:

- Low
- Medium
- High
- Emergency

Priority score:

- 0 to 100

## Emergency Detection

Detect emergencies like:

- bridge collapse
- building collapse
- fire
- flood
- water contamination
- live wire
- accident
- hospital oxygen shortage
- medicine shortage
- dangerous road damage
- sewage overflow near school/hospital
- public safety threat

Emergency complaints should:

- be marked urgency Emergency
- get high priority score
- display emergency flag in dashboard
- be easy to filter

## Priority Score Logic

Priority score should consider:

- emergency keywords
- urgency
- category severity
- population from sample government dataset
- nearby schools count
- nearby hospitals count
- road access score
- water availability score
- duplicate/similar complaint count
- complaint seriousness

Use sample government dataset for now.

Do not integrate real government datasets yet.

## Explainable AI

Every AI score must include explanation.

Example:

Priority Score: 94

Reason:
- Emergency keyword detected: live wire
- Public safety risk is high
- Constituency population is high
- Hospital/school access may be affected
- Similar complaints exist in the same area

The explanation should be stored with the complaint and shown in APIs.

## Duplicate Complaint Detection Foundation

Implement basic duplicate detection using existing complaints.

For now, use simple similarity logic based on:

- same constituency
- same ward
- same category
- similar words in title/description
- close latitude/longitude if available

Store or return:

- possible duplicate count
- possible duplicate complaint IDs
- duplicate group/fingerprint if suitable

Do not overcomplicate with embeddings yet.

## Backend Changes

Update complaint creation flow:

1. Receive complaint input.
2. Run civic relevance guard.
3. If invalid, reject.
4. If valid, run AI analysis.
5. Save complaint with AI results.
6. Return full complaint response.

Update complaint model/schema if needed to store:

- ai_category
- ai_urgency
- ai_priority_score
- ai_summary
- ai_reason
- is_emergency
- duplicate_count
- duplicate_group_key or duplicate references

## API Requirements

Ensure APIs return AI fields for:

- citizen complaints
- complaint tracking
- MP dashboard
- officer dashboard
- super admin dashboard

Add optional filters if suitable:

- urgency
- emergency
- category
- priority range

## Frontend Updates

Make minimal frontend updates only where useful.

Show AI results clearly:

On complaint card/details:

- AI Category
- Priority Score
- Urgency
- Emergency badge
- AI Summary
- Why this priority?
- Duplicate reports count if available

If irrelevant complaint is submitted, show a clean error message:

"Post Failed. This platform accepts only civic and public governance related issues."

Do not redesign the whole UI.

## Gemini Integration Readiness

Add environment variable support for future Gemini API:

- GEMINI_API_KEY

Do not require Gemini for the app to work.

If no API key is present, use rule-based fallback.

If Gemini wrapper is added, keep it optional and safe.

## Testing Requirements

After implementation, test:

1. Valid civic complaint is accepted.
2. Movie/song/random complaint is rejected.
3. Emergency complaint gets Emergency urgency.
4. Priority score is generated.
5. AI reason is generated.
6. Complaint tracking shows AI fields.
7. MP dashboard shows AI fields.
8. Officer dashboard shows AI fields.
9. Super Admin dashboard shows AI fields.
10. Duplicate complaints in same ward/category are detected.
11. App builds without errors.
12. Backend runs without errors.
13. Existing auth still works.

## Important Rules

- Analyze current code first.
- Reuse existing services/models/routes.
- Keep code modular.
- Do not rewrite the whole app.
- Do not remove working Phase 1 or Phase 2 features.
- Do not integrate real government datasets yet.
- Do not make Gemini mandatory.
- Keep rule-based fallback reliable.
- After implementation, provide modified files summary and testing steps.

## Final Expected Result

Loktra AI should now behave like an AI-powered civic intelligence platform.

Complaints should be validated, analyzed, scored, explained, emergency-tagged, and duplicate-checked before appearing in role-based dashboards.