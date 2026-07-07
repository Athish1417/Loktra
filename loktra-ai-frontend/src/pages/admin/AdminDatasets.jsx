import { useEffect, useState } from "react";
import {
  Loader2,
  Trash2,
  Database,
  UploadCloud,
  FileText,
  X,
  CheckCircle2,
} from "lucide-react";
import usePageHeader from "../../lib/usePageHeader";
import {
  datasetSource,
  datasetSources,
  deleteDatasetSource,
  uploadDataset,
  previewDataset,
  importDatasetFile,
} from "../../api/admin";
import { errorMessage } from "../../api/client";
import { useToast } from "../../components/ui/Toast";

const TYPE_OPTIONS = [
  { value: "census", label: "Census Population" },
  { value: "lgd", label: "LGD Villages" },
  { value: "pincode", label: "PIN code directory" },
  { value: "nfhs", label: "NFHS dataset" },
  { value: "election", label: "Election/Constituency dataset" },
  { value: "imports", label: "Other / generic" },
];
const TYPE_LABEL = Object.fromEntries(TYPE_OPTIONS.map((o) => [o.value, o.label]));

export default function AdminDatasets() {
  usePageHeader(
    "Official datasets",
    "Import and manage government datasets that inform AI prioritisation"
  );
  const toast = useToast();

  const [source, setSource] = useState(null);
  const [sources, setSources] = useState([]);

  // Import wizard
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [staged, setStaged] = useState(null); // { path, file_name }
  const [type, setType] = useState("census");
  const [preview, setPreview] = useState(null);
  const [previewing, setPreviewing] = useState(false);
  const [replace, setReplace] = useState(false);
  const [department, setDepartment] = useState("");
  const [importing, setImporting] = useState(false);

  function refresh() {
    return Promise.all([datasetSources(), datasetSource()]).then(([s, m]) => {
      setSources(s);
      setSource(m);
    });
  }

  useEffect(() => {
    datasetSource().then(setSource).catch(() => {});
    datasetSources().then(setSources).catch(() => setSources([]));
  }, []);

  // ---- import wizard ----
  async function handleFile(file) {
    if (!file) return;
    const ext = file.name.toLowerCase().split(".").pop();
    if (!["csv", "xls", "xlsx"].includes(ext)) {
      toast.error("Upload a CSV, XLS, or XLSX file.");
      return;
    }
    setUploading(true);
    setPreview(null);
    try {
      const up = await uploadDataset(file);
      setStaged({ path: up.path, file_name: up.file_name });
      const t = up.suggested_type || "census";
      setType(t);
      await runPreview(up.path, t);
    } catch (err) {
      toast.error(errorMessage(err, "Upload failed."));
    } finally {
      setUploading(false);
    }
  }

  async function runPreview(path, t) {
    setPreviewing(true);
    try {
      setPreview(await previewDataset(path, t));
    } catch (err) {
      toast.error(errorMessage(err, "Preview failed."));
    } finally {
      setPreviewing(false);
    }
  }

  function onTypeChange(t) {
    setType(t);
    if (staged) runPreview(staged.path, t);
  }

  function cancelImport() {
    setStaged(null);
    setPreview(null);
    setDepartment("");
    setReplace(false);
  }

  async function doImport() {
    if (!staged) return;
    setImporting(true);
    try {
      const res = await importDatasetFile({
        path: staged.path,
        source_type: type,
        is_official: true,
        replace,
        source_name: staged.file_name,
        dataset_name: TYPE_LABEL[type],
        source_department: department || undefined,
      });
      if (res.status === "skipped_duplicate") {
        toast.info("This file is already imported — enable Replace to re-import.");
      } else {
        toast.success(`Imported ${res.record_count} record(s)`);
        cancelImport();
        await refresh();
      }
    } catch (err) {
      toast.error(errorMessage(err, "Import failed."));
    } finally {
      setImporting(false);
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  async function removeSource(id) {
    try {
      await deleteDatasetSource(id);
      await refresh();
      toast.success("Dataset source removed");
    } catch (err) {
      toast.error(errorMessage(err));
    }
  }

  const hasOfficial =
    sources.some((s) => s.is_official && s.record_count > 0) ||
    Boolean(source?.is_official);

  const lastImport = sources[0]?.imported_at
    ? new Date(sources[0].imported_at).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : null;

  return (
    <div className="space-y-4">
      {/* Dataset Mode */}
      <div className="flex items-start gap-2 rounded-xl border border-hairline bg-paper/60 p-3">
        <span
          className={`chip shrink-0 ${
            hasOfficial
              ? "bg-success/10 text-success"
              : "bg-saffron-100 text-saffron-600"
          }`}
        >
          Dataset Mode:{" "}
          {hasOfficial
            ? "Official Government Dataset"
            : "No Official Dataset Match"}
        </span>
        <p className="text-sm text-muted">
          {hasOfficial ? (
            "Loktra is using imported official government datasets for AI prioritisation and location intelligence."
          ) : (
            <>
              No official dataset imported yet. Import an official government file
              below to power AI prioritisation and location intelligence.
            </>
          )}
        </p>
      </div>

      {/* Import dataset */}
      <div className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <UploadCloud className="h-4 w-4 text-royal" />
          <h3 className="font-display font-600 text-body">Import dataset</h3>
          <span className="ml-auto text-xs text-muted">Supported: CSV · XLS · XLSX</span>
        </div>

        {!staged ? (
          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`flex cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border border-dashed py-10 text-center transition ${
              dragOver ? "border-royal bg-royal-50" : "border-hairline bg-paper/50 hover:border-royal"
            }`}
          >
            {uploading ? (
              <Loader2 className="h-6 w-6 animate-spin text-royal" />
            ) : (
              <UploadCloud className="h-6 w-6 text-royal" />
            )}
            <span className="text-sm font-600 text-body">
              {uploading ? "Uploading…" : "Drag & drop a dataset file"}
            </span>
            <span className="text-xs text-muted">or click to browse — CSV, XLS, XLSX</span>
            <input
              type="file"
              accept=".csv,.xls,.xlsx"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </label>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-3 rounded-lg border border-hairline bg-paper/50 px-3 py-2">
              <div className="flex min-w-0 items-center gap-2">
                <FileText className="h-4 w-4 shrink-0 text-royal" />
                <span className="truncate text-sm font-600 text-body">{staged.file_name}</span>
              </div>
              <button
                onClick={cancelImport}
                className="rounded-lg p-1 text-muted transition hover:bg-paper hover:text-body"
                aria-label="Discard file"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="label">Dataset type (auto-detected)</label>
                <select className="input" value={type} onChange={(e) => onTypeChange(e.target.value)}>
                  {TYPE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Source department (optional)</label>
                <input
                  className="input"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Census India, ECI"
                />
              </div>
            </div>

            <div>
              <label className="label">Import mode</label>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setReplace(false)}
                  className={`chip ${!replace ? "bg-royal-50 text-royal" : "bg-paper text-muted"}`}
                >
                  Merge
                </button>
                <button
                  type="button"
                  onClick={() => setReplace(true)}
                  className={`chip ${replace ? "bg-royal-50 text-royal" : "bg-paper text-muted"}`}
                >
                  Replace
                </button>
                <span className="text-xs text-muted">
                  {replace
                    ? "Re-import and overwrite this file's previous rows."
                    : "Add without wiping existing data."}
                </span>
              </div>
            </div>

            {previewing ? (
              <div className="flex items-center gap-2 text-sm text-muted">
                <Loader2 className="h-4 w-4 animate-spin" /> Reading columns…
              </div>
            ) : preview ? (
              <div className="space-y-3">
                {preview.sheet_names?.length > 1 && (
                  <p className="text-xs text-muted">
                    Sheet <strong className="text-body">{preview.sheet}</strong> of{" "}
                    {preview.sheet_names.length}
                  </p>
                )}
                <div>
                  <p className="label">Detected fields</p>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.keys(preview.detected_fields || {}).length ? (
                      Object.entries(preview.detected_fields).map(([f, h]) => (
                        <span key={f} className="chip bg-success/10 text-success">
                          {f} ← {h}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-muted">
                        No standard fields detected — try a different type.
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="label">Preview (first 10 rows)</p>
                  <div className="overflow-x-auto rounded-lg border border-hairline">
                    <table className="min-w-full text-xs">
                      <thead className="bg-paper">
                        <tr>
                          {preview.columns.map((c, i) => (
                            <th key={i} className="whitespace-nowrap px-2.5 py-1.5 text-left font-600 text-muted">
                              {c}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.sample_rows.slice(0, 10).map((r, ri) => (
                          <tr key={ri} className="border-t border-hairline">
                            {preview.columns.map((_, ci) => (
                              <td key={ci} className="whitespace-nowrap px-2.5 py-1.5 text-body/80">
                                {String(r[ci] ?? "")}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : null}

            <div className="flex gap-2">
              <button onClick={doImport} disabled={importing || !preview} className="btn-primary">
                {importing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="h-4 w-4" />
                )}
                Import dataset
              </button>
              <button onClick={cancelImport} className="btn-ghost">Cancel</button>
            </div>
          </div>
        )}
      </div>

      {/* Dataset sources */}
      <div className="card p-5">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 font-display font-600 text-body">
            <Database className="h-4 w-4 text-royal" />
            Dataset sources
          </h3>
          {sources.length > 0 && (
            <span className="text-xs text-muted">
              {sources.length} dataset{sources.length > 1 ? "s" : ""}
              {lastImport && ` · last import ${lastImport}`}
            </span>
          )}
        </div>
        {sources.length === 0 ? (
          <p className="text-sm text-muted">
            No official datasets imported yet. Import a file above to see it here.
          </p>
        ) : (
          <div className="divide-y divide-hairline">
            {sources.map((s) => (
              <div key={s.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-500 text-body">{s.dataset_name || s.source_name}</p>
                    <span
                      className={`chip ${
                        s.is_official ? "bg-success/10 text-success" : "bg-saffron-100 text-saffron-600"
                      }`}
                    >
                      {s.is_official ? "Official" : "Unofficial"}
                    </span>
                  </div>
                  <p className="truncate text-xs text-muted">
                    {(s.source_department || TYPE_LABEL[s.source_type] || s.source_type)} · {s.file_name}
                    {s.imported_at &&
                      ` · ${new Date(s.imported_at).toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}`}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <span
                    className={`chip ${
                      s.import_status === "success"
                        ? "bg-success/10 text-success"
                        : s.import_status === "partial"
                        ? "bg-saffron-100 text-saffron-600"
                        : "bg-emergency/10 text-emergency"
                    }`}
                  >
                    {s.record_count.toLocaleString()} · {s.import_status}
                  </span>
                  <button
                    onClick={() => removeSource(s.id)}
                    className="rounded-lg p-1.5 text-muted transition hover:bg-emergency/5 hover:text-emergency"
                    aria-label="Delete dataset source"
                    title="Delete source + its records"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
