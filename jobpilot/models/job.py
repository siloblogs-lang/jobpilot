from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class JobPosting:
    id: str
    title: str
    company: str
    location: str
    url: str
    provider: str
    easy_apply: bool
    metadata: Dict[str, str]

@dataclass
class ApplyResult:
    status: str            # "APPLIED"|"SKIPPED"|"ERROR"
    app_id: Optional[str]
    notes: Optional[str]
