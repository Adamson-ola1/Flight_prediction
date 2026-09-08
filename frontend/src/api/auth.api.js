// This project's API is unauthenticated (a public prediction demo), so
// these are stubs kept for structural parity / future extension — wire
// them up to backend/main.py once auth is added there.

export async function login(_credentials) {
  throw new Error("Auth is not enabled on this backend yet.");
}

export async function logout() {
  return true;
}

export async function getCurrentUser() {
  return null;
}
