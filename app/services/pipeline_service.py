class TranslationPipelineService:
    def __init__(
        self,
        pdf_repo,
        job_repo,
        output_repo,
        validation_service,
        chunking_service,
        translation_service,
        copy_edit_service=None,
    ):
        self.pdf_repo = pdf_repo
        self.job_repo = job_repo
        self.output_repo = output_repo
        self.validation = validation_service
        self.chunking = chunking_service
        self.translator = translation_service
        self.copy_editor = copy_edit_service

    def run(self, job):
        try:
            self.validation.validate(job.source_lang, job.target_lang)
            self.job_repo.update_status(job.job_id, "IN_PROGRESS")

            text = self.pdf_repo.load_text(job.input_path)
            chunks = self.chunking.chunk(text)

            translated_chunks = []
            for chunk in chunks:
                translated = self.translator.translate(
                    chunk, job.source_lang, job.target_lang
                )
                if self.copy_editor:
                    translated = self.copy_editor.clean(translated, job.target_lang)
                    
                translated_chunks.append(translated)

            final_text = "\n\n".join(translated_chunks)
            
            # if self.copy_editor:
            #     final_text = self.copy_editor.clean(final_text, job.target_lang)
            
            self.output_repo.save(job.output_path, final_text)

            self.job_repo.update_status(job.job_id, "COMPLETED")

        except Exception as e:
            self.job_repo.update_status(job.job_id, "FAILED")
            raise e
