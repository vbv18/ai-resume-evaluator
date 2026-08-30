import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  Sparkles,
  FileText,
  Briefcase,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { motion } from "framer-motion";

export const EvaluationFlowPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const preselectedResumeVer = searchParams.get("resume_version_id");
  const preselectedJdVer = searchParams.get("job_description_version_id");

  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedResumeVerId, setSelectedResumeVerId] = useState<string>(preselectedResumeVer || "");

  const [selectedJdId, setSelectedJdId] = useState<string>("");
  const [selectedJdVerId, setSelectedJdVerId] = useState<string>(preselectedJdVer || "");

  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  // Queries
  const { data: resumesData } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.listResumes(),
  });

  const { data: jobsData } = useQuery({
    queryKey: ["job-descriptions"],
    queryFn: () => api.listJobDescriptions(),
  });

  const resumes = resumesData?.data || [];
  const jobs = jobsData?.data || [];

  const handleResumeSelect = (resumeId: string) => {
    setSelectedResumeId(resumeId);
    const r = resumes.find((item) => item.id === resumeId);
    if (r?.current_version_id) {
      setSelectedResumeVerId(r.current_version_id);
    }
  };

  const handleJdSelect = (jdId: string) => {
    setSelectedJdId(jdId);
    const j = jobs.find((item) => item.id === jdId);
    if (j?.current_version_id) {
      setSelectedJdVerId(j.current_version_id);
    }
  };

  // Mutation to enqueue run
  const enqueueMutation = useMutation({
    mutationFn: () =>
      api.enqueueEvaluation({
        resume_version_id: selectedResumeVerId,
        job_description_version_id: selectedJdVerId,
      }),
    onSuccess: (res) => {
      setActiveRunId(res.evaluation_id);
    },
  });

  // Status polling when run is queued or processing
  const { data: runStatus } = useQuery({
    queryKey: ["evaluation-status", activeRunId],
    queryFn: () => api.getEvaluationStatus(activeRunId!),
    enabled: !!activeRunId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "COMPLETED" || status === "FAILED") {
        return false;
      }
      return 1500;
    },
  });

  // Navigate when completed
  useEffect(() => {
    if (runStatus?.status === "COMPLETED") {
      const timer = setTimeout(() => {
        navigate(`/evaluations/${activeRunId}`);
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [runStatus, activeRunId, navigate]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="pb-6 border-b border-border/60 text-center sm:text-left">
        <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
          Run Multi-Criteria AI Evaluation
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Select a resume version and a target job posting to analyze ATS compatibility, keyword density, and skill alignment.
        </p>
      </div>

      {activeRunId ? (
        /* Live Processing View */
        <div className="p-8 bg-card rounded-xl border border-border/70 shadow-xs text-center space-y-6">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto">
            {runStatus?.status === "COMPLETED" ? (
              <CheckCircle2 className="w-8 h-8 text-emerald-500 animate-in zoom-in" />
            ) : runStatus?.status === "FAILED" ? (
              <AlertCircle className="w-8 h-8 text-destructive" />
            ) : (
              <Loader2 className="w-8 h-8 animate-spin" />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-semibold text-foreground">
              {runStatus?.status === "COMPLETED"
                ? "Evaluation Complete!"
                : runStatus?.status === "PROCESSING"
                ? "Analyzing Resume & Job Requirements..."
                : runStatus?.status === "FAILED"
                ? "Evaluation Failed"
                : "Queued for AI Evaluation..."}
            </h3>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto">
              {runStatus?.status === "COMPLETED"
                ? "Redirecting to your detailed score breakdown..."
                : "Generating deterministic sub-scores, ATS findings, and actionable recommendations."}
            </p>
          </div>

          {/* Animated Progress Bar */}
          <div className="max-w-md mx-auto bg-muted rounded-full h-2 overflow-hidden">
            <motion.div
              className="bg-primary h-full rounded-full"
              initial={{ width: "15%" }}
              animate={{
                width: `${runStatus?.progress_percentage || 25}%`,
              }}
              transition={{ duration: 0.5 }}
            />
          </div>

          {runStatus?.status === "FAILED" && (
            <div className="text-xs text-destructive bg-destructive/10 p-3 rounded-lg max-w-md mx-auto">
              {runStatus.error_message || "An unexpected error occurred during evaluation."}
            </div>
          )}
        </div>
      ) : (
        /* Configuration Step */
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Pick Resume */}
            <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
                <FileText className="w-4 h-4 text-primary" />
                <span>1. Select Resume</span>
              </div>

              {resumes.length === 0 ? (
                <div className="text-xs text-muted-foreground py-4">
                  No resumes found.{" "}
                  <Link to="/resumes" className="text-primary hover:underline font-medium">
                    Upload a resume first.
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  <label className="block text-xs text-muted-foreground">Candidate Resume</label>
                  <select
                    value={selectedResumeId}
                    onChange={(e) => handleResumeSelect(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="">Select a resume...</option>
                    {resumes.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.title} ({r.target_role || "General"})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Pick Job */}
            <div className="p-6 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
                <Briefcase className="w-4 h-4 text-emerald-500" />
                <span>2. Select Target Job</span>
              </div>

              {jobs.length === 0 ? (
                <div className="text-xs text-muted-foreground py-4">
                  No jobs found.{" "}
                  <Link to="/jobs" className="text-primary hover:underline font-medium">
                    Add a job description first.
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  <label className="block text-xs text-muted-foreground">Target Role</label>
                  <select
                    value={selectedJdId}
                    onChange={(e) => handleJdSelect(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="">Select a target job...</option>
                    {jobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.title} {j.company_name ? `(${j.company_name})` : ""}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Launch Action */}
          <div className="p-5 bg-muted/30 rounded-xl border border-border/60 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-muted-foreground">
              Evaluated with <span className="font-semibold text-foreground">openai/gpt-oss-20b</span> via Groq high-throughput engine.
            </div>

            <button
              type="button"
              disabled={
                !selectedResumeVerId || !selectedJdVerId || enqueueMutation.isPending
              }
              onClick={() => enqueueMutation.mutate()}
              className="w-full sm:w-auto px-6 py-2.5 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch AI Evaluation</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
