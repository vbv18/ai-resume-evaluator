import React, { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const EvaluationComparePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const runAParam = searchParams.get("run_a") || "";
  const runBParam = searchParams.get("run_b") || "";

  const [runAId, setRunAId] = useState(runAParam);
  const [runBId, setRunBId] = useState(runBParam);

  const { data: evalsData } = useQuery({
    queryKey: ["evaluations"],
    queryFn: () => api.listEvaluations(),
  });

  const evaluations = (evalsData?.data || []).filter((e) => e.status === "COMPLETED");

  const { data: diff } = useQuery({
    queryKey: ["evaluation-compare", runAId, runBId],
    queryFn: () => api.compareEvaluations(runAId, runBId),
    enabled: !!runAId && !!runBId && runAId !== runBId,
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <Link
            to="/history"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-medium mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to History</span>
          </Link>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            Evaluation Version Comparison
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Compare score trajectories, newly matched skills, and delta improvements between two evaluation runs.
          </p>
        </div>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-card rounded-xl border border-border/70 shadow-xs">
        <div>
          <label className="block text-xs font-semibold text-foreground mb-1.5">
            Baseline Run (e.g. Version 1)
          </label>
          <select
            value={runAId}
            onChange={(e) => setRunAId(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">Select baseline evaluation...</option>
            {evaluations.map((e) => (
              <option key={e.id} value={e.id}>
                #{e.id.slice(0, 8)} — Score: {e.overall_score || 0}% ({formatDate(e.created_at)})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-foreground mb-1.5">
            Target Run (e.g. Version 2)
          </label>
          <select
            value={runBId}
            onChange={(e) => setRunBId(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">Select target evaluation...</option>
            {evaluations.map((e) => (
              <option key={e.id} value={e.id}>
                #{e.id.slice(0, 8)} — Score: {e.overall_score || 0}% ({formatDate(e.created_at)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Results */}
      {diff ? (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* Overall Delta Banner */}
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Overall Improvement Trajectory
              </span>
              <div className="flex items-center gap-4 mt-2">
                <div className="text-3xl font-bold font-heading text-foreground">
                  {diff.run_a.overall_score}% → {diff.run_b.overall_score}%
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 border ${
                    diff.overall_delta >= 0
                      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                      : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
                  }`}
                >
                  {diff.overall_delta >= 0 ? (
                    <ArrowUpRight className="w-4 h-4" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4" />
                  )}
                  <span>
                    {diff.overall_delta >= 0 ? `+${diff.overall_delta}` : diff.overall_delta}% Overall Delta
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div>
                <span className="block font-semibold text-foreground">
                  Run A: #{diff.run_a.id.slice(0, 8)}
                </span>
                <span>{formatDate(diff.run_a.created_at)}</span>
              </div>
              <span>vs</span>
              <div>
                <span className="block font-semibold text-foreground">
                  Run B: #{diff.run_b.id.slice(0, 8)}
                </span>
                <span>{formatDate(diff.run_b.created_at)}</span>
              </div>
            </div>
          </div>

          {/* Sub-scores Table */}
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Component Score Diffs
            </h3>
            <div className="divide-y divide-border/50">
              {diff.score_diffs.map((item, idx) => (
                <div key={idx} className="py-3 flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">{item.category}</span>
                  <div className="flex items-center gap-6">
                    <span className="text-muted-foreground">{item.score_a}%</span>
                    <span className="text-muted-foreground">→</span>
                    <span className="font-semibold text-foreground">{item.score_b}%</span>
                    <span
                      className={`w-16 text-right font-bold ${
                        item.delta > 0
                          ? "text-emerald-500"
                          : item.delta < 0
                          ? "text-rose-500"
                          : "text-muted-foreground"
                      }`}
                    >
                      {item.delta > 0 ? `+${item.delta}%` : `${item.delta}%`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Newly Matched Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Newly Matched Skills in Run B ({diff.newly_matched_skills.length})</span>
              </h3>
              {diff.newly_matched_skills.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {diff.newly_matched_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-md font-medium border border-emerald-500/20"
                    >
                      +{skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">No new skill matches detected.</p>
              )}
            </div>

            <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span>Still Missing Gaps ({diff.still_missing_skills.length})</span>
              </h3>
              {diff.still_missing_skills.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {diff.still_missing_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 text-xs bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-md font-medium border border-amber-500/20"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">All required skills matched!</p>
              )}
            </div>
          </div>
        </div>
      ) : runAId && runBId && runAId === runBId ? (
        <div className="p-8 text-center text-xs text-muted-foreground">
          Please select two different evaluation runs to compare.
        </div>
      ) : (
        <div className="p-12 text-center bg-card rounded-xl border border-border/70 shadow-xs text-muted-foreground text-xs">
          Select both runs above to compute score trajectories and skill coverage diffs.
        </div>
      )}
    </div>
  );
};
