# Engineering Skills & Capabilities Reference

This document catalogs the engineering disciplines, toolchains, and operational competencies required for building, maintaining, and scaling the **AI Resume Evaluator** platform. It maps project requirements to practical development workflows and rules.

---

## 1. Skills Matrix Overview

| Discipline | Key Technologies | Responsibility in Project | Project Rules & Constraints |
|---|---|---|---|
| **Backend Architecture** | FastAPI, Python 3.11+, Pydantic v2, uv | API routing, request validation, modular monolith design, async runtime | Thin controllers; strict separation into API, Service, Domain, and Repository layers. |
| **Database & ORM** | PostgreSQL (Supabase), SQLAlchemy 2.0 Async, Alembic | Relational data modeling, migrations, JSONB indexing, transactions | Never alter DB manually; explicit UUID primary keys; soft-delete for user entities; strict foreign keys. |
| **Authentication & Security** | Supabase Auth, JWT (PyJWT), Cryptography | Auth tokens, object-level authorization (IDOR prevention), RLS | Validate Supabase JWT on every protected route; verify object ownership in repo/service; no secrets in frontend. |
| **AI / LLM Engineering** | Groq, OpenAI, Anthropic, Gemini, Tenacity, tiktoken | Resilient prompt pipeline, structured output validation, token estimation | Provider abstraction interface; prompt & rubric semantic versioning; 2-stage JSON repair retry; prompt injection defense. |
| **Storage & File Processing** | Supabase Storage, PyMuPDF, python-docx | PDF/DOCX text extraction, pre-signed upload URLs, checksum hashing | Files max 10MB; MIME allowlist validation; compute SHA-256 before storage; never store raw binaries in DB. |
| **Frontend Architecture** | React 19, TypeScript, Vite, React Router, TanStack Query | Client state, routing, caching, feature-sliced module layout | Server state managed via TanStack Query; strict TypeScript types (no `any`); feature-driven folder structure. |
| **UI/UX & Design System** | Tailwind CSS, shadcn/ui, Framer Motion, Lucide | Notion-inspired minimalist aesthetic, Dark/Light sliding toggle, micro-interactions | Calm, information-dense layout; subtle animations; respect `prefers-reduced-motion`; custom subtle cursor tail. |
| **Quality & Testing** | Pytest, pytest-asyncio, Playwright, Vitest, Testing Library | Test pyramid (Unit, Integration, API, E2E, Contract) | Mock AI in CI; test ownership boundaries; contract tests for LLM schemas; E2E evaluation flow validation. |
| **Observability & Ops** | Structlog, ContextVars, OpenTelemetry/Sentry (future) | Structured JSON logs, request correlation IDs, token usage tracking | Never log raw resume PII or API secrets; track model latency, error rates, and token consumption. |

---

## 2. Detailed Disciplines & Operational Rules

### A. Backend Engineering (FastAPI + Async Python)
- **Role**: Core application orchestration, business rules enforcement, and REST API contract management.
- **Workflow**:
  1. Define request and response schemas in `app/schemas/` using Pydantic v2.
  2. Implement business logic inside `app/services/`.
  3. Keep FastAPI route handlers under `app/api/v1/endpoints/` purely focused on dependency injection, parameter extraction, and status code mapping.
  4. Ensure all asynchronous operations (`async`/`await`) avoid blocking CPU-bound tasks by offloading heavy parsing to thread pools if necessary.
- **Constants Enforcement**: All magic numbers, character caps, timeouts, and byte limits MUST be imported from `app/lib/constants.py`.

### B. Database Engineering (SQLAlchemy 2.0 Async + Supabase PostgreSQL)
- **Role**: Schema evolution, transaction management, data integrity, and performant query execution.
- **Workflow**:
  1. Define ORM models in `app/models/` inheriting from an async `Base` model with UUID primary keys and timestamp mixins.
  2. Write explicit Alembic migration scripts using `alembic revision --autogenerate -m "<description>"`.
  3. Review generated migration files for proper index creation, nullable flags, and foreign key cascades (`ondelete="CASCADE"` or `"SET NULL"`).
  4. Use SQLAlchemy 2.0 style syntax (`select(...)`, `update(...)`, `delete(...)`) through repository classes under `app/repositories/`.
- **PostgreSQL Features**: Leverage `UUID`, `TIMESTAMPTZ`, `JSONB`, check constraints, and composite indexes for user-scoped lookups.

### C. AI & LLM Systems Engineering
- **Role**: Managing prompt templates, rubric scoring, LLM provider fallback/switching, and structured JSON output guarantee.
- **Workflow**:
  1. All LLM calls MUST pass through the `AIProvider` abstract interface (`app/ai/providers/base.py`).
  2. Maintain prompt templates and scoring rubrics under `app/ai/prompts/` with semantic version tags (e.g., `v1.0.0`).
  3. Enforce token pre-flight checks using `tiktoken` to reject payloads exceeding `MAX_INPUT_TOKENS` before invoking external APIs.
  4. Validate all LLM JSON completions with Pydantic models. On validation error, trigger a single automated correction prompt passing the validation error back to the model.
  5. Log token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`) for every run into the `evaluation_runs` record.

### D. Security & Identity Engineering
- **Role**: Protecting user data, preventing unauthorized access, ensuring safe file handling, and mitigating prompt injection.
- **Workflow**:
  1. Validate incoming Supabase JWT tokens via `app/security/auth.py` FastAPI dependency.
  2. Inject authenticated `current_user` into service layer; enforce `WHERE user_id = current_user.id` on all read/write/delete operations.
  3. Validate uploaded file magic bytes (MIME type verification) and file size caps (10MB) before parsing.
  4. Wrap user-submitted resume and job description text within explicit structural XML/delimited tags (`<resume_data>`, `<job_description>`) in prompts to prevent prompt injection hijacking.

### E. Frontend Engineering (React 19 + TypeScript + Vite)
- **Role**: Providing a responsive, Notion-inspired user interface with client-side state caching and fluid feedback.
- **Workflow**:
  1. Structure frontend code by features: `src/features/<feature-name>/{components,hooks,api,types}`.
  2. Use TanStack Query (`@tanstack/react-query`) for all asynchronous server state with defined `staleTime` and explicit query key factories.
  3. Style components using Tailwind CSS utility classes and shadcn/ui primitives.
  4. Implement Light/Dark theme switching via a sliding header toggle with smooth transitions and persistent `localStorage` state.
  5. Include subtle micro-interactions (hover elevation, button tap feedback, animated score counters, evaluation step progress) using Framer Motion.
  6. Implement a lightweight, elegant cursor tail following physics, automatically disabled on touch devices and when `prefers-reduced-motion` is active.

### F. Testing & Quality Assurance
- **Role**: Ensuring regression prevention, contract compliance, and end-to-end user journey integrity.
- **Workflow**:
  1. Backend unit tests for parsers, token estimators, and schema validators using `pytest`.
  2. Repository integration tests using an ephemeral PostgreSQL database or test container.
  3. Service and API tests using `pytest-asyncio` and `httpx.AsyncClient` with mocked `AIProvider`.
  4. Frontend unit and component tests using `Vitest` and `React Testing Library`.
  5. End-to-end integration tests using `Playwright` covering the complete resume upload -> JD input -> evaluation -> results review journey.

---

## 3. Tool & Skill Integration in Workspace

### Available Installed Agent Skills
- **`modern-web-guidance`**: Execute before writing modern frontend layout, CSS styling, animations, dialogs, and accessibility components.
- **`chrome-devtools` / `a11y-debugging`**: Use for browser verification, DOM inspection, accessibility auditing, and performance profiling.
- **`firebase-*`**: Available in environment; note that this project uses **Supabase** (PostgreSQL + Auth + Storage), so Firebase is not active for this stack.

---

## 4. Skills Maintenance & Updates
Whenever new capabilities (e.g., pgvector RAG embeddings, background task queues, multi-agent evaluation graphs) are introduced into the project, this `skills.md` document must be updated to reflect the new architecture requirements, testing standards, and security constraints.
