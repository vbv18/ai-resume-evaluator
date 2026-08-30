import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  Briefcase,
  Plus,
  Trash2,
  Calendar,
  Building2,
  ArrowRight,
  Sparkles,
  Link as LinkIcon,
  Type,
  X,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const JobListPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"TEXT" | "URL">("TEXT");

  // Form states
  const [title, setTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [rawText, setRawText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["job-descriptions"],
    queryFn: () => api.listJobDescriptions(),
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      return api.createJobDescription({
        title: title || "Target Role",
        company_name: companyName || undefined,
        input_source: activeTab === "TEXT" ? "DIRECT_TEXT" : "URL_IMPORT",
        raw_text: activeTab === "TEXT" ? rawText : undefined,
        source_url: activeTab === "URL" ? sourceUrl : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job-descriptions"] });
      setIsModalOpen(false);
      resetForm();
    },
  });

  const archiveMutation = useMutation({
    mutationFn: (id: string) => api.archiveJobDescription(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job-descriptions"] });
    },
  });

  const resetForm = () => {
    setTitle("");
    setCompanyName("");
    setRawText("");
    setSourceUrl("");
  };

  const jobs = data?.data || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            Target Job Catalog
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Store and organize target job listings. AI extracts structured requirements for evaluation matching.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-xs transition-colors flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Job Description</span>
        </button>
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-44 bg-card/60 rounded-xl border border-border/40 animate-pulse"
            />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-12 text-center bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground">
            <Briefcase className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-foreground">No Job Descriptions Saved</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Add a target role or paste a job posting to extract requirements and match your resume against it.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="mt-2 px-3.5 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-lg inline-flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Job Description</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-card rounded-xl border border-border/70 shadow-xs hover:border-border transition-all flex flex-col justify-between p-5 group"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                    <Briefcase className="w-4 h-4" />
                  </div>
                  <button
                    onClick={() => {
                      if (confirm("Are you sure you want to remove this job description?")) {
                        archiveMutation.mutate(job.id);
                      }
                    }}
                    className="text-muted-foreground hover:text-destructive transition-colors p-1"
                    title="Archive job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1">
                    {job.title}
                  </h3>
                  <div className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1.5">
                    <Building2 className="w-3 h-3 text-muted-foreground" />
                    <span>{job.company_name || "Unspecified Company"}</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-border/50 flex items-center justify-between text-[11px] text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{formatDate(job.created_at).split(",")[0]}</span>
                </span>

                <div className="flex items-center gap-3">
                  <Link
                    to={`/evaluate?job_description_version_id=${job.current_version_id}`}
                    className="text-primary font-medium hover:underline flex items-center gap-1"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>Evaluate</span>
                  </Link>
                  <Link
                    to={`/jobs/${job.id}`}
                    className="text-muted-foreground hover:text-foreground flex items-center gap-1"
                  >
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Job Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-xl border border-border shadow-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-5 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground">Add Target Job Description</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Role Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. Senior Fullstack Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Company Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Stripe, OpenAI, Acme Corp"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              {/* Source tabs */}
              <div>
                <label className="block text-xs font-medium text-foreground mb-1.5">
                  Input Source
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveTab("TEXT")}
                    className={`py-2 text-xs rounded-lg border font-medium flex items-center justify-center gap-1.5 transition-colors ${
                      activeTab === "TEXT"
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-muted/40 border-border text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    <Type className="w-3.5 h-3.5" />
                    <span>Paste Posting Text</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveTab("URL")}
                    className={`py-2 text-xs rounded-lg border font-medium flex items-center justify-center gap-1.5 transition-colors ${
                      activeTab === "URL"
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-muted/40 border-border text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    <LinkIcon className="w-3.5 h-3.5" />
                    <span>Job URL</span>
                  </button>
                </div>
              </div>

              {activeTab === "TEXT" ? (
                <div>
                  <textarea
                    rows={7}
                    placeholder="Paste job requirements, responsibilities, and qualifications..."
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                  />
                </div>
              ) : (
                <div>
                  <input
                    type="url"
                    placeholder="https://jobs.lever.co/company/job-id"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border bg-muted/20 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-3.5 py-1.5 text-xs text-muted-foreground hover:text-foreground font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={
                  createMutation.isPending ||
                  (activeTab === "TEXT" && !rawText.trim()) ||
                  (activeTab === "URL" && !sourceUrl.trim())
                }
                onClick={() => createMutation.mutate()}
                className="px-4 py-2 text-xs bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {createMutation.isPending ? "Extracting Requirements..." : "Save Job"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
