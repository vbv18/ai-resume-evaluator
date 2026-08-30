import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return "N/A";
  const date = new Date(isoString);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return "--";
  return `${Math.round(score)}`;
}

export function getScoreColorClass(score: number | null | undefined): {
  badge: string;
  bar: string;
  text: string;
} {
  if (score === null || score === undefined) {
    return {
      badge: "bg-muted text-muted-foreground",
      bar: "bg-muted",
      text: "text-muted-foreground",
    };
  }
  if (score >= 85) {
    return {
      badge: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
      bar: "bg-emerald-500",
      text: "text-emerald-600 dark:text-emerald-400",
    };
  }
  if (score >= 70) {
    return {
      badge: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
      bar: "bg-blue-500",
      text: "text-blue-600 dark:text-blue-400",
    };
  }
  if (score >= 50) {
    return {
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      bar: "bg-amber-500",
      text: "text-amber-600 dark:text-amber-400",
    };
  }
  return {
    badge: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
    bar: "bg-rose-500",
    text: "text-rose-600 dark:text-rose-400",
  };
}
