# Loktra AI — Phase 5.2 Map + Location Search Fix

## Goal
Improve map view and citizen location selection before MVP polish.

## Current Issues
1. MP dashboard map is plain/empty-looking.
2. Need Google-map-like satellite/map toggle view.
3. Citizen report form location search does not find cities/districts like Visakhapatnam.
4. State/district/constituency/ward selectors are too limited and depend on fallback sample data.

## Requirements

### 1. Map View Upgrade
Update MP/Admin map to support:
- Street map view
- Satellite-like view if available through free/open tile layer
- Toggle button: Map / Satellite
- Complaint markers with colors:
  - Critical = red
  - High = orange
  - Medium = blue
  - Low = green
- Marker popup with complaint title, score, category, status, and open-detail link

Use current map library if already installed. Do not add paid Google Maps dependency unless API key support already exists.

### 2. Official Dataset Location Search
Citizen report form must use imported official location datasets where available:
- LGD villages
- Census districts/subdistricts
- Pincode directory if imported
- Existing app locations as fallback

Search should support:
- state
- district
- city
- constituency
- ward/village
- partial text search
- case-insensitive search

Example:
Searching `visakhapatnam` should show matching district/city options if available in imported data.

### 3. Location Selector Behaviour
When user selects:
- State → district list should update
- District → constituency/city/ward options should update
- Ward/village optional but searchable

Do not restrict only to Maharashtra/Telangana sample data.

### 4. Fallback Rule
Use official imported location data first.
Use sample fallback only if no official data exists.

### 5. Backend APIs
Add or reuse APIs for:
- searching locations
- listing states
- listing districts by state
- listing wards/villages by district
- map complaint points

Do not duplicate existing APIs if they already exist.

### 6. Testing
Verify:
- MP map shows markers
- Map/Satellite toggle works
- Citizen form can search official dataset locations
- Maharashtra/Telangana sample still works as fallback
- Complaint submission still works
- AI guard still rejects off-topic posts
- Frontend builds
- Backend tests pass

## Important Rules
- Do not rewrite full app.
- Do not break auth.
- Do not break official dataset importer.
- Do not remove fallback system completely from backend.
- Make only surgical changes.