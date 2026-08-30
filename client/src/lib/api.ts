import { getAuthHeader } from "./supabase";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

export interface Profile {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  professional_title?: string;
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResumeVersion {
  id: string;
  resume_id: string;
  version_number: number;
  input_source: string;
  source_url?: string;
  raw_text: string;
  structured_data: {
    contact_info?: {
      full_name?: string;
      email?: string;
      phone?: string;
      location?: string;
      linkedin?: string;
      github?: string;
    };
    professional_summary?: string;
    skills?: {
      hard_skills?: string[];
      soft_skills?: string[];
      tools_and_technologies?: string[];
      certifications?: string[];
    };
    work_experience?: Array<{
      company?: string;
      position?: string;
      start_date?: string;
      end_date?: string;
      is_current?: boolean;
      responsibilities?: string[];
    }>;
    education?: Array<{
      institution?: string;
      degree?: string;
      field_of_study?: string;
      graduation_year?: string;
    }>;
  };
  change_summary?: string;
  created_at: string;
}

export interface Resume {
  id: string;
  user_id: string;
  title: string;
  target_role?: string;
  current_version_id?: string;
  current_version?: ResumeVersion;
  version_count?: number;
  created_at: string;
  updated_at: string;
}

export interface JobDescriptionVersion {
  id: string;
  job_description_id: string;
  version_number: number;
  input_source: string;
  raw_text: string;
  structured_data: {
    role_title?: string;
    company_name?: string;
    seniority_level?: string;
    employment_type?: string;
    required_skills?: string[];
    preferred_skills?: string[];
    core_responsibilities?: string[];
    minimum_qualifications?: string[];
  };
  created_at: string;
}

export interface JobDescription {
  id: string;
  user_id: string;
  title: string;
  company_name?: string;
  current_version_id?: string;
  current_version?: JobDescriptionVersion;
  created_at: string;
  updated_at: string;
}

export interface MatchedSkill {
  skill: string;
  importance: string;
  context_in_resume?: string;
  source_location?: string;
}

export interface MissingSkill {
  skill: string;
  importance: string;
  impact_on_score?: string;
  remedy?: string;
}

export interface Recommendation {
  category: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  issue: string;
  action: string;
  example: string;
}

export interface EvaluationResult {
  id: string;
  evaluation_run_id: string;
  executive_summary: string;
  matched_skills: MatchedSkill[];
  missing_skills: MissingSkill[];
  keyword_analysis: {
    matched_keywords?: string[];
    missing_keywords?: string[];
    density_rating?: string;
    summary?: string;
  };
  ats_findings: {
    score?: number;
    formatting_issues?: string[];
    section_issues?: string[];
    parseability_rating?: string;
  };
  strengths: string[];
  weaknesses: string[];
  recommendations: Recommendation[];
  section_breakdowns: {
    summary_review?: { score: number; feedback: string };
    experience_review?: { score: number; feedback: string };
    skills_review?: { score: number; feedback: string };
    education_review?: { score: number; feedback: string };
  };
  created_at: string;
}

export interface EvaluationRun {
  id: string;
  user_id: string;
  resume_version_id: string;
  job_description_version_id: string;
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED" | "CANCELLED";
  ai_provider: string;
  model_name: string;
  prompt_version: string;
  rubric_version: string;
  overall_score?: number;
  ats_score?: number;
  job_match_score?: number;
  skills_match_score?: number;
  experience_match_score?: number;
  verdict?: string;
  duration_ms?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  result?: EvaluationResult;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface ComparisonDiff {
  run_a: EvaluationRun;
  run_b: EvaluationRun;
  overall_delta: number;
  score_diffs: Array<{
    category: string;
    score_a: number;
    score_b: number;
    delta: number;
  }>;
  newly_matched_skills: string[];
  still_missing_skills: string[];
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const authHeaders = await getAuthHeader();
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      ...authHeaders,
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData?.error?.message || `Request failed with status ${res.status}`;
    throw new Error(message);
  }

  return res.json();
}

export const api = {
  // Profiles
  getProfile: () => request<Profile>("/profile"),
  updateProfile: (data: Partial<Profile>) =>
    request<Profile>("/profile", { method: "PATCH", body: JSON.stringify(data) }),

  // Resumes
  listResumes: (page = 1, pageSize = 20) =>
    request<{ data: Resume[]; pagination: any }>(`/resumes?page=${page}&page_size=${pageSize}`),
  getResume: (id: string) => request<Resume>(`/resumes/${id}`),
  createResume: (data: { title: string; target_role?: string; input_source?: string; raw_text?: string; source_url?: string }) =>
    request<Resume>("/resumes", { method: "POST", body: JSON.stringify(data) }),
  uploadResumeFile: (file: File, title: string, targetRole?: string) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("title", title);
    if (targetRole) fd.append("target_role", targetRole);
    return request<Resume>("/resumes/upload", { method: "POST", body: fd });
  },
  deleteResume: (id: string) => request<{ success: boolean; message: string }>(`/resumes/${id}`, { method: "DELETE" }),
  createResumeVersion: (resumeId: string, data: { input_source: string; raw_text?: string; source_url?: string; change_summary?: string }) =>
    request<ResumeVersion>(`/resumes/${resumeId}/versions`, { method: "POST", body: JSON.stringify(data) }),
  listResumeVersions: (resumeId: string) => request<any[]>(`/resumes/${resumeId}/versions`),
  getResumeVersion: (resumeId: string, versionId: string) => request<ResumeVersion>(`/resumes/${resumeId}/versions/${versionId}`),

  // Job Descriptions
  listJobDescriptions: (page = 1, pageSize = 20) =>
    request<{ data: JobDescription[]; pagination: any }>(`/job-descriptions?page=${page}&page_size=${pageSize}`),
  getJobDescription: (id: string) => request<JobDescription>(`/job-descriptions/${id}`),
  createJobDescription: (data: { title: string; company_name?: string; input_source: string; raw_text?: string; source_url?: string }) =>
    request<JobDescription>("/job-descriptions", { method: "POST", body: JSON.stringify(data) }),
  archiveJobDescription: (id: string) => request<{ success: boolean; message: string }>(`/job-descriptions/${id}`, { method: "DELETE" }),

  // Evaluations
  enqueueEvaluation: (data: { resume_version_id: string; job_description_version_id: string; ai_provider?: string; model_name?: string }) =>
    request<{ evaluation_id: string; status: string; message: string }>("/evaluations", { method: "POST", body: JSON.stringify(data) }),
  getEvaluation: (id: string) => request<EvaluationRun>(`/evaluations/${id}`),
  getEvaluationStatus: (id: string) =>
    request<{ evaluation_id: string; status: string; progress_percentage: number; started_at?: string; completed_at?: string; error_message?: string }>(`/evaluations/${id}/status`),
  listEvaluations: (page = 1, pageSize = 20) =>
    request<{ data: EvaluationRun[]; pagination: any }>(`/evaluations?page=${page}&page_size=${pageSize}`),
  compareEvaluations: (runA: string, runB: string) =>
    request<ComparisonDiff>(`/evaluations/compare?run_a=${runA}&run_b=${runB}`),
};
