# AI Resume Evaluator — Backend

A FastAPI service that scores how well a resume matches a job description using an LLM pipeline: **parse → structured extraction → evaluation**. Upload a PDF/DOCX resume and a job description, get back a structured fit score, verdict, and reasoning — no manual prompt-wrangling on the client side.

## Why this exists

Resume screening is repetitive, inconsistent, and slow. This service turns unstructured resume/JD text into typed, validated data (via Pydantic schemas) and produces an auditable, structured evaluation instead of a black-box "yes/no."

## How it works

1. **Parse** — extracts raw text from PDF (PyMuPDF) or DOCX (python-docx) uploads.
2. **Extract** — two concurrent LLM calls turn the resume and job description into strongly-typed structured data (skills, experience, education, requirements).
3. **Evaluate** — a third LLM call compares the structured resume against the structured job description and returns a score, verdict, and reasoning.

All three calls run through a shared `LLMClient` (Groq) with automatic retries and exponential backoff on rate limits/timeouts, and every LLM response is schema-validated before it's trusted.

## Tech stack

- **FastAPI** + **Pydantic v2** — async API, request/response validation, typed settings
- **Groq** (LLM inference) via the `groq` SDK, with `tenacity` for retry/backoff
- **PyMuPDF** / **python-docx** — resume text extraction
- **tiktoken** — token counting to enforce input limits before calling the LLM
- **structlog** — structured, queryable JSON logs (incl. per-request token usage)
- **uvicorn** — ASGI server

## Architecture

```
app/
├── api/v1/endpoints/   # HTTP layer — request validation, orchestration
├── services/           # LLM client, resume parsing, extraction, evaluation
├── models/schemas.py   # Pydantic contracts for every LLM output
├── lib/prompts.py      # System prompts
└── core/                # Settings, structured logging, error hierarchy
```

Errors are modeled as a typed exception hierarchy mapped to HTTP status codes, so failures (bad file type, oversized upload, LLM validation failure, provider error) return consistent, structured error responses instead of raw tracebacks.

## Running locally

```bash
uv sync            # or: pip install -e .
cp .env.example .env   # add your GROQ_API_KEY
uvicorn app.main:app --reload
```

## API

`POST /api/v1/evaluate` — multipart form: `resume` (PDF/DOCX file) + `job_description` (text). Returns structured `resume_data`, `job_description_data`, and `evaluation` (score, verdict, reasoning).

## Roadmap

The current pipeline is a linear 3-call chain. Planned evolution toward a more capable, agentic system:

- **RAG for JD grounding** — embed a database of role/skill taxonomies (e.g. O*NET-style) and retrieve relevant context to reduce hallucinated skill matches, instead of relying on the LLM's raw judgment alone.
- **Vector DB (Qdrant/pgvector)** — store embedded resumes for semantic candidate search ("find resumes similar to this JD") rather than one-off single-resume scoring.
- **LangGraph orchestration** — replace the current fixed 3-call sequence with a stateful graph: conditional re-extraction on low-confidence parses, a critique/revise loop on the evaluation step, and clean checkpointing for long-running batch runs.
- **Multi-agent evaluation** — split scoring into specialized sub-agents (skills-match, experience-match, culture/soft-skills) whose outputs are aggregated, improving interpretability over a single monolithic score.
- **Streaming responses** — stream evaluation reasoning token-by-token instead of waiting for the full completion.
- **Feedback loop** — capture recruiter overrides on verdicts to build a fine-tuning/eval dataset over time.

## Status

Core pipeline is functional and production-hardened (input validation, retries, structured errors, token-limit guards). Agentic/RAG features above are the next milestone.
