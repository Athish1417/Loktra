import client from "./client";

export const login = (email, password) =>
  client.post("/api/v1/auth/login", { email, password }).then((r) => r.data);

export const register = (payload) =>
  client.post("/api/v1/auth/register", payload).then((r) => r.data);

export const me = () => client.get("/api/v1/auth/me").then((r) => r.data);

export const forgotPassword = (email) =>
  client.post("/api/v1/auth/forgot-password", { email }).then((r) => r.data);
