# Loktra AI — Phase 2 Backend Foundation Spec

## Context

Phase 1 frontend/citizen UI is already implemented.

Claude Code must inspect the existing codebase before making changes.

Do not rewrite the frontend unnecessarily.
Do not change the current UI design unless backend integration requires minimal changes.
Do not remove existing working features.

## Goal

Implement Phase 2: Backend Foundation for Loktra AI.

Loktra AI is an AI-powered constituency intelligence and decision support platform.

This phase must add a working FastAPI backend with SQLite, authentication, role-based access, database models, seed data, and APIs that can later connect to the existing frontend.

## Tech Requirements

Use:

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT authentication
- Password hashing
- CORS enabled for React frontend
- Clean modular backend architecture

## Backend Folder Structure

Claude Code should decide the best structure after analyzing the current repo, but the backend should be modular and include areas for:

- app entry point
- database configuration
- models
- schemas
- routers
- services
- auth utilities
- seed data
- AI service placeholder
- dashboard service

## Required User Roles

Implement role support for:

- Citizen
- Officer
- MP/Admin
- Super Admin

## Authentication Requirements

Implement:

- User registration
- User login
- JWT token generation
- Password hashing
- Current user endpoint
- Role-based protected endpoints

## Database Models Required

Create proper database models for:

- Users
- States
- Districts
- Constituencies
- Wards
- Departments
- Complaints
- Complaint status history
- Assignments
- Government dataset records

Relationships must support geo-based complaint routing.

## Geo-Based Routing Requirement

Every complaint must belong to:

State → District → Constituency → Ward/Village

A complaint should be visible only to:

- the citizen who created it
- the MP/Admin assigned to that constituency
- officers assigned to the correct department/area
- Super Admin

Other MPs must not see complaints outside their assigned constituency.

## Complaint Requirements

Complaints must support:

- complaint ID
- title
- description
- category
- language
- original text
- translated text placeholder
- image path placeholder
- state
- district
- constituency
- ward/village
- status
- priority score
- urgency
- AI summary
- AI reason/explanation
- created by user
- assigned department
- timestamps

Statuses:

- Submitted
- Verified
- Assigned
- Work Started
- Completed
- Rejected

## AI Placeholder Service

Create a backend AI service placeholder for Phase 3.

For now it should expose clean service functions for:

- civic relevance checking
- category detection
- urgency detection
- priority score calculation
- emergency detection
- AI summary generation
- AI reason generation

The logic can be basic/rule-based for now, but it must be modular so Gemini API can be added later.

## Civic Relevance Guard

Backend must reject irrelevant complaint submissions.

Allowed civic topics include:

- roads
- water supply
- electricity
- drainage
- garbage
- healthcare
- education
- street lights
- public transport
- public safety
- government services
- sanitation

Blocked topics include:

- movies
- songs
- celebrities
- games
- dating
- jokes
- random chat
- spam
- abusive content

If blocked, API should return a clear failure response.

## Government Dataset Seed Data

Create sample dataset records with fields such as:

- state
- district
- constituency
- population
- schools count
- hospitals count
- road access score
- water availability score

This data should be usable later in AI priority scoring.

## Required API Groups

Implement backend routes for:

- auth
- users
- complaints
- dashboard
- datasets
- admin

Claude Code may choose exact endpoint names after inspecting the project, but the API should be clean and documented through FastAPI Swagger.

## Dashboard API Requirements

Create dashboard APIs for:

Citizen:

- my complaints
- complaint tracking by complaint ID

MP/Admin:

- complaints only from assigned constituency
- total complaints
- high priority complaints
- emergency complaints
- completed complaints
- category distribution
- recent complaints
- ranked complaints

Officer:

- assigned complaints
- update complaint status
- add progress note

Super Admin:

- all complaints
- state-wise summary
- constituency-wise summary

## Seed Users

Create sample users for demo login:

- Citizen
- Officer
- MP/Admin
- Super Admin

Use simple demo credentials and document them in a backend README.

## Frontend Integration Preparation

Do not fully rewrite frontend.

Prepare backend APIs so the existing frontend can connect later.

If needed, add only minimal frontend API config files, but avoid major UI changes in this phase.

## Testing Requirements

After implementation, verify:

- backend starts without errors
- database creates successfully
- seed data loads successfully
- Swagger docs open
- login works
- protected routes work
- complaint submission works
- irrelevant complaint is blocked
- geo-based filtering works
- dashboard APIs return correct role-based data

## Documentation Requirements

Add/update README with:

- backend setup steps
- virtual environment setup
- install commands
- run command
- database seed command if separate
- API docs URL
- sample demo credentials

## Important Rules

- Analyze the existing codebase first.
- Do not delete working Phase 1 code.
- Do not rewrite frontend unnecessarily.
- Do not hardcode everything in one file.
- Keep backend modular.
- Keep code beginner-readable.
- Do not implement Phase 3 advanced AI yet.
- Do not integrate real government datasets yet.
- Use sample data only for this phase.
- After changes, provide a summary of what was added and how to run/test it.

## Final Expected Result

At the end of Phase 2, the project should have a working FastAPI backend with database, authentication, role-based access, complaint APIs, sample government dataset, seed users, and dashboard APIs ready for frontend integration.