import { createContext, useContext, useEffect, useMemo, useState } from "react";
import * as authApi from "../api/auth";

const AuthContext = createContext(null);

// Landing route per role after login.
export const HOME_BY_ROLE = {
  citizen: "/app/submit",
  officer: "/app/officer",
  mp: "/app/dashboard",
  super_admin: "/app/admin",
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("loktra_user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [ready, setReady] = useState(false);

  // Revalidate the stored token on boot so a stale session logs out cleanly.
  useEffect(() => {
    const token = localStorage.getItem("loktra_token");
    if (!token) {
      setReady(true);
      return;
    }
    authApi
      .me()
      .then((fresh) => {
        setUser(fresh);
        localStorage.setItem("loktra_user", JSON.stringify(fresh));
      })
      .catch(() => logout())
      .finally(() => setReady(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function persist(data) {
    localStorage.setItem("loktra_token", data.access_token);
    localStorage.setItem("loktra_user", JSON.stringify(data.user));
    setUser(data.user);
  }

  async function login(email, password, expectedRole) {
    const data = await authApi.login(email, password);
    // Enforce the selected role against the backend (source of truth). On a
    // mismatch we throw WITHOUT persisting, so no session is ever established.
    if (expectedRole && data.user.role !== expectedRole) {
      const err = new Error("ROLE_MISMATCH");
      err.code = "ROLE_MISMATCH";
      err.actualRole = data.user.role;
      throw err;
    }
    persist(data);
    return data.user;
  }

  async function register(payload) {
    const data = await authApi.register(payload);
    persist(data);
    return data.user;
  }

  function logout() {
    localStorage.removeItem("loktra_token");
    localStorage.removeItem("loktra_user");
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, ready, login, register, logout, role: user?.role }),
    [user, ready]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
