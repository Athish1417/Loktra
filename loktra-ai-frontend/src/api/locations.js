import client from "./client";

export const getStates = () =>
  client.get("/api/v1/locations/states").then((r) => r.data);

export const getDistricts = (stateId) =>
  client
    .get("/api/v1/locations/districts", { params: { state_id: stateId } })
    .then((r) => r.data);

export const getConstituencies = (districtId) =>
  client
    .get("/api/v1/locations/constituencies", { params: { district_id: districtId } })
    .then((r) => r.data);

export const getWards = (constituencyId) =>
  client
    .get("/api/v1/locations/wards", { params: { constituency_id: constituencyId } })
    .then((r) => r.data);

// Free-text, case-insensitive search across states/districts/cities/wards.
export const searchLocations = (q) =>
  client
    .get("/api/v1/locations/search", { params: { q } })
    .then((r) => r.data);

// Cache an id -> {name, districtId, stateId} index for resolving a complaint's
// constituency name (used for map coordinates) — the payload carries only ids.
// One flat request instead of walking the whole tree (fast even with all-India seeded).
let _indexCache = null;
export async function getConstituencyIndex() {
  if (_indexCache) return _indexCache;
  const rows = await client
    .get("/api/v1/locations/constituencies-index")
    .then((r) => r.data);
  const index = {};
  for (const c of rows) {
    index[c.id] = { name: c.name, districtId: c.district_id, stateId: c.state_id };
  }
  _indexCache = index;
  return index;
}
