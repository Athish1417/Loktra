# Loktra AI — Phase 4 Official Dataset Import Spec

## Context

Phase 1 UI, Phase 2 auth/backend, and Phase 3 AI Civic Guard are working.

Now official government datasets have been downloaded and must be integrated.

Claude Code must inspect the existing codebase first.

Do not rewrite the full app.
Do not break auth, AI guard, complaint submission, dashboards, or routing.

## Goal

Build a robust official dataset import system and connect imported government data to Loktra AI dashboards, location intelligence, and AI priority scoring.

## Dataset Folders

Create/use this structure:

datasets/
  census/
  lgd/
  pincode/
  nfhs/
  election/
  imports/

The user will place downloaded files in these folders.

## Downloaded Dataset Types

Support these official datasets:

1. Census Population Dataset
2. LGD Villages Dataset
3. All India PIN Code Directory
4. NFHS District Factsheet
5. NFHS State/UT Factsheet
6. Constituency Data Summary Report 2024
7. Parliamentary Constituency-wise Summary 2024
8. Constituency-wise Detailed Result 2024

## Important

Do not assume exact file names or column names.

Government files may be:
- CSV
- XLS
- XLSX

They may contain:
- inconsistent headers
- merged rows
- extra notes
- multiple sheets
- blank rows

Claude Code must inspect available files and build flexible import logic.

## Backend Requirements

Create/extend dataset import services to:

- scan dataset folders
- list detected files
- preview file sheets/columns
- normalize column names
- detect dataset type
- validate useful fields
- import rows safely
- skip bad rows
- store import summary
- avoid duplicate imports
- allow re-import/replacement

## Database Requirements

Create/update tables for:

- dataset_sources
- population_records
- lgd_location_records
- pincode_records
- nfhs_records
- election_constituency_records

Each dataset source should store:

- dataset_name
- source_department
- file_name
- file_path
- source_url optional
- is_official
- imported_at
- record_count
- import_status

## AI Integration

Update AI priority scoring to use official data when available.

Use:

- Census population for population weighting
- LGD for village/location matching
- PIN code directory for location validation
- NFHS for health/sanitation/water indicators
- Election constituency data for constituency context

If official data is missing, safely fall back to sample dataset.

Never crash if a dataset is incomplete.

## Dashboard Integration

Admin/Super Admin dashboard should show:

- Dataset Mode: Official Government Dataset Imported
- Number of imported datasets
- Last import date
- Dataset source cards
- Record counts
- Import status

Complaint detail / AI assessment should mention when real dataset context is used.

Example:
"Priority enhanced using imported Census/NFHS dataset context."

## API Requirements

Add or update endpoints for:

- list dataset files
- preview dataset file
- import dataset file
- list imported sources
- view import summary
- delete/reimport dataset source if safe

Use current backend architecture and route naming style.

## Frontend Requirements

Add minimal UI only if needed.

Prefer adding a Super Admin dataset management page or improving existing dataset page.

Features:

- show detected dataset files
- preview columns
- import button
- import summary
- official/sample dataset badge

Do not redesign the full app.

## README Update

Update README with:

- dataset folder structure
- where to place files
- supported dataset types
- how to run import
- how to verify import
- what official datasets are used
- fallback behavior

## Testing Requirements

Verify:

- backend starts
- frontend builds
- existing login works
- AI guard still rejects cricket/movie complaints
- files are detected in dataset folders
- preview works for CSV/XLS/XLSX
- import works for at least one file from each folder
- imported record counts are shown
- dashboard shows official dataset mode
- AI scoring uses imported data when matching location exists
- fallback works when data is missing
- no crashes from messy Excel files

## Important Rules

- Analyze existing code first.
- Do not rewrite full project.
- Do not remove sample data fallback.
- Do not hardcode exact file names.
- Do not falsely label sample data as official.
- Keep importer flexible and defensive.
- Keep code beginner-readable.
- Provide final summary of modified files and test steps.

## Final Expected Result

Loktra AI should now support importing official government datasets from downloaded CSV/XLS/XLSX files and use them in dataset dashboards, AI priority scoring, and location intelligence while keeping fallback behavior stable.