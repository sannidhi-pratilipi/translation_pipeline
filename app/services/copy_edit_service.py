from app.llm.gpt_client import complete_gpt

class CopyEditService:
    """
    Copy editing service to polish translated text for language cleanliness.
    
    Uses Gemini to review and improve translated text, ensuring it reads
    naturally in the target language while preserving meaning and tone.
    """
    
    def __init__(self):
        self.prompt_template = open("app/prompts/copy_edit.txt").read()
    
    def clean(self, text: str, target_lang: str) -> str:
        """
        Copy edit translated text to improve language cleanliness and fluency.
        
        Args:
            text: The translated text to polish
            target_lang: Target language name (e.g., "English", "Hindi")
            
        Returns:
            Polished text that reads naturally in the target language
        """
        if not text or not text.strip():
            return ""
        
        # Format the system prompt with target language
        system_prompt = self.prompt_template.format(target_lang=target_lang)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        
        return complete_gpt(
            messages=messages,
            temperature=0.1,
        )
