# Phase 4 – Official Dataset Admin UI

## Goal
Replace the current sample dataset editor with an Official Dataset Management page.

## Requirements

### 1. Add an Import Dataset section
- Upload CSV/XLS/XLSX files.
- Show supported formats.
- Allow drag-and-drop.

### 2. Preview before import
- Display detected columns.
- Show first 10 rows.
- Detect dataset type automatically.
- Allow Replace or Merge mode.

### 3. Dataset Sources
Display imported datasets with:
- Dataset name
- Department
- Status
- Import date
- Number of records
- Official/Sample badge
- Delete button

### 4. Dataset Mode
If at least one official dataset exists:
- Switch to Official Dataset Mode
Otherwise:
- Stay in Sample Mode

### 5. Do NOT modify
- Authentication
- Complaint flow
- AI prioritization
- Existing backend importer

### 6. Connect to existing backend APIs
Reuse all APIs already implemented.
Do not rewrite backend logic.

### 7. Keep existing styling
Match the current LoktraAI admin dashboard design exactly.

### Success Criteria
- Admin can upload official datasets.
- Preview works.
- Import works.
- Dataset list updates.
- Official badge appears.
- Existing functionality remains unchanged.