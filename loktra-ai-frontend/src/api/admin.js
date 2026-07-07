import client from "./client";

export const listUsers = () =>
  client.get("/api/v1/admin/users").then((r) => r.data);

export const createUser = (payload) =>
  client.post("/api/v1/admin/users", payload).then((r) => r.data);

export const listDatasets = () =>
  client.get("/api/v1/datasets").then((r) => r.data);

export const datasetSource = () =>
  client.get("/api/v1/datasets/source").then((r) => r.data);

export const datasetSources = () =>
  client.get("/api/v1/datasets/sources").then((r) => r.data);

export const deleteDatasetSource = (id) =>
  client.delete(`/api/v1/datasets/sources/${id}`).then((r) => r.data);

export const uploadDataset = (file) => {
  const form = new FormData();
  form.append("file", file);
  return client
    .post("/api/v1/datasets/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export const previewDataset = (path, source_type) =>
  client
    .post("/api/v1/datasets/preview", { path, source_type })
    .then((r) => r.data);

export const importDatasetFile = (payload) =>
  client.post("/api/v1/datasets/import-file", payload).then((r) => r.data);

export const upsertDataset = (constituencyId, payload) =>
  client.put(`/api/v1/datasets/${constituencyId}`, payload).then((r) => r.data);
