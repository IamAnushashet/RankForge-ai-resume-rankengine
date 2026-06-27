import pandas as pd
import numpy as np
from joblib import Parallel, delayed

def _join(items, key: str) -> str:
    if not isinstance(items, list):
        return ""
    return " ".join(str(x.get(key, "")) for x in items if isinstance(x, dict))

def _skill_names(skills) -> list[str]:
    if not isinstance(skills, list):
        return []
    return [str(s.get("name", "")) for s in skills if isinstance(s, dict) and s.get("name")]

def _get_val(d, k, default):
    v = d.get(k)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    return v

def _flatten_record(record: dict) -> dict:
    profile = _get_val(record, "profile", {})
    career = _get_val(record, "career_history", [])
    education = _get_val(record, "education", [])
    skills = _get_val(record, "skills", [])
    signals = _get_val(record, "redrob_signals", {})
    salary = _get_val(signals, "expected_salary_range_inr_lpa", {})
    assessments = _get_val(signals, "skill_assessment_scores", {})

    titles = _join(career, "title")
    descriptions = _join(career, "description")
    companies = _join(career, "company")
    edu_fields = _join(education, "field_of_study")
    names = _skill_names(skills)
    skill_text = " ".join(names)
    endorsements = sum(int(s.get("endorsements", 0) or 0) for s in skills if isinstance(s, dict))
    skill_months = sum(int(s.get("duration_months", 0) or 0) for s in skills if isinstance(s, dict))
    if isinstance(assessments, dict):
        values = [
            float(v)
            for v in assessments.values()
            if v is not None and isinstance(v, (int, float))
        ]
        assessment_avg = sum(values) / max(len(values), 1)
    else:
        assessment_avg = 0
    candidate_text = " ".join(
        str(x)
        for x in [
            profile.get("headline", ""),
            str(profile.get("summary", ""))[:900],
            profile.get("current_title", ""),
            profile.get("current_industry", ""),
            titles,
            descriptions[:1800],
            edu_fields,
            skill_text,
        ]
    )
    
    return {
        "candidate_id": record.get("candidate_id", ""),
        "headline": profile.get("headline", ""),
        "summary": profile.get("summary", ""),
        "location": profile.get("location", ""),
        "country": profile.get("country", ""),
        "years": float(profile.get("years_of_experience", 0) or 0),
        "role": profile.get("current_title", ""),
        "industry": profile.get("current_industry", ""),
        "career_titles": titles,
        "career_descriptions": descriptions,
        "companies": companies,
        "education": edu_fields,
        "skills_text": skill_text,
        "skill_count": len(names),
        "endorsements": endorsements,
        "skill_months": skill_months,
        "assessment_avg": assessment_avg,
        "profile_completeness": float(signals.get("profile_completeness_score", 0) or 0),
        "open_to_work": bool(signals.get("open_to_work_flag", False)),
        "response_rate": float(signals.get("recruiter_response_rate", 0) or 0),
        "response_hours": float(signals.get("avg_response_time_hours", 999) or 999),
        "notice_days": int(signals.get("notice_period_days", 180) or 180),
        "preferred_work_mode": signals.get("preferred_work_mode", ""),
        "willing_to_relocate": bool(signals.get("willing_to_relocate", False)),
        "github_activity": float(signals.get("github_activity_score", -1) or -1),
        "search_appearance": int(signals.get("search_appearance_30d", 0) or 0),
        "saved_by_recruiters": int(signals.get("saved_by_recruiters_30d", 0) or 0),
        "interview_completion": float(signals.get("interview_completion_rate", 0) or 0),
        "offer_acceptance": float(signals.get("offer_acceptance_rate", -1) or -1),
        "verified_email": bool(signals.get("verified_email", False)),
        "verified_phone": bool(signals.get("verified_phone", False)),
        "linkedin_connected": bool(signals.get("linkedin_connected", False)),
        "salary_min": float(salary.get("min", 0) or 0),
        "salary_max": float(salary.get("max", 0) or 0),
        "candidate_text": candidate_text,
    }

def flatten_candidates(df: pd.DataFrame) -> pd.DataFrame:
    records = df.to_dict("records")
    if len(records) > 2000:
        results = Parallel(n_jobs=-1)(delayed(_flatten_record)(r) for r in records)
    else:
        results = [_flatten_record(r) for r in records]
    return pd.DataFrame(results)
