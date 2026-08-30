import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { ScoreCard } from "../../components/common/ScoreCard";
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  Sparkles,
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  Layers,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const EvaluationResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<"skills" | "ats" | "strengths" | "recommendations">("skills");

  const { data: run, isLoading } = useQuery({
    queryKey: ["evaluation", id],
    queryFn: () => api.getEvaluation(id!),
    enabled: !!id,
  });

  if (isLoading || !run) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-muted-foreground">
        Loading evaluation results...
      </div>
    );
  }

  const result = run.result;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <Link
            to="/history"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-medium mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Evaluations History</span>
          </Link>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground flex items-center gap-2.5">
            <span>Evaluation #{run.id.slice(0, 8)}</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-muted text-muted-foreground">
              {run.model_name}
            </span>
          </h1>
          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
            <span>Completed {formatDate(run.completed_at)}</span>
            <span>•</span>
            <span>Duration: {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : "1.2s"}</span>
            <span>•</span>
            <span>Tokens: {run.total_tokens || 0}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to={`/compare?run_a=${run.id}`}
            className="px-3.5 py-2 text-xs font-medium bg-card hover:bg-muted text-foreground border border-border/80 rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <Layers className="w-3.5 h-3.5 text-muted-foreground" />
            <span>Compare Version</span>
          </Link>
        </div>
      </div>

      {/* Hero Score Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ScoreCard
          score={run.overall_score}
          label="Overall Match Score"
          verdict={run.verdict}
          size="lg"
          subScores={{
            ats: run.ats_score,
            jobMatch: run.job_match_score,
            skills: run.skills_match_score,
            experience: run.experience_match_score,
          }}
        />

        <div className="lg:col-span-2 p-6 bg-card rounded-xl border border-border/70 shadow-xs flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-primary" />
              <span>Executive AI Summary</span>
            </div>
            <p className="mt-3 text-xs sm:text-sm text-muted-foreground leading-relaxed">
              {result?.executive_summary || "Evaluation completed successfully."}
            </p>
          </div>

          <div className="pt-4 border-t border-border/50 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-muted-foreground text-[11px]">Matched Skills</span>
              <div className="text-sm font-bold text-emerald-500">
                {result?.matched_skills.length || 0} skills
              </div>
            </div>
            <div>
              <span className="text-muted-foreground text-[11px]">Missing Gaps</span>
              <div className="text-sm font-bold text-rose-500">
                {result?.missing_skills.length || 0} skills
              </div>
            </div>
            <div>
              <span className="text-muted-foreground text-[11px]">Action Items</span>
              <div className="text-sm font-bold text-primary">
                {result?.recommendations.length || 0} fixes
              </div>
            </div>
            <div>
              <span className="text-muted-foreground text-[11px]">Formula</span>
              <div className="text-[11px] font-medium text-foreground">
                25% ATS + 30% JD + 25% Skills + 20% Exp
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-border/60 flex items-center gap-2">
        <button
          onClick={() => setActiveTab("skills")}
          className={`px-4 py-2.5 text-xs font-medium border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "skills"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Skills Analysis ({result?.matched_skills.length || 0} / {result?.missing_skills.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab("ats")}
          className={`px-4 py-2.5 text-xs font-medium border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "ats"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <FileCheck2 className="w-3.5 h-3.5" />
          <span>ATS & Keywords</span>
        </button>

        <button
          onClick={() => setActiveTab("strengths")}
          className={`px-4 py-2.5 text-xs font-medium border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "strengths"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ThumbsUp className="w-3.5 h-3.5" />
          <span>Strengths & Gaps</span>
        </button>

        <button
          onClick={() => setActiveTab("recommendations")}
          className={`px-4 py-2.5 text-xs font-medium border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "recommendations"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          <span>Recommendations ({result?.recommendations.length || 0})</span>
        </button>
      </div>

      {/* Tab 1: Skills Analysis */}
      {activeTab === "skills" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Matched Skills */}
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Matched Skills ({result?.matched_skills.length || 0})</span>
            </h3>

            <div className="space-y-3">
              {result?.matched_skills.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-muted/30 rounded-lg border border-border/40 space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-foreground">{item.skill}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-medium">
                      {item.importance}
                    </span>
                  </div>
                  {item.context_in_resume && (
                    <p className="text-[11px] text-muted-foreground italic">
                      "{item.context_in_resume}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Missing Skills */}
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <span>Missing Skill Gaps ({result?.missing_skills.length || 0})</span>
            </h3>

            <div className="space-y-3">
              {result?.missing_skills.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-muted/30 rounded-lg border border-border/40 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-foreground">{item.skill}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-medium">
                      {item.importance}
                    </span>
                  </div>
                  {item.remedy && (
                    <p className="text-[11px] text-muted-foreground flex items-start gap-1.5">
                      <Lightbulb className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                      <span>{item.remedy}</span>
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: ATS & Keywords */}
      {activeTab === "ats" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <FileCheck2 className="w-4 h-4 text-primary" />
              <span>ATS Formatting & Parseability</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <span className="text-muted-foreground">Parseability Quality:</span>
                <span className="font-bold text-foreground">
                  {result?.ats_findings?.parseability_rating || "Standard"}
                </span>
              </div>

              {result?.ats_findings?.formatting_issues?.length ? (
                <div>
                  <span className="font-semibold text-foreground block mb-1.5">
                    Formatting Issues Found:
                  </span>
                  <ul className="space-y-1 text-muted-foreground list-disc list-inside">
                    {result.ats_findings.formatting_issues.map((iss, i) => (
                      <li key={i}>{iss}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="text-emerald-500 flex items-center gap-1.5 font-medium">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>No major ATS formatting roadblocks detected!</span>
                </div>
              )}
            </div>
          </div>

          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span>Keyword Density & Coverage</span>
            </h3>

            <div className="space-y-3">
              {result?.keyword_analysis?.density_rating && (
                <div className="text-xs text-muted-foreground">
                  Coverage Rating:{" "}
                  <span className="font-semibold text-foreground">
                    {result.keyword_analysis.density_rating}
                  </span>
                </div>
              )}

              <div>
                <span className="text-xs font-semibold text-foreground block mb-1.5">
                  Matched Keywords:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result?.keyword_analysis?.matched_keywords?.map((kw, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-md"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-foreground block mb-1.5">
                  Recommended Missing Keywords:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result?.keyword_analysis?.missing_keywords?.map((kw, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 text-xs bg-rose-500/10 text-rose-600 dark:text-rose-400 rounded-md"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Strengths & Weaknesses */}
      {activeTab === "strengths" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <ThumbsUp className="w-4 h-4 text-emerald-500" />
              <span>Key Strengths</span>
            </h3>
            <ul className="space-y-2.5 text-xs text-muted-foreground">
              {result?.strengths.map((str, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{str}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-2">
              <ThumbsDown className="w-4 h-4 text-amber-500" />
              <span>Areas for Improvement</span>
            </h3>
            <ul className="space-y-2.5 text-xs text-muted-foreground">
              {result?.weaknesses.map((weak, i) => (
                <li key={i} className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{weak}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Tab 4: Actionable Recommendations */}
      {activeTab === "recommendations" && (
        <div className="space-y-4">
          {result?.recommendations.map((rec, idx) => {
            const isHigh = rec.priority === "HIGH";
            const isMed = rec.priority === "MEDIUM";

            return (
              <div
                key={idx}
                className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-foreground">
                    {rec.category}: {rec.issue}
                  </span>
                  <span
                    className={`text-[10px] px-2.5 py-0.5 rounded-full font-semibold border ${
                      isHigh
                        ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
                        : isMed
                        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
                        : "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20"
                    }`}
                  >
                    {rec.priority} Priority
                  </span>
                </div>

                <div className="text-xs text-muted-foreground flex items-start gap-2">
                  <span className="font-semibold text-foreground shrink-0">Action:</span>
                  <span>{rec.action}</span>
                </div>

                {rec.example && (
                  <div className="p-3 bg-muted/40 rounded-lg border border-border/50 text-xs font-mono">
                    <span className="text-[10px] font-sans uppercase font-bold text-muted-foreground block mb-1">
                      Example Bullet Point Rewrite:
                    </span>
                    <span className="text-foreground">{rec.example}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
