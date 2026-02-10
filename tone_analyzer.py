"""Tone analysis and style learning from past weekly documents."""
from typing import List, Dict, Any, Set
import re
from collections import Counter

class ToneAnalyzer:
    """Analyzes past documents to learn writing style and tone."""
    
    def __init__(self):
        """Initialize the tone analyzer."""
        self.common_phrases: Set[str] = set()
        self.enthusiasm_markers: Set[str] = set()
        self.sentence_patterns: List[str] = []
        self.casual_expressions: Set[str] = set()
    
    def analyze_documents(self, documents: List[str]) -> Dict[str, Any]:
        """Analyze a collection of past documents to learn tone and style."""
        all_text = " ".join(documents)
        
        # Extract common phrases (2-4 word phrases)
        phrases = self._extract_phrases(all_text)
        self.common_phrases = set(phrases.most_common(50))
        
        # Identify enthusiasm markers
        self.enthusiasm_markers = self._extract_enthusiasm_markers(all_text)
        
        # Extract sentence patterns
        self.sentence_patterns = self._extract_sentence_patterns(documents)
        
        # Identify casual expressions
        self.casual_expressions = self._extract_casual_expressions(all_text)
        
        return {
            "common_phrases": list(self.common_phrases),
            "enthusiasm_markers": list(self.enthusiasm_markers),
            "sentence_patterns": self.sentence_patterns,
            "casual_expressions": list(self.casual_expressions)
        }
    
    def _extract_phrases(self, text: str) -> Counter:
        """Extract common 2-4 word phrases."""
        words = text.lower().split()
        phrases = []
        
        for i in range(len(words) - 1):
            # 2-word phrases
            phrases.append(f"{words[i]} {words[i+1]}")
            if i < len(words) - 2:
                # 3-word phrases
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
                if i < len(words) - 3:
                    # 4-word phrases
                    phrases.append(f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}")
        
        return Counter(phrases)
    
    def _extract_enthusiasm_markers(self, text: str) -> Set[str]:
        """Extract enthusiasm markers from text."""
        markers = {
            "super psyched", "crushing it", "lfg", "killing the game",
            "huge", "awesome", "excited", "pumped", "psyched",
            "crushed", "killed", "nailed", "rocked"
        }
        
        found_markers = set()
        text_lower = text.lower()
        
        for marker in markers:
            if marker in text_lower:
                found_markers.add(marker)
        
        return found_markers
    
    def _extract_sentence_patterns(self, documents: List[str]) -> List[str]:
        """Extract common sentence structure patterns."""
        patterns = []
        
        for doc in documents:
            sentences = re.split(r'[.!?]+', doc)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10 and len(sentence) < 200:
                    # Extract pattern (simplified - look for common structures)
                    if sentence.startswith("*"):
                        patterns.append("bullet_point")
                    elif ":" in sentence and sentence.count(":") == 1:
                        patterns.append("colon_separated")
                    elif sentence.startswith(("I", "We", "The", "This")):
                        patterns.append("subject_start")
        
        return list(set(patterns))
    
    def _extract_casual_expressions(self, text: str) -> Set[str]:
        """Extract casual expressions and contractions."""
        casual = {
            "imo", "tbh", "fwiw", "imo", "ngl", "tbf",
            "don't", "won't", "can't", "it's", "we're", "they're",
            "gonna", "wanna", "gotta"
        }
        
        found = set()
        text_lower = text.lower()
        
        for expr in casual:
            if expr in text_lower:
                found.add(expr)
        
        return found
    
    def apply_tone(self, content: str, section_type: str) -> str:
        """Apply learned tone to content based on section type."""
        # For Highlights: concise, positive
        if section_type == "highlights":
            return self._make_concise_and_positive(content)
        
        # For This Week: casual, enthusiastic
        elif section_type == "this_week":
            return self._add_enthusiasm(content)
        
        # For Next Week: action-oriented
        elif section_type == "next_week":
            return self._make_action_oriented(content)
        
        return content
    
    def _make_concise_and_positive(self, content: str) -> str:
        """Make content concise and positive."""
        # Remove unnecessary words, keep it brief
        # This is a simplified version
        sentences = content.split(". ")
        concise = []
        
        for sentence in sentences[:5]:  # Limit to 5 sentences
            sentence = sentence.strip()
            if sentence:
                concise.append(sentence)
        
        return ". ".join(concise)
    
    def _add_enthusiasm(self, content: str) -> str:
        """Add enthusiasm markers where appropriate."""
        # Don't overdo it - just ensure positive tone
        # This is a simplified version
        return content
    
    def _make_action_oriented(self, content: str) -> str:
        """Make content action-oriented."""
        # Ensure sentences start with action verbs where possible
        # This is a simplified version
        return content
