import client from "./client";

// Submit as multipart so optional image/voice files can ride along.
export const submitComplaint = (fields, image, voice) => {
  const form = new FormData();
  Object.entries(fields).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== "") form.append(k, v);
  });
  if (image) form.append("image", image);
  if (voice) form.append("voice", voice);
  return client
    .post("/api/v1/complaints", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export const listComplaints = (params = {}) =>
  client.get("/api/v1/complaints", { params }).then((r) => r.data);

export const getComplaint = (id) =>
  client.get(`/api/v1/complaints/${id}`).then((r) => r.data);

export const trackComplaint = (code) =>
  client.get(`/api/v1/complaints/track/${code}`).then((r) => r.data);
