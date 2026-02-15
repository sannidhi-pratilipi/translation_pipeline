from app.llm.gpt_client import complete_gpt

class TranslationService:
    def __init__(self):
        self.system_prompt_template = open("app/prompts/translation.txt").read()

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        if not text or not text.strip():
            return ""

        system_prompt = self.system_prompt_template.format(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # Provide the raw chunk as the user message so the model focuses
        # on translating *only* this text.
        messages = [
            {"role": "system", "content": "You are a professional literary translator.Preserve meaning, tone, tense, names, and structure exactly.Do not add or omit content.Maintain paragraph and line breaks exactly.Output only the translated text"},
            {"role": "user", "content": system_prompt},
        ]

        return complete_gpt(
            messages=messages,
            temperature=0.3,
        )
