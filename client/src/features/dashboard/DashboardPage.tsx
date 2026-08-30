import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  FileText,
  Briefcase,
  Sparkles,
  TrendingUp,
  ArrowRight,
  Clock,
} from "lucide-react";
import { formatDate, getScoreColorClass } from "../../lib/utils";

export const DashboardPage: React.FC = () => {
  const { data: resumesData, isLoading: resumesLoading } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.listResumes(),
  });

  const { data: jobsData, isLoading: jobsLoading } = useQuery({
    queryKey: ["job-descriptions"],
    queryFn: () => api.listJobDescriptions(),
  });

  const { data: evalsData, isLoading: evalsLoading } = useQuery({
    queryKey: ["evaluations"],
    queryFn: () => api.listEvaluations(),
  });

  const resumes = resumesData?.data || [];
  const jobs = jobsData?.data || [];
  const evaluations = evalsData?.data || [];

  const completedEvals = evaluations.filter((e) => e.status === "COMPLETED" && e.overall_score != null);
  const avgScore =
    completedEvals.length > 0
      ? Math.round(
          completedEvals.reduce((acc, curr) => acc + (curr.overall_score || 0), 0) /
            completedEvals.length
        )
      : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            Evaluation Dashboard
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Track resume scores, optimize for applicant tracking systems, and close skill gaps.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/resumes"
            className="px-3.5 py-2 text-xs font-medium bg-card hover:bg-muted text-foreground border border-border/80 rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <FileText className="w-3.5 h-3.5 text-muted-foreground" />
            <span>Upload Resume</span>
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

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Active Resumes</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-500 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold font-heading text-foreground">
            {resumesLoading ? "--" : resumes.length}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Snapshots & version histories
          </div>
        </div>

        <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Target Jobs</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold font-heading text-foreground">
            {jobsLoading ? "--" : jobs.length}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Saved job descriptions catalog
          </div>
        </div>

        <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">AI Evaluations</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-500 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold font-heading text-foreground">
            {evalsLoading ? "--" : evaluations.length}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Immutable evaluation runs
          </div>
        </div>

        <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Average Match</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold font-heading text-foreground">
            {avgScore !== null ? `${avgScore}%` : "--"}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Across all completed evaluations
          </div>
        </div>
      </div>

      {/* Main Grid: Quick Actions & Recent Evaluations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Recent Evaluations */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span>Recent Evaluations</span>
            </h2>
            <Link
              to="/history"
              className="text-xs text-primary hover:underline flex items-center gap-1 font-medium"
            >
              <span>View all</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="bg-card rounded-xl border border-border/70 shadow-xs overflow-hidden">
            {evaluations.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <p className="text-xs">No evaluation runs recorded yet.</p>
                <Link
                  to="/evaluate"
                  className="mt-3 inline-flex items-center gap-1.5 text-xs text-primary font-medium hover:underline"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Start your first evaluation</span>
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-border/50">
                {evaluations.slice(0, 5).map((run) => {
                  const scoreConfig = getScoreColorClass(run.overall_score);

                  return (
                    <Link
                      key={run.id}
                      to={`/evaluations/${run.id}`}
                      className="p-4 flex items-center justify-between hover:bg-muted/40 transition-colors group"
                    >
                      <div className="flex items-center space-x-3.5">
                        <div
                          className={`w-9 h-9 rounded-lg border flex items-center justify-center font-bold text-xs ${scoreConfig.badge}`}
                        >
                          {run.overall_score !== null && run.overall_score !== undefined
                            ? run.overall_score
                            : "--"}
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors flex items-center gap-2">
                            <span>Evaluation #{run.id.slice(0, 8)}</span>
                            {run.verdict && (
                              <span className="text-[10px] px-1.5 py-0.2 rounded font-normal bg-muted text-muted-foreground">
                                {run.verdict}
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-muted-foreground mt-0.5">
                            {formatDate(run.created_at)} • {run.model_name}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            run.status === "COMPLETED"
                              ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                              : run.status === "PROCESSING" || run.status === "QUEUED"
                              ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                              : "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                          }`}
                        >
                          {run.status}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Quick Tips & Setup */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold tracking-tight text-foreground">
            Optimization Workflow
          </h2>
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-4 text-xs">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                1
              </div>
              <div>
                <div className="font-semibold text-foreground">Upload or Paste Resume</div>
                <div className="text-muted-foreground text-[11px] mt-0.5">
                  Parsed into structured sections (skills, experience, contact).
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                2
              </div>
              <div>
                <div className="font-semibold text-foreground">Add Target Job</div>
                <div className="text-muted-foreground text-[11px] mt-0.5">
                  AI extracts core requirements, keywords, and qualifications.
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                3
              </div>
              <div>
                <div className="font-semibold text-foreground">Evaluate & Compare</div>
                <div className="text-muted-foreground text-[11px] mt-0.5">
                  Get deterministic weighted scores, actionable remedies, and version-by-version diffs.
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-border/50">
              <Link
                to="/evaluate"
                className="w-full py-2 bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-lg text-center flex items-center justify-center gap-1.5 transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Launch New Evaluation</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
