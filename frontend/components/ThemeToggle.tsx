"use client";

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("finflow-theme") as "dark" | "light" | null;
    if (saved) {
      setTheme(saved);
      if (saved === "light") {
        document.documentElement.classList.remove("dark");
      } else {
        document.documentElement.classList.add("dark");
      }
    } else {
      const isDark = document.documentElement.classList.contains("dark");
      setTheme(isDark ? "dark" : "light");
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("finflow-theme", nextTheme);
    if (nextTheme === "light") {
      document.documentElement.classList.remove("dark");
    } else {
      document.documentElement.classList.add("dark");
    }
  };

  if (!mounted) {
    return (
      <div className="w-16 h-8 rounded-full bg-slate-200 dark:bg-white/10 opacity-70" />
    );
  }

  return (
    <button
      onClick={toggleTheme}
      type="button"
      title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
      aria-label={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
      className="relative flex items-center p-1 w-16 h-8 rounded-full transition-all duration-300 bg-slate-200/90 hover:bg-slate-300 dark:bg-white/10 dark:hover:bg-white/20 border border-slate-300/80 dark:border-white/15 cursor-pointer shadow-sm"
    >
      <div
        className={`w-6 h-6 rounded-full bg-white dark:bg-indigo-600 shadow-md transform transition-transform duration-300 flex items-center justify-center ${
          theme === "light" ? "translate-x-0 text-amber-500" : "translate-x-8 text-white"
        }`}
      >
        {theme === "light" ? (
          <Sun className="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
        ) : (
          <Moon className="w-3.5 h-3.5 text-indigo-100" />
        )}
      </div>
      <span className="sr-only">Toggle theme</span>
    </button>
  );
}
