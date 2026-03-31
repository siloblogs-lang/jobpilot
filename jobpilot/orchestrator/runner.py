##### UPDATE ####
"""
_ Check if the job id is in the google sheets before applying.
_ May be Verify the Apply button text is not Applied before applying

python -c "from jobpilot.orchestrator.runner import JobPilotRunner; JobPilotRunner().run_once(max_results=500)"
"""

from __future__ import annotations
import os, time 
from datetime import datetime, timezone
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
            # ------------------------------------------------------------
            # 1) FILTER OUT JOBS ALREADY IN GOOGLE SHEETS BEFORE SAVE_JOBS
            # ------------------------------------------------------------
            existing_by_id = self.repo.get_existing_jobs_id(provider.NAME)
            
            fresh_jobs: List[JobPosting] = []
            for job in jobs:
                if job.id in existing_by_id:
                    print(f"[Runner] SKIP EXISTING => {job.id}")
                    continue
                # existing = existing_by_id.get(job.id)
                # if existing:
                #     row_idx, row_values = existing
                #     already_applied = self.repo.is_applied_row(provider.NAME, row_values)

                #     if already_applied:
                #         print(f"[Runner] SKIP EXISTING APPLIED => {job.id}")
                #     else:
                #         print(f"[Runner] SKIP EXISTING => {job.id}")

                    # Do not append dupe rows from previous runs
                    # continue

                fresh_jobs.append(job)

            jobs = fresh_jobs
            
            if not jobs:
                print("[Runner] No new jobs to process after existing-sheet filter")
                return []
            
            resume_text = self._load_resume_text()
            matcher = JobMatcher(resume_text=resume_text)

            scored_jobs: List[JobPosting] = []
            # --------------------------------------------------
            # 2) SCORE ONLY NEW JOBS
            # --------------------------------------------------
            for job in jobs:
                desc = provider.get_job_description(job)
                match_result = matcher.top_score(job, desc)

                # Attach match info to metadata for SheetsClient
                md = dict(job.metadata or {})
                md["match_percent"] = match_result.match_percent
                md["recommended"] = match_result.recommended
                md["match_reasons"] = match_result.reasons
                job.metadata = md

                scored_jobs.append(job)

            # ---------------------------------------------------
            # 3) SAVE ONLY NEW JOBS
            # ---------------------------------------------------
            # use repo to select correct sheet and write
            # self.repo.save_jobs(provider.NAME, scored_jobs)
            row_map = self.repo.save_jobs(provider.NAME, scored_jobs)

            # ---------------------------------------------------
            # 4) Decide apply vs skip + record application status
            # ---------------------------------------------------
            for job in scored_jobs:
                match_percent = float(job.metadata.get("match_percent", 0.0))
                recommended = bool(job.metadata.get("recommended", False))
                print(
                    f"[Runner] job={job.id} easy_apply={job.easy_apply} "
                    f"recommended={recommended} match={match_percent}"
                )

                # Default: skipped, log why
                applied = "No"
                notes = f"Only {match_percent}% match. Match score is too low."

                # result = None

                if recommended and job.easy_apply:
                    print(f"[Runner] APPLYING => {job.id} {job.title} | {job.url}")

                    result = provider.apply(job)

                    print(
                        f"[Runner] [APPLY RESULT] job={job.id} "
                        f"status={result.status!r} notes={result.notes!r}"
                    )

                    now_iso = datetime.now(timezone.utc).isoformat()
                    status = (result.status or "").upper()
                    notes_lower = (result.notes or "").lower()

                    # Better applied mapping:
                    # - APPLIED -> Yes
                    # - already applied on Dice -> Yes
                    # - confirmation miss after submit -> blank/uncertain
                    # - everything else -> No
                    if status == "APPLIED":
                        applied = "Yes"
                    elif status == "SKIPPED" and "already applied" in notes_lower:
                        applied = "Yes"
                    elif status == "ERROR" and "confirmation was not detected" in notes_lower:
                        applied = ""
                    else: 
                        applied = "No"

                    notes = result.notes or f"Apply status: {result.status}"

                    print(
                        f"[Runner] [APPLY DECISION] job={job.id} "
                        f"result.status={result.status!r} -> applied={applied!r}"
                    )

                    print(f"Updading sheet for {job.id} applied={applied}")

                    self.repo.update_job_status(
                        job,
                        match_percent=match_percent,
                        applied=applied,
                        applied_at=now_iso if applied == "Yes" else "",
                        notes=notes,
                        row_idx=row_map.get(job.id)
                    )
                    print(f"Updated sheet OK for {job.id}")
                    time.sleep(1.5)
                else: 
                    print(
                        f"[Runner] SKIP => {job.id} recommended={recommended}"
                        f"easy_apply={job.easy_apply}"
                    )
                    reason = []
                    if not recommended:
                        reason.append("match below threshold")
                    if not job.easy_apply:
                        reason.append("Not Easy Apply")
                    notes = "; ".join(reason)

                    print(f"Updating sheet for {job.id} applied={applied}")

                    self.repo.update_job_status(
                        job,
                        match_percent=match_percent,
                        applied="No",
                        notes=notes,
                        row_idx=row_map.get(job.id),
                    )
                    time.sleep(1.5)

                    # Check if the job was applied for
                #     if self.repo.was_already_applied(job.provider, job.id):
                #         print(f"[Runner] SKIP => {job.id} already applied in sheet")
                #         self.repo.update_job_status(
                #             job, 
                #             match_percent=match_percent,
                #             applied="No",
                #             notes="Skipped: job already marked applied in Google Sheets.",
                #             row_idx=row_map.get(job.id)
                #         )
                #         time.sleep(1.5)
                #         continue

                #     print(f"[Runner] APPLYING => {job.id} {job.title} | {job.url}")
                #     # Call provider.apply()
                #     result = provider.apply(job)
                #     # Status update DEBUG
                #     print(
                #         f"[Runner][APPLY RESULT] job={job.id} "
                #         f"status={result.status!r} notes={result.notes!r}"
                #     )
                #     now_iso = datetime.now(timezone.utc).isoformat()
                    
                #     applied = "Yes" if result.status == "APPLIED" else "No"
                #     notes = result.notes or f"Apply status: {result.status}"

                #     # Apply status debug
                #     print(
                #         f"[Runner][APPLY DECISION] job={job.id} "
                #         f"result.status={result.status!r} -> applied={applied!r}"
                #     )

                #     print("Updating sheet for", job.id, "applied=", applied)
                    
                #     self.repo.update_job_status(
                #         job,
                #         match_percent=match_percent,
                #         applied=applied,
                #         applied_at=now_iso if applied == "Yes" else "",
                #         notes=notes,
                #         row_idx=row_map.get(job.id)
                #     )
                #     print("Updated sheet OK for", job.id)
                #     time.sleep(1.5)
                # else:
                #     print(f"[Runner] SKIP => {job.id} recommended={recommended} easy_apply={job.easy_apply}")
                #     # Not recomened (low match %) OR not Easy Apply
                #     reason = []
                #     if not recommended:
                #         reason.append("match below threshold")
                #     if not job.easy_apply:
                #         reason.append("Not Easy Apply")
                #     notes = "; ".join(reason)

                #     print("Updating sheet for", job.id, "applied=", applied)
                #     self.repo.update_job_status(
                #         job, 
                #         match_percent=match_percent,
                #         applied="No",
                #         notes=notes
                #     )
                #     time.sleep(1.5)
            return scored_jobs

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