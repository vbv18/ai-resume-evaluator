from app.lib.constants import (
    WEIGHT_ATS,
    WEIGHT_EXPERIENCE,
    WEIGHT_JOB_MATCH,
    WEIGHT_SKILLS,
)


def calculate_overall_score(
    *,
    ats_score: int,
    job_match_score: int,
    skills_match_score: int,
    experience_match_score: int,
) -> int:
    """
    Deterministically computes the final overall resume score using weighted rubric criteria.
    Formula: round(ATS * 0.25 + JobMatch * 0.30 + Skills * 0.25 + Experience * 0.20)
    Result is guaranteed to be an integer between 0 and 100.
    """
    raw_score = (
        (ats_score * WEIGHT_ATS)
        + (job_match_score * WEIGHT_JOB_MATCH)
        + (skills_match_score * WEIGHT_SKILLS)
        + (experience_match_score * WEIGHT_EXPERIENCE)
    )
    bounded_score = max(0, min(100, round(raw_score)))
    return bounded_score


def determine_verdict(overall_score: int) -> str:
    """
    Maps an overall score to a standardized verbal verdict.
    """
    if overall_score >= 90:
        return "Excellent Match"
    elif overall_score >= 75:
        return "Good Match"
    elif overall_score >= 55:
        return "Moderate Match"
    elif overall_score >= 40:
        return "Weak Match"
    else:
        return "Not a Match"
