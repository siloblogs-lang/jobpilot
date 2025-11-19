from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List

from jobpilot.providers.base import BaseProvider
from jobpilot.models.job import JobPosting
from jobpilot.storage.sheets import SheetsClient

from jobpilot.storage.repo import JobRepo
from jobpilot.services.matcher import JobMatcher
from jobpilot.providers.dice.provider import DiceProvider
from jobpilot.utils.config import load_configs
from jobpilot.browser.engine import build_driver

@dataclass
class JobPilotRunner:
    """
    Minimal orchestrator for a single 'discovery + log to Sheets' cycle.

    Responsibilities (for now):
    - Use a provider to login and search for jobs
    - Append discovered jobs to a Google Sheet
    - Return the list of JobPosting objects for further processing
    """
    def __init__(self, provider_name: str = "dice") -> None:
        self.cfg = load_configs()
        self.provider_name = provider_name
        self.repo = JobRepo()

    def _load_resume_text(self) -> str:
        profile = self.cfg.get("profile", {})
        # print(f"[Profile from YAML] => {profile}")
        env_cfg = self.cfg.get("env", {})

        key_or_path = profile.get("resume_path")

        if not key_or_path:
            raise RuntimeError("profile.resume_path is not set")
        
        resolved = env_cfg.get(key_or_path) or os.getenv(key_or_path)
        resume_path = resolved or key_or_path

        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume file is not fond at: {resume_path}")
        
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()

    # provider: BaseProvider
    # sheets: SheetsClient
    # jobs_sheet_name: str = "jobs" # Change the default to whatevr is used

    def run_once(self, max_results: int = 10) -> List[JobPosting]:
        """
        Single-shot run:
        1) Login with provider
        2) Search for jobs (respecting max_results)
        3) Append them to Sheets
        4) Return the list of JobPosting objects
        """
        driver = build_driver(headless=False)
        try: 
            provider = DiceProvider(driver, self.cfg)
            print("[Runner] Starting run_once")
            provider.login()

            jobs = provider.search(max_results=max_results)

            resume_text = self._load_resume_text()
            matcher = JobMatcher(resume_text=resume_text)

            score_jobs: List[JobPosting] = []

            for job in jobs:
                desc = provider.get_job_description(job)
                match_result = matcher.top_score(job, desc)

                # Attach match info to metadata for SheetsClient
                md = dict(job.metadata or {})
                md["match_percent"] = match_result.match_percent
                md["recommended"] = match_result.recommended
                md["match_reasons"] = match_result.reasons
                job.metadata = md

                score_jobs.append(job)

            # use repo to select correct sheet and write
            self.repo.save_jobs(provider.NAME, score_jobs)

            return score_jobs

        finally:
            driver.quit()    
        # print("[Runner] Starting run_once")
        # # 1. Login
        # provider.login()
        # print("[Runner] Login OK")

        # # 2. Run provider search
        # jobs = list(self.provider.search(max_results=max_results))
        # print(f"[Runner] Provider.search() returned {len(jobs)} jobs")
        # if not jobs:
        #     # Nothing to log just return
        #     print("[Runner] No jobs returned ; nothing to append")
        #     return []
        
        # print(
        #     f"[Runner] About to append {len(jobs)} jobs "
        #     f"to sheet '{self.jobs_sheet_name}'"
        # )
        
        # # 3. Make sure target sheet exists, then appnd jobs
        # self.sheets.ensure_sheet_exists(self.jobs_sheet_name)
        # self.sheets.append_jobs(self.jobs_sheet_name, jobs)
        # print("[Runner] append_job() completed")

        # # 4. Return the list for any further scripts to use
        # return jobs