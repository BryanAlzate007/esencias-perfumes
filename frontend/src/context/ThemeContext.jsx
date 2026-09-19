import { createContext, useEffect, useMemo, useState } from "react";

export const ThemeContext = createContext(null);

function systemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => (typeof window === "undefined" ? "light" : systemTheme()));

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const next = media.matches ? "dark" : "light";
      setTheme(next);
      document.documentElement.setAttribute("data-bs-theme", next);
    };
    apply();
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, []);

  const value = useMemo(() => ({ theme }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
