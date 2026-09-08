import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // No real authentication in this project (public prediction demo) —
  // this context is kept so the folder structure and future auth wiring
  // (backend/main.py) have a place to plug into.
  const [user] = useState(null);

  const value = useMemo(() => ({ user, isAuthenticated: false }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
