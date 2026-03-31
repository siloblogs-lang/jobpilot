from __future__ import annotations
from typing import List
from jobpilot.models.job import JobPosting
from jobpilot.storage.sheets import SheetsClient
# from jobpilot.utils.config import load_configs

class JobRepo:
    """
    Currently backed by Google Sheets via SheetsClient, but callers don't
    need to know that. They just say: 'save these jobs for provider X'.
    """
    def __init__(self, client: SheetsClient | None = None):
        self._client = client or SheetsClient()

    def _sheet_name_for_provider(self, provider: str) -> str:
        # return f"{provider.capitalize()} Jobs"
        return self._client.default_sheet_name
    
    def save_jobs(self, provider: str, jobs: List[JobPosting]) -> dict[str, int]:
        """
        Persits a batch of jobs for a provider.

        Right now this just delegates to SheetsClient.append_jobs
        with a provide-specific worksheet name. 
        """
        if not jobs:
            return {}
        
        sheet_name = self._sheet_name_for_provider(provider)
        return self._client.append_jobs(sheet_name, jobs)

    def _find_row_index_by_job_id(self, provider:  str, job_id: str) -> int | None:
        sheet_name = self._sheet_name_for_provider(provider)
        last_match = None
        for row_idx, row_values in self._client.iter_jobs(sheet_name):
            # HEADER: ["id", "provider", "title", ...]
            if not row_values:
                continue
            if row_values[0] == job_id:
                last_match = row_idx
        return last_match
    
    def _get_job_row(self, provider: str, job_id: str) -> tuple[int, list[str]] | None:
        sheet_name = self._sheet_name_for_provider(provider)
        last_match = None

        for row_idx, row_values in self._client.iter_jobs(sheet_name):
            if row_values and row_values[0] == job_id:
                last_match = (row_idx, row_values)

        return last_match

    def get_existing_jobs_id(self, provider: str) -> dict[str, tuple[int, list[str]]]:
        """
        Load all existing jobs for a provider sheet once.
        Returns:
            {
                job_id: (row_idx, row_values),
                ...
            }
        """
        sheet_name = self._sheet_name_for_provider(provider)
        found: dict[str, tuple[int, list[str]]] = {}

        for row_idx, row_values in self._client.iter_jobs(sheet_name):
            if not row_values:
                continue
            job_id = row_values[0]
            if job_id:
                found[job_id] = (row_idx, row_values)

        return found

    def is_applied_row(self, provider: str, row_values: list[str]) -> bool:
        """
        Check whether a row's 'applied' column is Yes
        """
        try:
            headers = self._client.headers_for_sheet(self._sheet_name_for_provider(provider))
            applied_idx = headers.index("applied")
            applied_value = row_values[applied_idx].strip().lower() if len(row_values) > applied_idx else ""
            return applied_value == "yes"
        except Exception as e:
            print(f"[JobRepo.is_applied_row] failed to read applied value: {e}")
            return False

    def was_already_applied(self, provider: str, job_id: str) -> bool:
        found = self._get_job_row(provider, job_id)
        if not found:
            return False
        
        _, row_values = found
        return self.is_applied_row(provider, row_values)
        # row_idx, row_values = found
        # try:
        #     headers = self._client.headers_for_sheet(self._sheet_name_for_provider(provider))
        #     applied_idx = headers.index("applied")
        #     applied_value = row_values[applied_idx].strip().lower() if len(row_values) > applied_idx else ""
        #     print(
        #       f"[JobRepo.was_already_applied] provider={provider} job_id={job_id} "
        #       f"row_idx={row_idx} applied_value={applied_value!r}"  
        #     )
        #     return applied_value == "yes"
        # except Exception as e:
        #     print(f"[JobRepo.was_already_applied] lookup failed for job_id={job_id}: {e}")
        #     return False
        
    def update_job_status(
            self, 
            job: JobPosting,
            match_percent: float | None = None,
            applied: str | None = None,
            applied_at: str | None = None,
            notes: str | None = None,
            row_idx: int | None = None,
    ) -> None:
        sheet_name = self._sheet_name_for_provider(job.provider)

        if row_idx is None:
            row_idx = self._find_row_index_by_job_id(job.provider, job.id)

        if row_idx is None:
            # Row not found; log or skip quitly
            raise RuntimeError(f"Could not find job row in sheet for id={job.id}")
        
        fields: dict[str, str] = {}
        if match_percent is not None:
            fields["match_percent"] = f"{match_percent:.1f}"
        if applied is not None:
            fields["applied"] = applied
        if applied_at is not None:
            fields["applied_at"] = applied_at
        if notes is not None:
            fields["application_status_notes"] = notes

        if fields:
            self._client.update_fields(sheet_name, row_idx, fields)
