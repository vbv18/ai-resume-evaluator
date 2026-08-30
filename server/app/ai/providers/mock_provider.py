from pydantic import BaseModel
from app.ai.providers.base import AIProvider
from app.schemas.ai_contracts import (
    ATSFindings,
    Education,
    Experience,
    JobDescriptionData,
    KeywordAnalysis,
    MatchedSkill,
    MissingSkill,
    RawEvaluationResult,
    RecommendationItem,
    ResumeData,
    SectionBreakdowns,
)


class MockAIProvider(AIProvider):
    """
    Deterministic Mock AI Provider for automated unit and integration tests.
    Produces valid typed schemas without network calls or API credits.
    """

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        response_schema: type[BaseModel],
        model: str | None = None,
        temperature: float = 0.1,
    ) -> tuple[BaseModel, dict[str, int]]:
        usage = {"prompt_tokens": 500, "completion_tokens": 300, "total_tokens": 800}

        if response_schema == ResumeData:
            mock_resume = ResumeData(
                candidate_name="Alex Johnson",
                skills=["Python", "FastAPI", "PostgreSQL", "Docker", "TypeScript", "React"],
                education=[
                    Education(degree="B.S. in Computer Science", institution="State University", year="2020")
                ],
                experience=[
                    Experience(
                        title="Senior Software Engineer",
                        company="TechCorp Inc.",
                        duration="2021 - Present",
                        description="Built scalable microservices and async APIs in Python.",
                    )
                ],
                projects=["AI Resume Analyzer", "Realtime Chat App"],
                certifications=["AWS Certified Developer"],
                total_years_experience=4.5,
            )
            return mock_resume, usage

        elif response_schema == JobDescriptionData:
            mock_jd = JobDescriptionData(
                job_title="Senior Python Backend Engineer",
                required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
                preferred_skills=["React", "AWS", "Kubernetes"],
                min_years_experience=3.0,
                education_requirements=["B.S. in Computer Science or equivalent"],
                responsibilities=[
                    "Design and build performant backend APIs",
                    "Maintain asynchronous PostgreSQL databases and caching",
                ],
            )
            return mock_jd, usage

        elif response_schema == RawEvaluationResult:
            mock_eval = RawEvaluationResult(
                ats_score=92,
                job_match_score=88,
                skills_match_score=95,
                experience_match_score=85,
                verdict="Good Match",
                executive_summary="Candidate demonstrates strong alignment with backend engineering requirements, particularly in Python, FastAPI, and PostgreSQL.",
                matched_skills=[
                    MatchedSkill(skill="Python", proficiency="Expert", evidence="Built production microservices"),
                    MatchedSkill(skill="FastAPI", proficiency="Advanced", evidence="Designed async APIs"),
                    MatchedSkill(skill="PostgreSQL", proficiency="Advanced", evidence="Maintained async PostgreSQL databases"),
                ],
                missing_skills=[
                    MissingSkill(skill="Kubernetes", criticality="PREFERRED", recommendation="Add hands-on container orchestration projects")
                ],
                keyword_analysis=KeywordAnalysis(
                    matched_keywords=["Python", "FastAPI", "PostgreSQL", "Docker", "Async"],
                    missing_keywords=["Kubernetes", "CI/CD"],
                    density_score=84,
                ),
                ats_findings=ATSFindings(
                    formatting_issues=[],
                    readability_assessment="Clean, standard formatting with clear section hierarchy.",
                    actionable_ats_fixes=["Ensure consistent month-year date formatting across employment entries."],
                ),
                strengths=[
                    "Direct experience with required core tech stack (FastAPI, PostgreSQL)",
                    "Demonstrated project delivery with measurable scope",
                ],
                weaknesses=[
                    "Limited explicit mention of cloud orchestration (Kubernetes)",
                ],
                recommendations=[
                    RecommendationItem(
                        title="Quantify Performance Gains",
                        category="Impact",
                        action="Include specific metrics on API latency or throughput improvements.",
                        before_example="Built scalable microservices in Python.",
                        after_example="Engineered Python microservices reducing average endpoint latency by 35%.",
                    )
                ],
                section_breakdowns=SectionBreakdowns(
                    experience_relevance="Highly relevant senior backend experience.",
                    education_match="Direct match with CS degree.",
                    certifications_impact="AWS certification validates cloud competencies.",
                ),
            )
            return mock_eval, usage

        # Generic fallback
        return response_schema(), usage
