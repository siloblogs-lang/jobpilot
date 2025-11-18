from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import re, os, json
from jobpilot.models.job import JobPosting

# OpenAI import 
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None # Graceful fallback on your installed client version

@dataclass
class JobMatchResult:
    job_id: str
    provider: str
    match_percent: float
    recommended: bool
    reasons: str

class JobMatcher:
    """
    Job/resume matcher.

    Uses: 
    - naive keyword-overlap heuristic
    - LLM scoring via OpenAI

    Public API:
    - top-scrore(job, description) -> JobMatchResult 
    """

    def __init__(
            self, 
            resume_text: str, 
            threshold: float = 0.60,
            use_llm: bool = True,
    ) -> None:
        
        self.resume_text = resume_text or ""
        self.threshold = threshold
        
        self.use_llm = use_llm
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = None
        if self.api_key and OpenAI is not None and self.use_llm:
            # Only create client if key is present and library is installed
            self.client = OpenAI(api_key=self.api_key)
        
        # Pre-tokenize resume once; reruse for evry job.
        self._resume_words = self._tokenize(self.resume_text)

    def _tokenize(self, text: str) -> set[str]:
        """
        Turn text into a set of lowercase word tokens.
        """
        words = re.findall(r"\w+", text.lower())
        return set(words)
    
    def _score_naive(self, job: JobPosting, description: str) -> Dict[str, Any]:
        """
        Fallback heuristic: keyword overlap between resume and job descrioption.
        """
        resume_text = (self.resume_text or "").lower()
        desc_text = (description or "").lower()

        # Very dumb tokenization: split on whitespace
        # Can be replaced by other more advanced methods like SBERT
        resume_tokens = set(resume_text.split())
        desc_tokens = set(desc_text.split())

        if not resume_tokens or not desc_tokens:
            return JobMatchResult(
                job_id=job.id,
                provider=job.provider,
                match_percent=0.0,
                recommended=False,
                reasons="Missing text of resume or job description"
            )
        
        shared = resume_tokens & desc_tokens

        overlap_ratio = len(shared) / max(1, len(resume_tokens))
        match_percent = round(overlap_ratio * 100, 1)
        recommended = match_percent >= 60.0

        reasons = (
            f"Naive keyword overlap: {len(shared)} shared unque terms between "
            f"resume and job description; approx {match_percent}% match." 
        )

        return JobMatchResult(
            job_id=job.id,
            provider=job.provider,
            match_percent=match_percent,
            recommended=recommended,
            reasons=reasons,
        )
    
    def _score_with_llm(self, job: JobPosting, description: str) -> Dict[str, Any]:
        """
        Use an OpenAI model to score job vs resume.

        Returens a JobMatchResult.
        Falls back to naive scoring if anything goes wrong.
        """
        if not self.client:
            # Safely fallback if client not available
            return self._score_naive(job, description)
        
        # Basic safety: truncate very long texts to avoid token blow-up
        desc_text = (description or "").strip()
        resume_text = (self.resume_text or "").strip()

        if not desc_text or not resume_text:
            return self._score_naive(job, description)

        model_name = os.getenv("JOBPILOT_MATCH_MODEL", "gpt-4.1-mini")

        system_msg = (
            "You are an expert technical recruiter. "
            "Given a candidate's resume and a job description, you must evaluate "
            "how strong the match is. Return ONLY valid JSON with keys: "
            "match_percent (float 0-100), recommended (boolean, true if >=60%), "
            "reasons (short explanation string)."
        )

        user_msg = f"""
            Job Posting:
            - Provider: {job.provider}
            - Title: {job.title}
            - Company: {job.company or "Unknown"}
            - Location: {job.location or "Unknown"}
            - URL: {job.url}

            Job Description:
            \"\"\"{desc_text[:8000]}\"\"\"

            Candidate Resume:
            \"\"\"{resume_text[:8000]}\"\"\"

            Instructions:
            1. Analyze how well the candidate fits the role, considering skills, tech stack, years of experience, domain knowledge, and responsibilities.
            2. Return ONLY JSON, no extra text.
            3. JSON format:

            {{
            "match_percent": 0-100 as float,
            "recommended": true or false,
            "reasons": "short explanation"
            }}
            """
        
        try: 
            resp = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1,
            )

            raw = resp.choices[0].message.content.strip()
            data = json.loads(raw)

            match_percent = float(data.get("match_percent", 0.0))
            recommended = bool(data.get("recommended", match_percent >= 60.0))
            reasons = str(data.get("reasons", "")) or "No reasons returned by the model."

            # Clamp match_percent to [0, 100] just in case
            match_percent = max(0.0, min(100.0, match_percent))

            return JobMatchResult(
                job_id=job.id,
                provider=job.provider,
                match_percent=match_percent,
                recommended=recommended,
                reasons=reasons,
            )

        except Exception as e:
            # If anything blows up (bad JSON , etc.) -> fallback to naive
            fallback = self._score_naive(job, description)
            fallback.reasons += f"[FALLBACK: LLM scoring failed: {e}]"
            return fallback

    def top_score(self, job:JobPosting, description: str) -> Dict[str, Any]:

        """
        Get both scores llm and naive and return to score
        """

        naive_score = self._score_naive(job, description)
        llm_score = self._score_with_llm(job, description)

        if naive_score.match_percent > llm_score.match_percent:
            return naive_score
        else:
            return llm_score

    # The set up is using top_score method instead of this.
    def score(self, job: JobPosting, description: str) -> JobMatchResult:
        """
        Compute a naive match score between the resume and this job.

        Returns:
            JobMatchResult with:
            - match_percent    : 0–100 float
            - recommended      : True if >= threshold
            - reasons          : simple explanation
        """

        description = description or ""
        job_title = job.title or ""
        job_company = job.company or ""

        combined = f"{job_title}\n{job_company}\n{description}"
        job_words = self._tokenize(combined)

        if not job_words:
            match_percent = 0.0
            recomended = False
            reasons = "Job description appears empty; cannot compute overlap."

        else:
            overlap = self._resume_words & job_words
            overlap_ration = len(overlap) / max(len(job_words), 1)

            # Slightly amplify so its not always tiny numbers
            raw_score = overlap_ration * 100 * 1.5
            match_percent = max(0.0, min(100.0, raw_score))
            recomended = match_percent >= (self.threshold * 100.0)

            reasons = (
                f"Naive keyword overlap: {len(overlap)} shared unique terms "
                f"between resume and job description; approx "
                f"{match_percent:.1f}% match."
            )

            return JobMatchResult(
                job_id=job.id,
                provider=job.provider,
                match_percent=round(match_percent, 1),
                recommended=recomended,
                reasons=reasons,
            )