import uuid
from pathlib import Path

from app.models.translation_job import TranslationJob, JobStatus

from app.repositories.pdf_repository import PDFRepository
from app.repositories.job_repository import JobRepository
from app.repositories.output_repository import OutputRepository

from app.services.validation_service import ValidationService
from app.services.chunking_service import ChunkingService
from app.services.translation_service import TranslationService
from app.services.copy_edit_service import CopyEditService
from app.services.pipeline_service import TranslationPipelineService

def build_pipeline() -> TranslationPipelineService:
    return TranslationPipelineService(
        pdf_repo=PDFRepository(),
        job_repo=JobRepository(),
        output_repo=OutputRepository(),
        validation_service=ValidationService(),
        chunking_service=ChunkingService(),
        translation_service=TranslationService(),
        copy_edit_service=CopyEditService(),
    )

def run_job(
    pipeline: TranslationPipelineService,
    input_pdf: str,
    source_lang: str,
    target_lang: str,
):
    input_path = Path("data/input") / input_pdf
    print(f"Running job for {input_path} → {target_lang}")
    output_path = Path(
        "data/output",
        f"{input_path.stem}_{target_lang.lower()}.txt"
    )

    job = TranslationJob(
        job_id=str(uuid.uuid4()),
        source_lang=source_lang,
        target_lang=target_lang,
        status=JobStatus.PENDING,
        input_path=str(input_path),
        output_path=str(output_path),
    )
    pipeline.run(job)

def main():
    pipeline = build_pipeline()

    jobs = [
        {
            "input_pdf": "Dostoevsky - Chapter 1 (English).pdf",
            "source_lang": "English",
            "target_langs": ["Hindi"],
        },
    ]

    for job_cfg in jobs:
        for target_lang in job_cfg["target_langs"]:
            run_job(
                pipeline=pipeline,
                input_pdf=job_cfg["input_pdf"],
                source_lang=job_cfg["source_lang"],
                target_lang=target_lang,
            )

if __name__ == "__main__":
    main()
