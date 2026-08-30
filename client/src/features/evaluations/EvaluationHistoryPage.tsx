import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  Sparkles,
  ArrowRight,
  Clock,
  Layers,
} from "lucide-react";
import { formatDate, getScoreColorClass } from "../../lib/utils";

export const EvaluationHistoryPage: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["evaluations"],
    queryFn: () => api.listEvaluations(),
  });

  const evaluations = data?.data || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            Evaluation Audit History
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse all historical evaluation runs, telemetry, and score breakdowns.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/compare"
            className="px-3.5 py-2 text-xs font-medium bg-card hover:bg-muted text-foreground border border-border/80 rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <Layers className="w-3.5 h-3.5 text-muted-foreground" />
            <span>Compare Versions</span>
          </Link>
          <Link
            to="/evaluate"
            className="px-3.5 py-2 text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Evaluation</span>
          </Link>
        </div>
      </div>

      {/* Runs Table */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-16 bg-card/60 rounded-xl border border-border/40 animate-pulse"
            />
          ))}
        </div>
      ) : evaluations.length === 0 ? (
        <div className="p-12 text-center bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground">
            <Clock className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-foreground">No Evaluation Runs Found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Run an AI evaluation to start tracking your resume fit scores over time.
          </p>
          <Link
            to="/evaluate"
            className="mt-2 px-3.5 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-lg inline-flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Evaluate Resume</span>
          </Link>
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border/70 shadow-xs overflow-hidden divide-y divide-border/50">
          {evaluations.map((run) => {
            const scoreConfig = getScoreColorClass(run.overall_score);

            return (
              <div
                key={run.id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div
                    className={`w-11 h-11 rounded-lg border flex flex-col items-center justify-center font-bold ${scoreConfig.badge}`}
                  >
                    <span className="text-sm">
                      {run.overall_score !== null && run.overall_score !== undefined
                        ? run.overall_score
                        : "--"}
                    </span>
                    <span className="text-[9px] uppercase tracking-wider opacity-75">/ 100</span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-foreground">
                        Run #{run.id.slice(0, 8)}
                      </span>
                      {run.verdict && (
                        <span className="text-[10px] px-2 py-0.2 rounded-full font-medium bg-muted text-muted-foreground">
                          {run.verdict}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-2">
                      <span>{formatDate(run.created_at)}</span>
                      <span>•</span>
                      <span>Model: {run.model_name}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 self-end sm:self-center">
                  <span
                    className={`text-[10px] px-2.5 py-0.5 rounded-full font-semibold ${
                      run.status === "COMPLETED"
                        ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                        : run.status === "PROCESSING" || run.status === "QUEUED"
                        ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                        : "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                    }`}
                  >
                    {run.status}
                  </span>

                  <Link
                    to={`/evaluations/${run.id}`}
                    className="px-3 py-1.5 text-xs font-medium bg-muted hover:bg-muted/80 text-foreground rounded-lg transition-colors flex items-center gap-1.5"
                  >
                    <span>View Breakdown</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
