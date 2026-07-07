import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import * as loc from "../api/locations";
import SearchableSelect from "./ui/SearchableSelect";

/**
 * Controlled State → District → Constituency/City → Ward/Village picker.
 * Each level is a searchable dropdown (type to filter — no long scrolling lists)
 * populated from the locations API, which serves every state/district loaded on
 * the backend (not a hardcoded region).
 *
 * Props:
 *   value    { state_id, district_id, constituency_id, ward_id }
 *   onChange (patch) => void   — receives a partial update to merge into the parent form
 *   wardLabel  optional label override for the ward field
 */
export default function LocationCascade({ value, onChange, wardLabel = "Ward / Village (optional)" }) {
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [constituencies, setConstituencies] = useState([]);
  const [wards, setWards] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  useEffect(() => {
    loc.getStates().then(setStates).catch(() => {});
  }, []);

  async function onSearch(e) {
    const v = e.target.value;
    setQuery(v);
    if (v.trim().length < 2) {
      setResults([]);
      return;
    }
    setResults(await loc.searchLocations(v.trim()).catch(() => []));
  }

  async function jump(r) {
    onChange({
      state_id: r.state_id || "",
      district_id: r.district_id || "",
      constituency_id: r.constituency_id || "",
      ward_id: r.ward_id || "",
    });
    // Load the dependent option lists so each dropdown shows the picked value.
    setDistricts(r.state_id ? await loc.getDistricts(r.state_id).catch(() => []) : []);
    setConstituencies(
      r.district_id ? await loc.getConstituencies(r.district_id).catch(() => []) : []
    );
    setWards(r.constituency_id ? await loc.getWards(r.constituency_id).catch(() => []) : []);
    setQuery("");
    setResults([]);
  }

  function onState(state_id) {
    onChange({ state_id, district_id: "", constituency_id: "", ward_id: "" });
    setDistricts([]); setConstituencies([]); setWards([]);
    if (state_id) loc.getDistricts(state_id).then(setDistricts).catch(() => {});
  }
  function onDistrict(district_id) {
    onChange({ district_id, constituency_id: "", ward_id: "" });
    setConstituencies([]); setWards([]);
    if (district_id) loc.getConstituencies(district_id).then(setConstituencies).catch(() => {});
  }
  function onConstituency(constituency_id) {
    onChange({ constituency_id, ward_id: "" });
    setWards([]);
    if (constituency_id) loc.getWards(constituency_id).then(setWards).catch(() => {});
  }

  const opts = (rows) => rows.map((r) => ({ value: r.id, label: r.name }));

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        <input
          className="input pl-9"
          placeholder="Search any state, district, city or village…"
          value={query}
          onChange={onSearch}
        />
        {results.length > 0 && (
          <div className="absolute z-30 mt-1 max-h-60 w-full overflow-y-auto rounded-xl border border-hairline bg-white py-1 shadow-lift">
            {results.map((r) => (
              <button
                key={`${r.type}-${r.ward_id || r.constituency_id || r.district_id || r.state_id}`}
                type="button"
                onClick={() => jump(r)}
                className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm transition hover:bg-paper"
              >
                <span className="truncate text-body">{r.label}</span>
                <span className="shrink-0 text-[11px] capitalize text-muted">{r.type}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <label className="label">State</label>
        <SearchableSelect
          ariaLabel="State"
          value={value.state_id}
          onChange={onState}
          options={opts(states)}
          placeholder="Select state"
        />
      </div>
      <div>
        <label className="label">District</label>
        <SearchableSelect
          ariaLabel="District"
          value={value.district_id}
          onChange={onDistrict}
          options={opts(districts)}
          placeholder="Select district"
          disabled={!districts.length}
        />
      </div>
      <div>
        <label className="label">Constituency / City</label>
        <SearchableSelect
          ariaLabel="Constituency or city"
          value={value.constituency_id}
          onChange={onConstituency}
          options={opts(constituencies)}
          placeholder="Select constituency"
          disabled={!constituencies.length}
        />
      </div>
      <div>
        <label className="label">{wardLabel}</label>
        <SearchableSelect
          ariaLabel="Ward or village"
          value={value.ward_id}
          onChange={(ward_id) => onChange({ ward_id })}
          options={opts(wards)}
          placeholder="Select ward"
          disabled={!wards.length}
        />
      </div>
      </div>
    </div>
  );
}
