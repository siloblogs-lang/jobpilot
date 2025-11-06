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
