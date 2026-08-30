import React, { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { getScoreColorClass } from "../../lib/utils";

interface ScoreCardProps {
  score?: number | null;
  label?: string;
  verdict?: string | null;
  size?: "sm" | "md" | "lg";
  subScores?: {
    ats?: number | null;
    jobMatch?: number | null;
    skills?: number | null;
    experience?: number | null;
  };
}

export const ScoreCard: React.FC<ScoreCardProps> = ({
  score = 0,
  label = "Overall Match",
  verdict,
  size = "md",
  subScores,
}) => {
  const targetScore = score ?? 0;
  const spring = useSpring(0, { stiffness: 60, damping: 20 });
  const displayScore = useTransform(spring, (current) => Math.round(current));
  const [currentDisplay, setCurrentDisplay] = useState(0);

  useEffect(() => {
    spring.set(targetScore);
    const unsubscribe = displayScore.on("change", (latest) => {
      setCurrentDisplay(latest);
    });
    return () => unsubscribe();
  }, [targetScore, spring, displayScore]);

  const colorConfig = getScoreColorClass(targetScore);

  const radius = size === "lg" ? 54 : size === "md" ? 42 : 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (circumference * targetScore) / 100;

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-card rounded-xl border border-border/70 shadow-xs relative overflow-hidden">
      <div className="relative flex items-center justify-center">
        <svg
          className={size === "lg" ? "w-36 h-36" : size === "md" ? "w-28 h-28" : "w-20 h-20"}
          viewBox="0 0 120 120"
        >
          {/* Background track */}
          <circle
            cx="60"
            cy="60"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted/40 fill-none"
          />
          {/* Animated fill */}
          <motion.circle
            cx="60"
            cy="60"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            strokeLinecap="round"
            className={colorConfig.text + " fill-none -rotate-90 origin-center"}
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center">
          <span
            className={`font-heading font-bold tracking-tight text-foreground ${
              size === "lg" ? "text-4xl" : size === "md" ? "text-3xl" : "text-xl"
            }`}
          >
            {currentDisplay}
          </span>
          <span className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">
            / 100
          </span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <div className="text-xs font-semibold text-foreground">{label}</div>
        {verdict && (
          <span
            className={`inline-block mt-1 px-2.5 py-0.5 text-[11px] font-medium rounded-full border ${colorConfig.badge}`}
          >
            {verdict}
          </span>
        )}
      </div>

      {subScores && (
        <div className="w-full mt-6 pt-4 border-t border-border/50 grid grid-cols-2 gap-3 text-left">
          {subScores.ats !== undefined && (
            <div>
              <div className="text-[11px] text-muted-foreground flex justify-between">
                <span>ATS Quality</span>
                <span className="font-medium text-foreground">{subScores.ats}%</span>
              </div>
              <div className="w-full bg-muted/60 rounded-full h-1.5 mt-1 overflow-hidden">
                <motion.div
                  className={`h-full ${getScoreColorClass(subScores.ats).bar}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${subScores.ats}%` }}
                  transition={{ duration: 1, delay: 0.2 }}
                />
              </div>
            </div>
          )}

          {subScores.jobMatch !== undefined && (
            <div>
              <div className="text-[11px] text-muted-foreground flex justify-between">
                <span>JD Match</span>
                <span className="font-medium text-foreground">{subScores.jobMatch}%</span>
              </div>
              <div className="w-full bg-muted/60 rounded-full h-1.5 mt-1 overflow-hidden">
                <motion.div
                  className={`h-full ${getScoreColorClass(subScores.jobMatch).bar}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${subScores.jobMatch}%` }}
                  transition={{ duration: 1, delay: 0.3 }}
                />
              </div>
            </div>
          )}

          {subScores.skills !== undefined && (
            <div>
              <div className="text-[11px] text-muted-foreground flex justify-between">
                <span>Hard Skills</span>
                <span className="font-medium text-foreground">{subScores.skills}%</span>
              </div>
              <div className="w-full bg-muted/60 rounded-full h-1.5 mt-1 overflow-hidden">
                <motion.div
                  className={`h-full ${getScoreColorClass(subScores.skills).bar}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${subScores.skills}%` }}
                  transition={{ duration: 1, delay: 0.4 }}
                />
              </div>
            </div>
          )}

          {subScores.experience !== undefined && (
            <div>
              <div className="text-[11px] text-muted-foreground flex justify-between">
                <span>Experience</span>
                <span className="font-medium text-foreground">{subScores.experience}%</span>
              </div>
              <div className="w-full bg-muted/60 rounded-full h-1.5 mt-1 overflow-hidden">
                <motion.div
                  className={`h-full ${getScoreColorClass(subScores.experience).bar}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${subScores.experience}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
