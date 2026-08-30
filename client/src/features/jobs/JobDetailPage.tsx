import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import {
  ArrowLeft,
  Briefcase,
  Building2,
  Sparkles,
  CheckCircle2,
  Star,
  ListOrdered,
} from "lucide-react";
import { formatDate } from "../../lib/utils";

export const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: job, isLoading } = useQuery({
    queryKey: ["job-description", id],
    queryFn: () => api.getJobDescription(id!),
    enabled: !!id,
  });

  if (isLoading || !job) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-muted-foreground text-xs">
        Loading job description...
      </div>
    );
  }

  const structured = job.current_version?.structured_data;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <Link
            to="/jobs"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-medium mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Job Catalog</span>
          </Link>
          <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
            {job.title}
          </h1>
          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
            <span className="flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5" />
              <span>{job.company_name || "Company Unspecified"}</span>
            </span>
            <span>•</span>
            <span>Created {formatDate(job.created_at)}</span>
          </div>
        </div>

        <Link
          to={`/evaluate?job_description_version_id=${job.current_version_id}`}
          className="px-4 py-2 text-xs font-medium bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg shadow-xs transition-colors flex items-center gap-2 self-start sm:self-auto"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Match with Resume</span>
        </Link>
      </div>

      {/* Structured Requirements Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Required & Preferred Skills */}
        <div className="space-y-6">
          {/* Required Skills */}
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              <span>Required Skills</span>
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {structured?.required_skills?.length ? (
                structured.required_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 text-xs rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-xs text-muted-foreground">None extracted.</span>
              )}
            </div>
          </div>

          {/* Preferred Skills */}
          {structured?.preferred_skills?.length ? (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                <Star className="w-3.5 h-3.5 text-amber-500" />
                <span>Preferred / Bonus Skills</span>
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {structured.preferred_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 text-[11px] rounded-md bg-secondary text-secondary-foreground"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          {/* Role Metadata */}
          <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-2 text-xs">
            <div className="text-muted-foreground">
              Seniority:{" "}
              <span className="text-foreground font-medium">
                {structured?.seniority_level || "Not specified"}
              </span>
            </div>
            <div className="text-muted-foreground">
              Employment:{" "}
              <span className="text-foreground font-medium">
                {structured?.employment_type || "Full-time"}
              </span>
            </div>
          </div>
        </div>

        {/* Right 2 Columns: Core Responsibilities & Qualifications */}
        <div className="lg:col-span-2 space-y-6">
          {/* Responsibilities */}
          {structured?.core_responsibilities?.length ? (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                <ListOrdered className="w-3.5 h-3.5 text-primary" />
                <span>Core Responsibilities</span>
              </h3>
              <ul className="space-y-2 text-xs text-muted-foreground list-disc list-inside">
                {structured.core_responsibilities.map((resp, idx) => (
                  <li key={idx} className="leading-relaxed">
                    {resp}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {/* Minimum Qualifications */}
          {structured?.minimum_qualifications?.length ? (
            <div className="p-5 bg-card rounded-xl border border-border/70 shadow-xs space-y-3">
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-primary" />
                <span>Qualifications & Experience</span>
              </h3>
              <ul className="space-y-2 text-xs text-muted-foreground list-disc list-inside">
                {structured.minimum_qualifications.map((qual, idx) => (
                  <li key={idx} className="leading-relaxed">
                    {qual}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
