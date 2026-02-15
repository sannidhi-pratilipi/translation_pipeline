class ValidationService:
    """
    Validates translation language pairs against allowed combinations.
    
    Supported source languages: German, French, Russian
    Supported target languages: English, Hindi
    """
    
    # Dictionary mapping source languages to their allowed target languages
    ALLOWED_TRANSLATIONS = {
        "German": ["English", "Hindi"],
        "French": ["English", "Hindi"],
        "Russian": ["English", "Hindi"],
        "English": ["Hindi"]
    }
    
    def __init__(self):
        # Normalize language names for case-insensitive matching
        self._normalized_source_langs = {
            lang.lower(): lang for lang in self.ALLOWED_TRANSLATIONS.keys()
        }
        self._normalized_target_langs = set()
        for targets in self.ALLOWED_TRANSLATIONS.values():
            for target in targets:
                self._normalized_target_langs.add(target.lower())
    
    def _normalize_lang(self, lang: str) -> str:
        """Normalize language name for comparison (case-insensitive)."""
        return lang.strip().lower()
    
    def validate(self, source_lang: str, target_lang: str):
        """
        Validate that the source and target language pair is allowed.
        
        Args:
            source_lang: Source language name (e.g., "German", "French", "Russian")
            target_lang: Target language name (e.g., "English", "Hindi")
            
        Raises:
            ValueError: If source and target are the same, or if the pair is not allowed
        """
        if source_lang == target_lang:
            raise ValueError(
                f"Source and target language cannot be the same: {source_lang}"
            )
        
        norm_source = self._normalize_lang(source_lang)
        norm_target = self._normalize_lang(target_lang)
        
        # Check if source language is supported
        if norm_source not in self._normalized_source_langs:
            supported_sources = ", ".join(self.ALLOWED_TRANSLATIONS.keys())
            raise ValueError(
                f"Source language '{source_lang}' is not supported. "
                f"Supported source languages: {supported_sources}"
            )
        
        # Get the canonical source language name
        canonical_source = self._normalized_source_langs[norm_source]
        allowed_targets = self.ALLOWED_TRANSLATIONS[canonical_source]
        
        # Check if target language is allowed for this source
        if norm_target not in [self._normalize_lang(t) for t in allowed_targets]:
            raise ValueError(
                f"Translation from '{source_lang}' to '{target_lang}' is not allowed. "
                f"Allowed target languages for {source_lang}: {', '.join(allowed_targets)}"
            )
        
        # Check if target language is supported at all
        if norm_target not in self._normalized_target_langs:
            raise ValueError(
                f"Target language '{target_lang}' is not supported. "
                f"Supported target languages: English, Hindi"
            )
