import client from "./client";

export const getDashboard = () =>
  client.get("/api/v1/mp/dashboard").then((r) => r.data);

export const mpComplaints = () =>
  client.get("/api/v1/mp/complaints").then((r) => r.data);

export const assignOfficer = (complaintId, officerId) =>
  client
    .post(`/api/v1/mp/complaints/${complaintId}/assign`, { officer_id: officerId })
    .then((r) => r.data);

export const mpOfficers = () =>
  client.get("/api/v1/mp/officers").then((r) => r.data);
