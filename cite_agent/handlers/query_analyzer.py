"""
Query Analyzer for EnhancedNocturnalAgent
Detects query types and user intent
"""

import re
from typing import Optional


class QueryAnalyzer:
    """
    Analyzes user queries to detect intent and classify query types

    Detects:
    - Simple greetings
    - Casual acknowledgments
    - Test prompts
    - Location queries
    - Language preferences
    - Vague queries that won't benefit from API calls
    """

    def is_simple_greeting(self, text: str) -> bool:
        """Check if text is a simple greeting"""
        greetings = {"hi", "hello", "hey", "greetings", "sup", "yo"}
        words = set(text.lower().strip().split())
        return len(words) <= 2 and bool(words & greetings)

    def is_casual_acknowledgment(self, text: str) -> bool:
        """Check if text is a casual acknowledgment (thanks, ok, etc.)"""
        acks = {
            "thanks", "thank you", "thx", "ty", "ok", "okay", "k", "kk",
            "cool", "nice", "great", "awesome", "perfect", "got it",
            "understood", "roger", "ack", "acknowledged", "bye", "goodbye",
            "see you", "later", "cya", "peace", "cheers"
        }

        # Also check for common phrases
        phrases = {
            "thank you", "thanks!", "thank you!", "ok!", "okay!", "got it!",
            "understood!", "see you!", "see ya", "thanks a lot", "thanks so much",
            "much appreciated", "appreciate it"
        }

        text_lower = text.lower().strip().rstrip('!.')
        words = set(text_lower.split())

        # Check if it's just acknowledgment words
        if len(words) <= 4:
            if words & acks:
                return True
            if text_lower in phrases:
                return True

        return False

    def detect_language_preference(self, text: str) -> Optional[str]:
        """
        Detect if user is expressing language preference

        Returns language code if detected, None otherwise
        """
        # Patterns for language preference
        patterns = {
            'zh': [
                r'用中[文語]', r'說中[文語]', r'中[文語]回[答覆]',
                r'請.*中[文語]', r'我想.*中[文語]'
            ],
            'es': [
                r'en español', r'habla español', r'responde en español',
                r'quiero.*español'
            ],
            'fr': [
                r'en français', r'parle français', r'répond en français',
                r'je veux.*français'
            ],
            'de': [
                r'auf deutsch', r'sprich deutsch', r'antworte auf deutsch',
                r'ich möchte.*deutsch'
            ],
            'ja': [
                r'日本語[でを]', r'日本語.*話',r'日本語.*答'
            ],
            'ko': [
                r'한국어[로를]', r'한국어.*말', r'한국어.*답'
            ]
        }

        text_lower = text.lower()

        for lang, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    return lang

        return None

    def is_generic_test_prompt(self, text: str) -> bool:
        """
        Check if this looks like a generic test prompt
        ("test", "hello", "are you there", etc.)
        """
        test_phrases = {
            "test", "testing", "hello world", "are you there",
            "can you hear me", "ping", "hello?", "hi?",
            "test test", "testing testing", "1 2 3", "123"
        }

        text_clean = text.lower().strip().rstrip('?.!')

        # Exact match for test phrases
        if text_clean in test_phrases:
            return True

        # Single word tests
        if text_clean.split() == ["test"] or text_clean.split() == ["testing"]:
            return True

        return False

    def is_location_query(self, text: str) -> bool:
        """Check if asking about current directory/location"""
        location_patterns = [
            r'^where am i\??$',
            r'^where are we\??$',
            r'^current (directory|folder|location)\??$',
            r'^what.*(directory|folder) (am i|are we) in\??$',
            r'^pwd\??$'
        ]

        text_lower = text.lower().strip()
        return any(re.match(pattern, text_lower) for pattern in location_patterns)

    def is_query_too_vague_for_apis(self, question: str) -> bool:
        """
        Detect if a query is too vague to warrant API calls

        Returns True if query is conversational/vague and shouldn't trigger APIs
        """
        question_lower = question.lower().strip()

        # Too short
        if len(question_lower) < 5:
            return True

        # Common vague phrases
        vague_phrases = [
            "tell me more", "what else", "continue", "go on",
            "explain", "what do you think", "any thoughts",
            "what about", "how about", "interesting", "i see",
            "tell me about it", "what's new", "anything else"
        ]

        if any(phrase in question_lower for phrase in vague_phrases):
            # Only vague if it's JUST these phrases without specific context
            words = question_lower.split()
            if len(words) <= 4:
                return True

        # Questions about the agent itself
        self_referential = [
            "who are you", "what are you", "what can you do",
            "how do you work", "what's your name", "are you ai",
            "are you a bot", "are you real", "can you help"
        ]

        if any(phrase in question_lower for phrase in self_referential):
            return True

        return False
