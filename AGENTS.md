# AI Resume Evaluator — Autonomous Agent & Contributor Manual (AGENTS.md)

This document is the authoritative instruction manual for any AI coding agent or human engineer contributing to the **AI Resume Evaluator** repository. All architecture decisions, coding standards, and project constraints documented here are mandatory.

---

## 1. Project Overview & Mission

The **AI Resume Evaluator** is a production-grade web application that helps candidates, job seekers, and recruiters analyze, score, and optimize resumes against job descriptions.

Key capabilities:
1. **Authentication**: Multi-provider authentication via Supabase Auth (Email/password, Google, GitHub).
2. **Resume Management**: Upload and maintain multiple resumes and version snapshots (PDF, DOCX, direct text, or URL import).
3. **Job Description Catalog**: Store, manage, and version job descriptions with structured requirement extraction.
4. **Multi-Criteria AI Evaluation**: Immutable evaluation runs generating detailed fit scores:
   - Component scores returned by AI:
     - ATS Compatibility & Formatting Score (0–100)
     - Job Description Match Score (0–100)
     - Hard Skills & Tech Stack Match Score (0–100)
     - Experience Relevance & Seniority Score (0–100)
   - Overall Fit Score (0–100): Calculated **deterministically by backend formula** using configured rubric weights:
     $$\text{Overall Score} = (\text{ATS} \times 0.25) + (\text{JobMatch} \times 0.30) + (\text{Skills} \times 0.25) + (\text{Experience} \times 0.20)$$
   - Matched & Missing Skills Analysis
   - Keyword Density & Coverage
   - Strengths, Weaknesses, and Actionable Recommendations with step-by-step guidance
5. **Historical Auditing & Diffing**: Track score trends and compare improvements between resume versions.
6. **Extensible AI Architecture**: Future-proofed for RAG-based skill grounding and vector candidate search without architectural rewrite.

---

## 2. System Architecture & Boundaries

The backend follows a **Modular Monolith** architecture with strict layer separation:

```text
HTTP Request
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ 1. API Layer (FastAPI routes & dependencies)           │
│    - Parameter binding, auth token validation          │
│    - Schema validation (Pydantic v2)                   │
│    - HTTP status code & error envelope translation     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Application Service Layer (app/services/)           │
│    - Use-case orchestration, business workflow rules   │
│    - Cross-cutting concerns (logging, audit trails)    │
│    - Transaction boundary management                   │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ 3. Domain & AI Layer      │ │ 4. Repository Layer      │
│    (app/domain/, app/ai/) │ │    (app/repositories/)   │
│    - Evaluation engine    │ │    - SQLAlchemy 2.0 Async│
│    - AI Provider strategy │ │    - Data access logic   │
│    - Prompt & Rubric logic│ │    - Explicit filters    │
│    - Text parsing logic   │ │    - Tenant isolation    │
└─────────────┬─────────────┘ └────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ External AI Providers     │ │ PostgreSQL (Supabase)    │
│ (OpenAI / Groq / Gemini)  │ │ (Tables, JSONB, Indexes) │
│ e.g. openai/gpt-oss-20b   │ │ SKIP LOCKED Job Worker   │
└───────────────────────────┘ └──────────────────────────┘
```

### Layer Rules
- **API Controllers (`app/api/v1/endpoints/`)**: MUST be thin. No SQL queries, no direct LLM SDK calls, no complex business calculations.
- **Services (`app/services/`)**: Orchestrate repositories, AI providers, and storage. Services accept and return domain models or Pydantic schemas.
- **Repositories (`app/repositories/`)**: Encapsulate all database interaction using Async SQLAlchemy 2.0. Every query involving user-owned data MUST enforce ownership filters (`WHERE user_id = :user_id`).
- **AI Abstraction (`app/ai/`)**: All LLM calls MUST go through the `AIProvider` abstract protocol. Never invoke external LLMs directly inside route handlers or controllers.
- **Constants (`app/lib/constants.py`)**: All limits (file size, character limits, token limits, timeouts, system prompts) MUST be defined in `constants.py`.

---

## 3. Backend Rules & Best Practices

1. **Python Runtime**: Python 3.11+ using `uv` for package management.
2. **Pydantic v2**:
   - Use Pydantic schemas for all API inputs (`*Create`, `*Update`), API outputs (`*Response`), and LLM structured responses.
   - Use `model_config = ConfigDict(from_attributes=True)` for ORM mapping.
3. **Async Everywhere**: All I/O operations (database queries, network requests, file reading, AI calls) MUST be asynchronous (`async def` and `await`).
4. **Structured Logging**: Use `structlog` with contextual logging. Always include `request_id`, `user_id`, and operation context. Never log raw resume PII or secret keys.
5. **Centralized Error Handling**:
   - Raise custom exceptions derived from `AppError` (`app/core/exceptions.py`).
   - Every error MUST produce a standardized JSON payload:
     ```json
     {
       "error": {
         "code": "RESOURCE_NOT_FOUND",
         "message": "Resume version not found",
         "details": null,
         "request_id": "req_abc123"
       }
     }
     ```
   - Never expose internal tracebacks to clients.

---

## 4. Database & Migration Rules

1. **SQLAlchemy 2.0 Async**:
   - Use `select()`, `insert()`, `update()`, `delete()` syntax with `await session.execute()`.
   - Never use legacy query APIs (`session.query()`).
2. **Alembic Migrations**:
   - Never alter the database schema manually or execute ad-hoc DDL in production.
   - Every schema change MUST be accompanied by an Alembic migration script in `server/alembic/versions/`.
   - Always verify both `upgrade()` and `downgrade()` functions.
3. **Data Integrity & PostgreSQL Features**:
   - Primary keys MUST be PostgreSQL `UUID` (generated via `gen_random_uuid()`).
   - Timestamps MUST use `TIMESTAMPTZ` with UTC defaults (`server_default=func.now()`).
   - Soft-delete MUST be used for core user entities (`is_deleted: bool = False`, `deleted_at: datetime | None`).
   - Historical records (`evaluation_runs`, `evaluation_results`, `resume_versions`, `job_description_versions`) are **IMMUTABLE**; once written, they are never updated in place.
   - Use `JSONB` for nested structured representations (`ResumeData`, `JobDescriptionData`, validated evaluation output, section breakdowns) and create GIN indexes where query filtering is required.
   - Foreign keys MUST have explicit `ondelete` actions (`CASCADE` or `SET NULL` or `RESTRICT`).
   - System prompts are maintained in code (`app/lib/constants.py`), NOT in database tables.
   - `profiles` table does NOT store derived counters like `evaluation_count`. Derive via `SELECT COUNT(*) FROM evaluation_runs WHERE user_id = :id`.
4. **PostgreSQL Background Worker**:
   - Job queue is natively backed by PostgreSQL using `SELECT ... FOR UPDATE SKIP LOCKED` on `evaluation_runs WHERE status = 'QUEUED'`. No Redis required.

---

## 5. Authentication & Security Rules

1. **Supabase Auth Integration**:
   - Frontend authenticates with Supabase Auth (Email, Google, GitHub) and passes the JWT bearer token in the `Authorization: Bearer <token>` header.
   - Backend validates the JWT signature, audience, and expiration using Supabase public JWKS / secret.
   - The verified `sub` UUID is mapped to `app.models.Profile`.
2. **Object-Level Authorization (IDOR Prevention)**:
   - Always verify that the authenticated user owns the resource before returning or mutating it.
   - Check `WHERE resource.user_id = current_user.id` on every query.
3. **File Upload Security**:
   - Enforce `MAX_RESUME_FILE_SIZE_BYTES = 10 * 1024 * 1024` (10 MB).
   - Validate file MIME types against the allowlist (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
   - Inspect magic bytes (file signature) before processing; do not trust file extensions alone.
   - Store files in Supabase Storage with user-isolated path prefixes: `resumes/{user_id}/{file_uuid}.pdf`.
   - `resume_files` table stores physical storage metadata only; parsed text and structured data belong solely to `resume_versions`.
4. **Prompt Injection & AI Security**:
   - Treat all user-supplied resume and job description text as untrusted.
   - Encapsulate inputs inside structured delimiters (`<resume_text>...</resume_text>`, `<job_description>...</job_description>`).
   - Include strict negative constraints in system prompts to prevent instruction override.
   - `raw_ai_response` in `evaluation_results` stores sanitized response data and provider metadata; NEVER store API keys, auth headers, or raw secrets.

---

## 6. AI & LLM Engineering Rules

1. **Provider Abstraction**:
   - All AI interactions MUST use the `AIProvider` interface (`generate_structured` and `generate_text`).
   - Provider implementation is selected via configuration (`AI_PROVIDER=groq`, `AI_PROVIDER=openai`, etc., supporting `openai/gpt-oss-20b`, `llama-3.3-70b-versatile`, etc.).
2. **Evaluation Reproducibility**:
   - Every `evaluation_run` record MUST record:
     - `resume_version_id` (immutable resume snapshot)
     - `job_description_version_id` (immutable JD snapshot)
     - `model_name` (e.g., `openai/gpt-oss-20b`, `llama-3.3-70b-versatile`)
     - `prompt_version` (e.g., `v1.0.0`)
     - `rubric_version` (e.g., `v1.0.0`)
     - Token metrics (`prompt_tokens`, `completion_tokens`, `total_tokens`)
     - Execution duration in milliseconds
3. **Structured Output & Resilient Validation**:
   - Never accept unstructured text when structured data is required.
   - Validate LLM JSON output against strict Pydantic schemas.
   - If validation fails, trigger a retry with the validation error fed back to the model for self-correction (max 1 retry attempt).
4. **Deterministic Score Computation**:
   - The LLM returns sub-scores (`ats_score`, `job_match_score`, `skills_match_score`, `experience_match_score`).
   - The backend service computes the final `overall_score` deterministically using configured weights (`sum(weights) = 1.0`).
5. **Token Pre-Flight Guard**:
   - Estimate input tokens before sending requests to external APIs using `tiktoken`.
   - Reject inputs exceeding `MAX_INPUT_TOKENS = 6000` with HTTP 422 (`TokenLimitExceededError`).

---

## 7. Frontend Engineering & UX Rules

1. **Technology Stack**: React 19, TypeScript (strict mode), Vite, React Router, TanStack Query, Tailwind CSS, shadcn/ui, Framer Motion.
2. **Visual Direction (Notion-Inspired)**:
   - Clean, calm, minimal, information-dense without clutter.
   - Restrained borders (`border-border/60`), subtle background surfaces (`bg-muted/40`), generous whitespace.
   - Neutral base palette (zinc/slate) with intentional, minimal accent colors.
   - No excessive colorful gradients or flashy AI clichés.
   - Dashboard must be vibrant, clean, and calm.
3. **Theme Switcher**:
   - Header MUST include an elegant sliding switch to toggle between **Light** and **Dark** themes.
   - Smooth CSS transitions between themes, persisting user preference in `localStorage`.
4. **Product-Focused Micro-Interactions**:
   - Upload lifecycle: drag/drop feedback -> upload progress -> parsing state -> parsed preview.
   - Evaluation lifecycle: queued -> processing step indicators -> animated score reveal.
   - Animated count-up numbers for all score vectors (`0 -> 87`).
   - Smooth collapsible recommendation cards with before/after rewrite examples.
   - Version-to-version score improvement diff visualizer.
   - Hover elevations, smooth button feedback, and skeleton loading states.
   - Respect `prefers-reduced-motion: reduce`.
5. **State Management**:
   - Use TanStack Query for all server data caching, background polling/revalidation, and optimistic updates.
   - Keep local state minimal (React `useState`/`useReducer`).
   - Avoid Redux or excessive global stores.

---

## 8. Testing Strategy & Quality Standards

1. **Backend Tests (`pytest`)**:
   - **Unit Tests**: Test parsers (PDF/DOCX), token estimators, prompt formatting, deterministic score formulas, and Pydantic schema validators.
   - **Integration Tests**: Test repositories, PostgreSQL `SKIP LOCKED` worker, and database transactions using an isolated test database.
   - **API Contract Tests**: Test all REST endpoints with `httpx.AsyncClient`, verifying auth headers, permissions, and status codes.
   - **Mock AI Provider**: Use `MockAIProvider` returning deterministic JSON fixtures for testing the evaluation pipeline without spending API credits or making network calls.
2. **Frontend Tests (`Vitest` + `Testing Library`)**:
   - Unit test utility functions, custom hooks, and isolated UI components.
   - Integration test feature flows (upload form, JD versioning, evaluation results rendering, score diff comparison).
3. **End-to-End Tests (`Playwright`)**:
   - Full user journey test: Sign in -> Upload resume -> Enter JD -> Trigger evaluation -> Verify results breakdown -> Create v2 -> View score diff.

---

## 9. Code Modification & Contribution Rules

When implementing or modifying code in this repository, future agents MUST follow this protocol:

1. **Inspect Before Changing**: Read existing implementations, models, and schemas before creating new ones.
2. **Preserve Architectural Boundaries**: Never cross layer boundaries (e.g., calling DB from API routes or calling LLM from React components).
3. **Make Focused, Atomic Changes**: Avoid sweeping unsolicited refactors. Change only what is necessary to fulfill the requirement.
4. **Maintain Types & Documentation**: Always provide full TypeScript and Python type annotations. No `any` or untyped dictionaries where schemas belong.
5. **Verify Changes**: Run linting (`oxlint` / `ruff`), type-checks (`tsc` / `pyright` / `mypy`), and automated tests before marking tasks as complete.

---

## 10. Strictly Forbidden Shortcuts

- ❌ **DO NOT** put business logic or SQL queries directly in FastAPI route handlers.
- ❌ **DO NOT** invoke LLM APIs directly from the frontend or bypass the backend evaluation pipeline.
- ❌ **DO NOT** bypass user authentication or object-level ownership checks (`WHERE user_id = current_user.id`).
- ❌ **DO NOT** manually modify database tables in production without an Alembic migration.
- ❌ **DO NOT** commit API keys, database credentials, or secrets to Git.
- ❌ **DO NOT** use `Any` / `any` to bypass type errors.
- ❌ **DO NOT** disable tests or suppress linter errors without explicit architectural justification.
- ❌ **DO NOT** store large binary resume files in PostgreSQL columns.
- ❌ **DO NOT** duplicate parsed resume text in `resume_files` (keep in `resume_versions`).
- ❌ **DO NOT** mutate historical `evaluation_runs`, `resume_versions`, or `job_description_versions` records in place.
- ❌ **DO NOT** let LLMs compute overall weighted scores; compute deterministically in backend code.
- ❌ **DO NOT** introduce Redis when PostgreSQL `SKIP LOCKED` satisfies the workload.
- ❌ **DO NOT** introduce Prisma or alternative ORMs.
