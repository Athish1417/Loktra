import client from "./client";

export const officerQueue = () =>
  client.get("/api/v1/officer/complaints").then((r) => r.data);

export const verifyComplaint = (id) =>
  client.post(`/api/v1/officer/complaints/${id}/verify`).then((r) => r.data);

export const updateStatus = (id, status, note) =>
  client
    .post(`/api/v1/officer/complaints/${id}/status`, { status, note })
    .then((r) => r.data);
