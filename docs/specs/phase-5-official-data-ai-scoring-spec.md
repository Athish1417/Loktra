# Phase 5 — Official Government Dataset AI Prioritisation

## Goal

Integrate imported official government datasets into Loktra AI's complaint prioritisation engine so that AI uses real government data instead of relying only on sample values whenever official data is available.

---

## Background

Phase 4 successfully implemented:

- Official dataset import
- Dataset source management
- Dataset mode (Official / Sample Fallback)
- Census dataset
- LGD dataset
- NFHS datasets

Now these datasets must influence AI prioritisation.

---

## Requirements

### 1. Dataset lookup

Whenever a complaint is submitted:

- Detect location
- Find matching official dataset
- Match using:
  - State
  - District
  - Constituency
  - Village
  - Ward
  - PIN code (if available)

If multiple datasets exist:

Use all matching datasets.

---

### 2. Census influence

Use Census data to improve priority using information like:

- Population
- Household count
- Density (if available)

Highly populated areas should receive slightly higher priority for infrastructure complaints.

---

### 3. LGD influence

Use LGD dataset for:

- Village validation
- Panchayat validation
- Administrative hierarchy

Improve location confidence.

---

### 4. NFHS influence

Use NFHS information for complaints involving:

- Health
- Water
- Sanitation
- Nutrition
- Women
- Children

Increase AI confidence when official health indicators support higher urgency.

---

### 5. AI Explanation

When official data is used, AI explanation should mention it naturally.

Example:

"This priority was enhanced using official Census and NFHS government datasets."

Do NOT expose raw database values.

---

### 6. Dashboard

Admin dashboard should continue ranking complaints.

Ranking should now consider:

- Complaint severity
- Emergency keywords
- Official dataset context
- Population
- Health indicators
- Infrastructure indicators

---

### 7. Complaint Details

Each complaint should display:

Dataset Mode:

Official Government Dataset

or

Sample Fallback Dataset

Also display:

Matched datasets:

- Census
- LGD
- NFHS

(if applicable)

---

### 8. Fallback

If no official dataset matches:

Automatically use sample dataset.

System must never crash.

---

### 9. Existing Features

Do NOT break:

- Authentication
- Complaint submission
- AI Guard
- Admin dashboard
- Dataset importer
- Dataset management
- Existing APIs

---

### 10. Code Quality

- Modular
- No hardcoded districts
- Reusable lookup functions
- Handle missing fields safely
- Clean logging

---

## Acceptance Tests

✓ Submit complaint inside imported district

✓ AI uses official datasets

✓ Dashboard ranking changes accordingly

✓ Complaint page shows Official Dataset Mode

✓ AI explanation references official datasets

✓ Unknown location falls back safely

✓ Frontend builds

✓ Backend runs

✓ Existing tests continue passing

---

## Deliverables

- Updated backend AI scoring
- Updated complaint prioritisation
- Updated complaint details
- Official dataset lookup module
- Final implementation summary