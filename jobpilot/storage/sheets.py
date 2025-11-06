from __future__ import annotations

import json, os, gspread
from dataclasses import asdict
from datetime import datetime, timezone
from typing import List

from google.oauth2.service_account import Credentials

from jobpilot.models.job import JobPosting
from jobpilot.utils.config import load_configs

HEADERS = [
    "id",
    "provider",
    "title",
    "company",
    "location",
    "job_url",
    "easy_apply",
    "created_at",
    "match_percent",
    "applied",
    "applied_at",
    "application_status_notes",
    "raw_metadata",
]

# Authentication helper
def _load_service_account_credentials(sa_json_path: str) -> Credentials:
    """ Load service account credentials for Google API
    Request inly Sheets & Drive scopes (Drive is needed to open by name)
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    return Credentials.from_service_account_file(sa_json_path, scopes=scopes)


class SheetsClient:
    def __init__(
            self,
            sa_json_path: str | None = None,
            spreadsheet_name: str | None = None
        ) -> None:
        """
        SheetsClient knows how to connect to a single Google Spreadsheet
        and operate on its worksheets.

        If args are omitted, it falls back to configs/env:
        - GOOGLE_SA_JSON
        - SHEETS_SPREADSHEET_NAME
        """
        cfg = load_configs()
        env_cfg = cfg.get("env", {})

        sa_json_path = sa_json_path or env_cfg.get("GOOGLE_SA_JSON")
        if not sa_json_path:
            raise ValueError("GOOGLE_SA_JSON is not set. Please configure service account JSON path.")
        
        if not os.path.exists(sa_json_path):
            raise FileNotFoundError(f"Service account JSON not found at: {sa_json_path}")
        
        spreadsheet_name = spreadsheet_name or env_cfg.get("SHEETS_SPREADSHEET_NAME", "JobPilot")

        # if not sa_json_path:
        #     raise ValueError("GOOGLE_SA_JSON is not set. Please configure service account JSON path.")
        
        self._spreadsheet_name = spreadsheet_name
        creds = _load_service_account_credentials(sa_json_path=sa_json_path)
        self._gc = gspread.authorize(creds)
        self._spreadsheet = self._get_spreadsheet()

    def _get_spreadsheet(self):
        """ Open spreadsheet by name, or create it if it doesn't exist"""
        try:
            return self._gc.open(self._spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            return self._gc.create(self._spreadsheet_name)
        
    def ensure_sheet_exists(self, sheet_name: str):
        """
        Ensure there's a worksheet with the given name and correct HEADERS.
        If it doesn't exist, create it and set headers in the first row.
        """
        try: 
            ws = self._spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            ws = self._spreadsheet.add_worksheet(
                title=sheet_name, 
                rows="1000",
                cols=str(len(HEADERS)))
            ws.append_row(HEADERS)
            return ws
        
        # if worksheet exists verify headers 
        existing = ws.row_values(1)
        if existing != HEADERS:
            # You can choose to:
            # - raise 
            # - log a warning
            # For now we will be strict so schema drifts don't silently break stuff
            raise ValueError(
                f"Worksheet '{sheet_name}' exists but headers differ\n"
                f"Expected: {HEADERS}\nGot: {existing}"
            )
        return ws

    @staticmethod
    def _job_to_row(job: JobPosting, created_at: datetime | None = None) -> list:
        """Flatten a JobPosting into a row  matching HEADERS orders."""
        created_at = created_at or datetime.now(timezone.utc)
        created_iso = created_at.isoformat()

        # Normalizing location into empty string in None.
        location = job.location or (job.metadata.get("location") if job.metadata else "")
        raw_metadata = json.dumps(job.metadata or {}, ensure_ascii=False)

        # Match HEADERS:
        return [
            job.id,
            job.provider,
            job.title,
            job.company,
            location,
            job.url,
            job.easy_apply,
            created_iso,
            "",          # match_percent (empty for now)
            "",          # applied
            "",          # applied_at
            "",          # application_status_notes
            raw_metadata,
        ]
    
    def append_jobs(self, sheet_name: str, jobs: List[JobPosting]) -> None:
        """
        Append a list of JobPosting objects as rows to the given worksheet.

        This does NOT deduplicate; it simply appends. Dedup logic has to be layered
        on top (e.g., via a repo or a later clean-up job).
        """
        if not jobs:
            return
        
        ws = self.ensure_sheet_exists(sheet_name)
        created_at = datetime.now(timezone.utc)
        rows = [self._job_to_row(job, created_at) for job in jobs]

        # gspread's append_rows is efficiant for batch inserts
        ws.append_rows(rows, value_input_option="USER_ENTERED")