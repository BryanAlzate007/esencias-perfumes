import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { getAuth, logout as allauthLogout } from "../lib/allauth";
import { ensureCsrfCookie, getMe } from "../services/auth";

export const AuthContext = createContext(null);

async function loadProfile(authMessage) {
  if (authMessage?.meta?.is_authenticated) {
    return getMe();
  }
  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  const refreshUser = useCallback(async () => {
    const auth = await getAuth();
    const me = await loadProfile(auth);
    setUser(me);
    return me;
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      await ensureCsrfCookie();
      const auth = await getAuth();
      if (!cancelled) {
        setUser(await loadProfile(auth));
        setReady(true);
      }
    }

    function onAuthChanged(event) {
      loadProfile(event.detail)
        .then((me) => {
          if (!cancelled) {
            setUser(me);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setUser(null);
          }
        });
    }

    document.addEventListener("allauth.auth.change", onAuthChanged);
    boot().catch(() => {
      if (!cancelled) {
        setUser(null);
        setReady(true);
      }
    });

    return () => {
      cancelled = true;
      document.removeEventListener("allauth.auth.change", onAuthChanged);
    };
  }, []);

  const logout = useCallback(async () => {
    await allauthLogout();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      ready,
      isAuthenticated: Boolean(user),
      isAdmin: Boolean(user?.is_admin || user?.role === "admin"),
      refreshUser,
      setUser,
      logout,
    }),
    [user, ready, refreshUser, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
