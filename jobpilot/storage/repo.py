from __future__ import annotations
from typing import List
from jobpilot.models.job import JobPosting
from jobpilot.storage.sheets import SheetsClient

class JobRepo:
    """
    Currently backed by Google Sheets via SheetsClient, but callers don't
    need to know that. They just say: 'save these jobs for provider X'.
    """
    def __init__(self, client: SheetsClient | None = None):
        self._client = client or SheetsClient()

    def _sheet_name_for_provider(self, provider: str) -> str:
        return f"{provider.capitalize()} Jobs"
    
    def save_jobs(self, provider: str, jobs: List[JobPosting]) -> None:
        """
        Persits a batch of jobs for a provider.

        Right now this just delegates to SheetsClient.append_jobs
        with a provide-specific worksheet name. 
        """
        if not jobs:
            return
        
        sheet_name = self._sheet_name_for_provider(provider)
        self._client.append_jobs(sheet_name, jobs)

    def _find_row_index_by_job_id(self, provider:  str, job_id: str) -> int | None:
        sheet_name = self._sheet_name_for_provider(provider)
        for row_idx, row_values in self._client.iter_jobs(sheet_name):
            # HEADER: ["id", "provider", "title", ...]
            if not row_values:
                continue
            if row_values[0] == job_id:
                return row_idx
        return None
    
    def update_job_status(
            self, 
            job: JobPosting,
            match_percent: float | None = None,
            applied: str | None = None,
            applied_at: str | None = None,
            notes: str | None = None,
    ) -> None:
        sheet_name = self._sheet_name_for_provider(job.provider)
        row_idx = self._find_row_index_by_job_id(job.provider, job.id)
        if row_idx is None:
            # Row not found; log or skip quitly
            return
        
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
