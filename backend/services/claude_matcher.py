"""Score job-resume fit using Claude AI."""
import json
import asyncio
from dataclasses import dataclass
from typing import Optional

import anthropic

from backend.core.config import get_settings

SYSTEM_PROMPT = """You are an expert technical recruiter and career coach specializing in \
Data Science, Data Engineering, and AI/ML roles. You evaluate job-candidate fit objectively.

You will be given a job description and a candidate resume. Return ONLY valid JSON with no \
other text, no markdown, no code fences."""

USER_PROMPT_TEMPLATE = """Evaluate the fit between this job and candidate. \
Return JSON exactly matching this schema:

{{
  "score": <integer 0-100>,
  "reasoning": [
    "<bullet 1: specific skill/experience match or gap>",
    "<bullet 2>",
    "<bullet 3>",
    "<bullet 4 if needed>"
  ],
  "summary": "<1-2 sentence plain-English fit summary>",
  "seniority_assessment": "<entry|mid|senior>",
  "red_flags": ["<any concern that would disqualify, or empty list>"],
  "role_type": "<data_scientist|data_engineer|ml_engineer|analyst|other>"
}}

Scoring guide:
- 90-100: Exceptional match, apply immediately
- 75-89:  Strong match, very likely worth applying
- 60-74:  Reasonable match, some gaps but worth considering
- 40-59:  Partial match, significant gaps
- 0-39:   Poor fit, do not recommend applying

Job Title: {title}
Company: {company}
Location: {location}
Employment Type: {employment_type}

Job Description:
{description}

---

Candidate Resume:
{resume_text}"""


@dataclass
class ClaudeScore:
    score: int
    reasoning: list[str]
    summary: str
    seniority_assessment: str
    red_flags: list[str]
    role_type: str


async def score_job(
    title: str,
    company: str,
    location: str,
    employment_type: str,
    description: str,
    resume_text: str,
) -> Optional[ClaudeScore]:
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = USER_PROMPT_TEMPLATE.format(
        title=title,
        company=company,
        location=location or "Not specified",
        employment_type=employment_type or "Not specified",
        description=(description or "")[:8000],  # cap to avoid huge token costs
        resume_text=resume_text[:4000],
    )

    try:
        # Run sync client in thread to not block the event loop
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        data = json.loads(raw)
        return ClaudeScore(
            score=int(data["score"]),
            reasoning=data.get("reasoning", []),
            summary=data.get("summary", ""),
            seniority_assessment=data.get("seniority_assessment", "unknown"),
            red_flags=data.get("red_flags", []),
            role_type=data.get("role_type", "other"),
        )
    except Exception as e:
        print(f"[claude_matcher] Error scoring {title} @ {company}: {e}")
        return None


async def score_jobs_batch(jobs: list[dict], resume_text: str, concurrency: int = 5) -> list[Optional[ClaudeScore]]:
    """Score multiple jobs concurrently with a semaphore to respect rate limits."""
    sem = asyncio.Semaphore(concurrency)

    async def _score_one(job: dict) -> Optional[ClaudeScore]:
        async with sem:
            return await score_job(
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                employment_type=job.get("employment_type", ""),
                description=job.get("description", ""),
                resume_text=resume_text,
            )

    return await asyncio.gather(*[_score_one(j) for j in jobs])
