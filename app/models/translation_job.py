from dataclasses import dataclass
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class TranslationJob:
    job_id: str
    source_lang: str
    target_lang: str
    status: JobStatus
    input_path: str
    output_path: str
