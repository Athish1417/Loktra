# Government datasets

Place downloaded **official** government dataset files in the matching folder.
The importer auto-detects `.csv`, `.xlsx`, and `.xls` files here — it does **not**
assume exact column names, so slightly different official headers are fine.

| Folder      | Dataset                          | Example source |
|-------------|----------------------------------|----------------|
| `census/`   | Census population data           | censusindia.gov.in |
| `lgd/`      | LGD villages / local directory   | lgdirectory.gov.in |
| `pincode/`  | All-India PIN Code directory     | data.gov.in |
| `nfhs/`     | NFHS district / state factsheets | rchiips.org/nfhs |
| `imports/`  | Any other / generic dataset      | — |

Nothing here is committed except `.gitkeep` and this README — the actual data
files are git-ignored. Until you import a file the app keeps its clearly-labelled
**Sample Government-Style Dataset**.

## How to import

1. Drop a file into the right folder (e.g. `census/population.csv`).
2. As Super Admin: `GET /api/v1/datasets/files` to see detected files, then
   `POST /api/v1/datasets/preview` to inspect columns, then
   `POST /api/v1/datasets/import-file` to import it.
3. `GET /api/v1/datasets/sources` shows the import log (record counts), and
   `GET /api/v1/datasets/source` shows the current **Dataset Mode**.

See the backend `README.md` for the full walkthrough and which fields the AI
priority engine currently uses.
