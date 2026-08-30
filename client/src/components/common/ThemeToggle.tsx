import React, { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";

export const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      type="button"
      aria-label="Toggle light and dark theme"
      className="relative flex items-center justify-between w-14 h-8 px-1 rounded-full bg-muted/80 hover:bg-muted border border-border/80 cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40"
    >
      <Sun className="w-3.5 h-3.5 ml-0.5 text-amber-500 transition-opacity" />
      <Moon className="w-3.5 h-3.5 mr-0.5 text-slate-400 dark:text-blue-400 transition-opacity" />
      <motion.div
        className="absolute top-1 left-1 w-6 h-6 rounded-full bg-card shadow-sm border border-border/40 flex items-center justify-center"
        layout
        transition={{ type: "spring", stiffness: 700, damping: 30 }}
        animate={{ x: isDark ? 24 : 0 }}
      >
        {isDark ? (
          <Moon className="w-3.5 h-3.5 text-blue-400" />
        ) : (
          <Sun className="w-3.5 h-3.5 text-amber-500" />
        )}
      </motion.div>
    </button>
  );
};
