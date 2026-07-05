from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressEvent:
    job_id: int
    percent: Optional[str]
    speed: str
    eta: str
    downloaded: str
