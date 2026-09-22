import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

export const AuthModalContext = createContext(null);

export function AuthModalProvider({ children }) {
  const [open, setOpen] = useState(false);
  const [redirectTo, setRedirectTo] = useState("/");
  const location = useLocation();

  const openLogin = useCallback((next = "/") => {
    setRedirectTo(next || "/");
    setOpen(true);
  }, []);

  const closeLogin = useCallback(() => {
    setOpen(false);
  }, []);

  useEffect(() => {
    if (location.pathname === "/registro") {
      setOpen(false);
    }
  }, [location.pathname]);

  const value = useMemo(
    () => ({
      open,
      redirectTo,
      openLogin,
      closeLogin,
    }),
    [open, redirectTo, openLogin, closeLogin],
  );

  return <AuthModalContext.Provider value={value}>{children}</AuthModalContext.Provider>;
}
