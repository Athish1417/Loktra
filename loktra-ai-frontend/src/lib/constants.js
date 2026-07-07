// Central UI constants mirroring the backend enums, plus presentation metadata
// (colors, labels) and approximate map coordinates for the seeded constituencies.

export const CATEGORIES = [
  "Roads",
  "Water Supply",
  "Electricity",
  "Drainage",
  "Garbage",
  "Healthcare",
  "Education",
  "Street Lights",
  "Public Transport",
  "Public Safety",
  "Government Services",
  "Others",
];

export const LANGUAGES = [
  { code: "en", label: "English", speech: "en-IN" },
  { code: "hi", label: "हिंदी (Hindi)", speech: "hi-IN" },
  { code: "te", label: "తెలుగు (Telugu)", speech: "te-IN" },
  { code: "ta", label: "தமிழ் (Tamil)", speech: "ta-IN" },
  { code: "kn", label: "ಕನ್ನಡ (Kannada)", speech: "kn-IN" },
  { code: "ml", label: "മലയാളം (Malayalam)", speech: "ml-IN" },
  { code: "mr", label: "मराठी (Marathi)", speech: "mr-IN" },
  { code: "bn", label: "বাংলা (Bengali)", speech: "bn-IN" },
];

// Per-complaint dataset provenance (mirrors backend complaint_service). The UI
// only ever shows these two — never any "sample/fallback" wording.
export const OFFICIAL_DATASET_MODE = "Official Government Dataset";
export const NO_MATCH_DATASET_MODE = "No Official Dataset Match";
export const isOfficialComplaint = (c) =>
  c?.dataset_mode === OFFICIAL_DATASET_MODE;

// Workflow order — used to render progress rails.
export const STATUS_FLOW = [
  "Submitted",
  "Verified",
  "Assigned",
  "Work Started",
  "Completed",
];

export const STATUS_META = {
  Submitted: { color: "#5B6178", bg: "#EEF0F5", label: "Submitted" },
  Verified: { color: "#3B49C4", bg: "#E7E9FB", label: "Verified" },
  Assigned: { color: "#7C3AED", bg: "#EDE7FB", label: "Assigned" },
  "Work Started": { color: "#F5820B", bg: "#FDEBD3", label: "Work Started" },
  Completed: { color: "#12A150", bg: "#D8F1E2", label: "Completed" },
};

export const URGENCY_META = {
  Emergency: { color: "#E5484D", bg: "#FBE3E4", rank: 4 },
  High: { color: "#F5820B", bg: "#FDEBD3", rank: 3 },
  Medium: { color: "#3B82F6", bg: "#E3EDFD", rank: 2 },
  Low: { color: "#64748B", bg: "#EEF0F5", rank: 1 },
};

// Color for the AI priority score (0-100).
export function priorityColor(score) {
  if (score >= 80) return "#E5484D";
  if (score >= 60) return "#F5820B";
  if (score >= 40) return "#3B82F6";
  return "#64748B";
}

export function priorityLabel(score) {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Moderate";
  return "Low";
}

// Approximate [lat, lng] centroids so the map is populated even for seeded
// complaints that have no explicit coordinates. Names match the seed data.
export const CONSTITUENCY_COORDS = {
  Goregaon: [19.1663, 72.849],
  "Andheri West": [19.1351, 72.8264],
  Serilingampally: [17.4482, 78.3915],
  Kukatpally: [17.4948, 78.3996],
};

export const DEFAULT_MAP_CENTER = [19.076, 72.8777];

// Deterministic small offset from a complaint id, so pins spread around the
// constituency centroid instead of stacking.
export function jitter(id, base) {
  const seed = (id * 9301 + 49297) % 233280;
  const r = seed / 233280;
  const seed2 = (id * 4021 + 7919) % 199933;
  const r2 = seed2 / 199933;
  return [base[0] + (r - 0.5) * 0.03, base[1] + (r2 - 0.5) * 0.035];
}
