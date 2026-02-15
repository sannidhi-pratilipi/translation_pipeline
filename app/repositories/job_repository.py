from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from app.models.translation_job import JobStatus, TranslationJob

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class JobEvent:
    at: str
    type: Literal["STATUS", "ERROR", "INFO"]
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class JobRecord:
    job_id: str
    source_lang: str | None = None
    target_lang: str | None = None
    input_path: str | None = None
    output_path: str | None = None

    status: str | None = None
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)

    error: str | None = None
    events: list[JobEvent] = field(default_factory=list)


class JobRepository:
    """
    Tracks translation jobs and their lifecycle.

    Backwards compatible with the previous behavior: `update_status(job_id, status)`
    still prints status changes, but now also records them, validates status values,
    and can optionally persist updates to disk.
    """

    def __init__(
        self,
        persist: bool = True,
        persist_path: str = "data/jobs/jobs.jsonl",
    ):
        self._records: dict[str, JobRecord] = {}
        self._persist = persist
        self._persist_path = Path(persist_path)

    def _persist_event(self, job_id: str, event: JobEvent) -> None:
        if not self._persist:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "job_id": job_id,
            **asdict(event),
        }
        self._persist_path.write_text(
            "", encoding="utf-8"
        ) if not self._persist_path.exists() else None
        with self._persist_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _coerce_status(self, status: str | JobStatus) -> str:
        if isinstance(status, JobStatus):
            return status.value

        status_str = str(status).strip().upper()
        allowed = {s.value for s in JobStatus}
        if status_str not in allowed:
            raise ValueError(
                f"Invalid job status '{status}'. Allowed: {', '.join(sorted(allowed))}"
            )
        return status_str

    def register(self, job: TranslationJob) -> None:
        """Optionally register a job so we can track its metadata."""
        rec = self._records.get(job.job_id) or JobRecord(job_id=job.job_id)
        rec.source_lang = job.source_lang
        rec.target_lang = job.target_lang
        rec.input_path = job.input_path
        rec.output_path = job.output_path
        if rec.status is None:
            rec.status = job.status.value if isinstance(job.status, JobStatus) else str(job.status)
        rec.updated_at = _utc_now_iso()
        self._records[job.job_id] = rec

    def get(self, job_id: str) -> JobRecord | None:
        return self._records.get(job_id)

    def update_status(self, job_id: str, status: str | JobStatus, message: str | None = None):
        """
        Update job status.

        This method is called by the pipeline; it also prints a human-readable line
        for quick CLI feedback.
        """
        new_status = self._coerce_status(status)

        rec = self._records.get(job_id)
        if rec is None:
            rec = JobRecord(job_id=job_id, status=new_status)
            self._records[job_id] = rec
        else:
            rec.status = new_status
            rec.updated_at = _utc_now_iso()

        event = JobEvent(
            at=_utc_now_iso(),
            type="STATUS",
            data={"status": new_status, **({"message": message} if message else {})},
        )
        rec.events.append(event)
        self._persist_event(job_id, event)

        if message:
            print(f"[JOB] {job_id} → {new_status} ({message})")
        else:
            print(f"[JOB] {job_id} → {new_status}")

    def record_error(self, job_id: str, error: Exception | str):
        """Record an error for a job (does not re-raise)."""
        err_str = str(error)
        rec = self._records.get(job_id)
        if rec is None:
            rec = JobRecord(job_id=job_id, status=JobStatus.FAILED.value, error=err_str)
            self._records[job_id] = rec
        else:
            rec.error = err_str
            rec.status = JobStatus.FAILED.value
            rec.updated_at = _utc_now_iso()

        event = JobEvent(at=_utc_now_iso(), type="ERROR", data={"error": err_str})
        rec.events.append(event)
        self._persist_event(job_id, event)
