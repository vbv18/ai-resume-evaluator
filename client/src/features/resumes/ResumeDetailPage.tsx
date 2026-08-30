import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  ArrowLeft,
  Briefcase,
  GraduationCap,
  Sparkles,
  Layers,
  Plus,
  Mail,
  MapPin,
  Globe,
  X,
  Code2,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const ResumeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [isNewVersionModalOpen, setIsNewVersionModalOpen] = useState(false);

  // New version state
  const [newRawText, setNewRawText] = useState("");
  const [changeSummary, setChangeSummary] = useState("");

  const { data: resume, isLoading } = useQuery({
    queryKey: ["resume", id],
    queryFn: () => api.getResume(id!),
    enabled: !!id,
  });

  const { data: versions = [] } = useQuery({
    queryKey: ["resume-versions", id],
    queryFn: () => api.listResumeVersions(id!),
    enabled: !!id,
  });

  const activeVersionId = selectedVersionId || resume?.current_version_id;

  const { data: activeVersion } = useQuery({
    queryKey: ["resume-version", id, activeVersionId],
    queryFn: () => api.getResumeVersion(id!, activeVersionId!),
    enabled: !!id && !!activeVersionId,
  });

  const createVersionMutation = useMutation({
    mutationFn: () =>
      api.createResumeVersion(id!, {
        input_source: "DIRECT_TEXT",
        raw_text: newRawText,
        change_summary: changeSummary,
      }),
    onSuccess: (newVersion) => {
      queryClient.invalidateQueries({ queryKey: ["resume", id] });
      queryClient.invalidateQueries({ queryKey: ["resume-versions", id] });
      setSelectedVersionId(newVersion.id);
      setIsNewVersionModalOpen(false);
      setNewRawText("");
      setChangeSummary("");
    },
  });

  if (isLoading || !resume) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-muted-foreground text-xs">
        Loading resume details...
      </div>
    );
  }

  const structured = activeVersion?.structured_data || resume.current_version?.structured_data;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <Link
            to="/resumes"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-medium mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Resumes</span>
          </Link>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            {resume.title}
          </h1>
          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
            <span>Target: {resume.target_role || "General"}</span>
            <span>•</span>
            <span>Created {formatDate(resume.created_at)}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsNewVersionModalOpen(true)}
            className="px-3.5 py-2 text-xs font-medium bg-card hover:bg-muted text-foreground border border-border/80 rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create New Version</span>
          </button>

          <Link
            to={`/evaluate?resume_version_id=${activeVersionId}`}
            className="px-3.5 py-2 text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-xs transition-colors flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Evaluate with AI</span>
          </Link>
        </div>
      </div>

      {/* Version History Selector */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <span className="text-xs font-medium text-muted-foreground flex items-center gap-1.5 mr-2">
          <Layers className="w-3.5 h-3.5" />
          <span>Versions:</span>
        </span>
        {versions.map((ver: any) => {
          const isSelected = ver.id === activeVersionId;
          return (
            <button
              key={ver.id}
              onClick={() => setSelectedVersionId(ver.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center gap-2 cursor-pointer ${
                isSelected
                  ? "bg-primary/10 border-primary text-primary font-semibold shadow-xs"
                  : "bg-card border-border text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <span>v{ver.version_number}</span>
              {ver.change_summary && (
                <span className="text-[10px] opacity-75 truncate max-w-[120px]">
                  ({ver.change_summary})
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Structured Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Contact & Skills */}
        <div className="space-y-6">
          {/* Contact Card */}
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Contact & Profile
            </h3>
            <div className="space-y-2 text-xs text-muted-foreground">
              {structured?.contact_info?.full_name && (
                <div className="text-sm font-bold text-foreground">
                  {structured.contact_info.full_name}
                </div>
              )}
              {structured?.contact_info?.email && (
                <div className="flex items-center gap-2">
                  <Mail className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>{structured.contact_info.email}</span>
                </div>
              )}
              {structured?.contact_info?.location && (
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>{structured.contact_info.location}</span>
                </div>
              )}
              {structured?.contact_info?.linkedin && (
                <div className="flex items-center gap-2">
                  <Globe className="w-3.5 h-3.5 text-muted-foreground" />
                  <span className="truncate">{structured.contact_info.linkedin}</span>
                </div>
              )}
              {structured?.contact_info?.github && (
                <div className="flex items-center gap-2">
                  <Code2 className="w-3.5 h-3.5 text-muted-foreground" />
                  <span className="truncate">{structured.contact_info.github}</span>
                </div>
              )}
            </div>
          </div>

          {/* Hard Skills */}
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Code2 className="w-3.5 h-3.5 text-primary" />
              <span>Hard Skills & Technologies</span>
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {structured?.skills?.hard_skills?.length ? (
                structured.skills.hard_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 text-xs rounded-md bg-muted font-medium text-foreground border border-border/50"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-foreground">No skills extracted.</span>
              )}
            </div>
          </div>

          {/* Tools & Soft Skills */}
          {structured?.skills?.tools_and_technologies?.length ? (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
                Tools & Frameworks
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {structured.skills.tools_and_technologies.map((tool, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 text-[11px] rounded-md bg-secondary text-secondary-foreground"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* Right 2 Columns: Summary, Experience, Education */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary Card */}
          {structured?.professional_summary && (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-2">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
                Professional Summary
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {structured.professional_summary}
              </p>
            </div>
          )}

          {/* Experience Section */}
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-primary" />
              <span>Work Experience</span>
            </h3>

            {structured?.work_experience?.length ? (
              <div className="space-y-4 divide-y divide-border/50">
                {structured.work_experience.map((exp, idx) => (
                  <div key={idx} className={idx > 0 ? "pt-4" : ""}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-xs font-bold text-foreground">
                          {exp.position || "Position"}
                        </div>
                        <div className="text-xs text-muted-foreground font-medium">
                          {exp.company || "Company"}
                        </div>
                      </div>
                      <div className="text-[11px] text-muted-foreground bg-muted px-2 py-0.5 rounded">
                        {exp.start_date || "Start"} — {exp.is_current ? "Present" : exp.end_date || "End"}
                      </div>
                    </div>

                    {exp.responsibilities && (
                      <ul className="mt-2 space-y-1 text-xs text-muted-foreground list-disc list-inside">
                        {exp.responsibilities.map((resp, rIdx) => (
                          <li key={rIdx} className="leading-relaxed">
                            {resp}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <span className="text-xs text-muted-foreground">No experience parsed.</span>
            )}
          </div>

          {/* Education Section */}
          {structured?.education?.length ? (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-4">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                <GraduationCap className="w-3.5 h-3.5 text-primary" />
                <span>Education</span>
              </h3>
              <div className="space-y-3">
                {structured.education.map((edu, idx) => (
                  <div key={idx} className="flex items-start justify-between">
                    <div>
                      <div className="text-xs font-bold text-foreground">
                        {edu.degree || "Degree"} {edu.field_of_study ? `in ${edu.field_of_study}` : ""}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {edu.institution || "Institution"}
                      </div>
                    </div>
                    {edu.graduation_year && (
                      <div className="text-[11px] text-muted-foreground">
                        {edu.graduation_year}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* New Version Modal */}
      {isNewVersionModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-xl border border-border shadow-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-5 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground">
                Create Version Snapshot (v{versions.length + 1})
              </h2>
              <button
                onClick={() => setIsNewVersionModalOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Change Summary / Goal
                </label>
                <input
                  type="text"
                  placeholder="e.g. Added Kubernetes and optimized keywords for Staff role"
                  value={changeSummary}
                  onChange={(e) => setChangeSummary(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-foreground mb-1">
                  Updated Resume Content
                </label>
                <textarea
                  rows={8}
                  placeholder="Paste your updated resume text here..."
                  value={newRawText}
                  onChange={(e) => setNewRawText(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-muted/40 border border-border rounded-lg text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
              </div>
            </div>

            <div className="p-4 border-t border-border bg-muted/20 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsNewVersionModalOpen(false)}
                className="px-3.5 py-1.5 text-xs text-muted-foreground hover:text-foreground font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={createVersionMutation.isPending || !newRawText.trim()}
                onClick={() => createVersionMutation.mutate()}
                className="px-4 py-2 text-xs bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {createVersionMutation.isPending ? "Parsing Version..." : "Save Version"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
