# Loktra AI — Phase 4 Real Government Dataset Import Spec

## Context

Phase 1 UI, Phase 2 backend/auth, and Phase 3 AI guard are completed.

Now add real government dataset support.

Claude Code must inspect the existing codebase first.

Do not rewrite the full project.
Do not break login, registration, dashboards, complaint submission, or AI guard.

## Dataset Folder Requirement

Create this folder structure if it does not exist:

datasets/
  census/
  lgd/
  pincode/
  nfhs/
  imports/

The user will manually place downloaded official files inside these folders.

## Goal

Build a real dataset import system that can read official CSV/XLS/XLSX government datasets and store normalized useful information in the database.

## Current Datasets

Support these downloaded datasets:

1. Census Population Dataset
Folder: datasets/census/

2. LGD Villages Dataset
Folder: datasets/lgd/

3. All India PIN Code Directory
Folder: datasets/pincode/

4. NFHS District Factsheet
Folder: datasets/nfhs/

5. NFHS State/UT Factsheet
Folder: datasets/nfhs/

## Important Dataset Rule

Do not assume exact column names.

Government datasets may have inconsistent headers.

Claude Code should inspect files, detect sheets/columns, and build robust mapping logic.

## Required Features

### 1. Dataset Import Service

Create backend services to:

- scan dataset folders
- detect CSV/XLS/XLSX files
- preview columns
- validate required data
- normalize useful columns
- import records into database
- skip invalid rows safely
- return import summary

### 2. Dataset Tables

Add database models/tables as needed for:

- dataset_sources
- population_records
- lgd_location_records
- pincode_records
- nfhs_records

Include fields like:

- dataset_name
- source_name
- source_type
- file_name
- imported_at
- is_official
- record_count
- state
- district
- subdistrict/taluk optional
- village optional
- pincode optional
- population optional
- households optional
- area optional
- health indicators optional

### 3. Admin Dataset Page/API

Add APIs for:

- list available dataset files
- preview dataset file columns
- import selected dataset
- view imported dataset sources
- view import summary

Use endpoints under something like:

/admin/datasets
/datasets/import
/datasets/preview

Use current project architecture.

### 4. Dataset Mode Display

Update UI/admin dashboard to show:

Dataset Mode:
Official Government Dataset Imported

If no real dataset has been imported, show:

Dataset Mode:
Sample Government-Style Dataset

Do not falsely label sample data as official.

### 5. AI Priority Engine Integration

Update AI priority scoring so it uses imported real dataset records when available.

Use:

- population from Census
- village/location data from LGD
- pincode/district mapping from PIN Code Directory
- health indicators from NFHS

If data is missing, fallback safely to sample dataset.

System must never crash if real data is missing or partially imported.

### 6. Location Intelligence

Use imported datasets to improve:

- state/district validation
- ward/village matching
- pincode lookup if pincode exists
- constituency/area context where possible

Do not force exact matching if the dataset is incomplete.

Use safe fuzzy/normalized matching.

### 7. README Update

Update README with:

- where to place dataset files
- supported folders
- how to run import
- how to verify import
- what datasets are official
- what fields are currently used by AI scoring

### 8. Testing Requirements

Verify:

- backend starts
- frontend builds
- existing login works
- existing AI guard still rejects cricket/movie complaints
- dataset folders are detected
- dataset files can be previewed
- datasets can be imported
- import summary shows record count
- AI scoring uses real data when available
- app falls back to sample data when no dataset exists
- no crash with missing columns

## Important Rules

- Analyze existing codebase before changes.
- Do not rewrite full app.
- Do not remove sample dataset fallback.
- Do not claim data is official unless imported from dataset folders.
- Do not hardcode one exact file name.
- Keep importer flexible.
- Keep code beginner-readable.
- Provide final summary of files changed and commands to test.

## Final Expected Result

Loktra AI should support real government dataset imports from downloaded official files and use them in AI scoring, dashboards, and location intelligence while still falling back safely to sample data.