import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  FileText,
  Plus,
  Upload,
  Link as LinkIcon,
  Type,
  ArrowRight,
  Trash2,
  Calendar,
  Layers,
  X,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const ResumeListPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"FILE" | "TEXT" | "URL">("FILE");

  // Form states
  const [title, setTitle] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [rawText, setRawText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.listResumes(),
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      if (activeTab === "FILE" && selectedFile) {
        return api.uploadResumeFile(selectedFile, title || "My Resume", targetRole);
      }
      return api.createResume({
        title: title || "My Resume",
        target_role: targetRole || undefined,
        input_source: activeTab === "TEXT" ? "DIRECT_TEXT" : "URL_IMPORT",
        raw_text: activeTab === "TEXT" ? rawText : undefined,
        source_url: activeTab === "URL" ? sourceUrl : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      setIsModalOpen(false);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  const resetForm = () => {
    setTitle("");
    setTargetRole("");
    setRawText("");
    setSourceUrl("");
    setSelectedFile(null);
  };

  const resumes = data?.data || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            Resume Catalog
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your resumes and snapshots. Each change generates a new immutable version.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-xs transition-colors flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Upload New Resume</span>
        </button>
      </div>

      {/* Resume Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-44 bg-card/60 rounded-xl border border-border/40 animate-pulse"
            />
          ))}
        </div>
      ) : resumes.length === 0 ? (
        <div className="p-12 text-center bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-foreground">No Resumes Found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Upload your existing PDF/DOCX resume or paste direct text to extract structured sections.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="mt-2 px-3.5 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-lg inline-flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Upload Resume</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((resume) => (
            <div
              key={resume.id}
              className="bg-card rounded-xl border border-border/70 shadow-xs hover:border-border transition-all flex flex-col justify-between p-5 group"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="w-9 h-9 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                    <FileText className="w-4 h-4" />
                  </div>
                  <button
                    onClick={() => {
                      if (confirm("Are you sure you want to delete this resume?")) {
                        deleteMutation.mutate(resume.id);
                      }
                    }}
                    className="text-muted-foreground hover:text-destructive transition-colors p-1"
                    title="Delete resume"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1">
                    {resume.title}
                  </h3>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {resume.target_role || "General Role"}
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-border/50 flex items-center justify-between text-[11px] text-muted-foreground">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5" />
                    <span>v{resume.version_count || 1}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{formatDate(resume.created_at).split(",")[0]}</span>
                  </span>
                </div>

                <Link
                  to={`/resumes/${resume.id}`}
                  className="text-primary font-medium hover:underline flex items-center gap-1"
                >
                  <span>Inspect</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload / Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-xl border border-border shadow-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-5 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground">Add New Resume</h2>
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
                  Resume Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. Senior Backend Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Target Role (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Staff Software Engineer"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              {/* Input Source Tabs */}
              <div>
                <label className="block text-xs font-medium text-foreground mb-1.5">
                  Input Method
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveTab("FILE")}
                    className={`py-2 text-xs rounded-lg border font-medium flex items-center justify-center gap-1.5 transition-colors ${
                      activeTab === "FILE"
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-muted/40 border-border text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    <Upload className="w-3.5 h-3.5" />
                    <span>File Upload</span>
                  </button>
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
                    <span>Direct Text</span>
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
                    <span>URL Import</span>
                  </button>
                </div>
              </div>

              {/* Dynamic Tab Contents */}
              {activeTab === "FILE" && (
                <div className="border-2 border-dashed border-border/80 rounded-xl p-6 text-center hover:border-primary/50 transition-colors">
                  <input
                    type="file"
                    id="resume-file-input"
                    accept=".pdf,.docx"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                  <label
                    htmlFor="resume-file-input"
                    className="cursor-pointer flex flex-col items-center justify-center space-y-2"
                  >
                    <Upload className="w-6 h-6 text-muted-foreground" />
                    <span className="text-xs font-medium text-foreground">
                      {selectedFile ? selectedFile.name : "Select PDF or DOCX file"}
                    </span>
                    <span className="text-[11px] text-muted-foreground">
                      Max file size: 10 MB
                    </span>
                  </label>
                </div>
              )}

              {activeTab === "TEXT" && (
                <div>
                  <textarea
                    rows={6}
                    placeholder="Paste resume content here..."
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                  />
                </div>
              )}

              {activeTab === "URL" && (
                <div>
                  <input
                    type="url"
                    placeholder="https://example.com/my-resume.pdf"
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
                  (activeTab === "FILE" && !selectedFile) ||
                  (activeTab === "TEXT" && !rawText.trim()) ||
                  (activeTab === "URL" && !sourceUrl.trim())
                }
                onClick={() => createMutation.mutate()}
                className="px-4 py-2 text-xs bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {createMutation.isPending ? "Extracting..." : "Parse & Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
