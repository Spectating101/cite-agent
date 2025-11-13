"""
Query Analyzer for EnhancedNocturnalAgent
Detects query types and user intent
"""

import re
from typing import Optional, Dict, Any, List


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
        Enhanced with pattern matching for multi-year queries, market share, comparisons
        """
        question_lower = question.lower().strip()

        # Too short
        if len(question_lower) < 5:
            return True

        # Pattern 1: Multiple years without SPECIFIC topic (e.g., "2008, 2015, 2019")
        years_pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(years_pattern, question)
        if len(years) >= 2:
            # Multiple years - check if there's a SPECIFIC topic beyond just "papers on"
            # Generic terms that don't add specificity
            generic_terms = ['papers', 'about', 'on', 'regarding', 'concerning', 'related to']
            # Remove generic terms and check what's left
            words = question_lower.split()
            content_words = [w for w in words if w not in generic_terms and not re.match(r'\d{4}', w)]
            # If fewer than 2 meaningful content words, it's too vague
            if len(content_words) < 2:
                return True  # Too vague: "papers on 2008, 2015, 2019" needs topic

        # Pattern 2: Market share without market specified
        if 'market share' in question_lower:
            market_indicators = ['analytics', 'software', 'government', 'data', 'cloud', 'sector', 'industry']
            if not any(indicator in question_lower for indicator in market_indicators):
                return True  # Too vague: needs market specification

        # Pattern 3: Comparison without metric (compare X and Y)
        if any(word in question_lower for word in ['compare', 'versus', 'vs', 'vs.']):
            metric_indicators = ['revenue', 'market cap', 'sales', 'growth', 'profit', 'valuation']
            if not any(indicator in question_lower for indicator in metric_indicators):
                return True  # Too vague: needs metric specification

        # Pattern 4: Ultra-short queries without specifics (< 4 words)
        word_count = len(question.split())
        if word_count <= 3 and '?' in question:
            return True  # Too short and questioning - likely needs clarification

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

    async def analyze_request_type(self, question: str) -> Dict[str, Any]:
        """
        Analyze what type of request this is and what APIs to use

        Returns:
            Dict with:
                - type: Request type (financial, research, system, comprehensive, general)
                - apis: List of APIs to use (finsight, archive, shell)
                - confidence: Confidence score (0.0-1.0)
                - analysis_mode: Analysis mode (qualitative, quantitative, mixed)
        """
        # Financial indicators - COMPREHENSIVE list to ensure FinSight is used
        financial_keywords = [
            # Core metrics
            'financial', 'revenue', 'sales', 'income', 'profit', 'earnings', 'loss',
            'net income', 'operating income', 'gross profit', 'ebitda', 'ebit',

            # Margins & Ratios
            'margin', 'gross margin', 'profit margin', 'operating margin', 'net margin', 'ebitda margin',
            'ratio', 'current ratio', 'quick ratio', 'debt ratio', 'pe ratio', 'p/e',
            'roe', 'roa', 'roic', 'roce', 'eps',

            # Balance Sheet
            'assets', 'liabilities', 'equity', 'debt', 'cash', 'capital',
            'balance sheet', 'total assets', 'current assets', 'fixed assets',
            'shareholders equity', 'stockholders equity', 'retained earnings',

            # Cash Flow
            'cash flow', 'fcf', 'free cash flow', 'operating cash flow',
            'cfo', 'cfi', 'cff', 'capex', 'capital expenditure',

            # Market Metrics
            'stock', 'market cap', 'market capitalization', 'enterprise value',
            'valuation', 'price', 'share price', 'stock price', 'quote',
            'volume', 'trading volume', 'shares outstanding',

            # Financial Statements
            'income statement', '10-k', '10-q', '8-k', 'filing', 'sec filing',
            'quarterly', 'annual report', 'earnings report', 'financial statement',

            # Company Info
            'ticker', 'company', 'corporation', 'ceo', 'earnings call',
            'dividend', 'dividend yield', 'payout ratio',

            # Growth & Performance
            'growth', 'yoy', 'year over year', 'qoq', 'quarter over quarter',
            'cagr', 'trend', 'performance', 'returns'
        ]

        # Research indicators (quantitative)
        research_keywords = [
            'research', 'paper', 'study', 'academic', 'literature', 'journal',
            'synthesis', 'findings', 'methodology', 'abstract', 'citation',
            'author', 'publication', 'peer review', 'scientific'
        ]

        # Qualitative indicators (NEW)
        qualitative_keywords = [
            'theme', 'themes', 'thematic', 'code', 'coding', 'qualitative',
            'interview', 'interviews', 'transcript', 'case study', 'narrative',
            'discourse', 'content analysis', 'quote', 'quotes', 'excerpt',
            'participant', 'respondent', 'informant', 'ethnography',
            'grounded theory', 'phenomenology', 'what do people say',
            'how do participants', 'sentiment', 'perception', 'experience',
            'lived experience', 'meaning', 'interpret', 'understand',
            'focus group', 'observation', 'field notes', 'memoir', 'diary'
        ]

        # Quantitative indicators (explicit stats/math)
        quantitative_keywords = [
            'calculate', 'average', 'mean', 'median', 'percentage', 'correlation',
            'regression', 'statistical', 'significance', 'p-value', 'variance',
            'standard deviation', 'trend', 'forecast', 'model', 'predict',
            'rate of', 'ratio', 'growth rate', 'change in', 'compared to'
        ]

        # System/technical indicators
        system_keywords = [
            'file', 'files', 'directory', 'directories', 'folder', 'folders',
            'command', 'run', 'execute', 'install',
            'python', 'code', 'script', 'scripts', 'program', 'system', 'terminal',
            'find', 'search for', 'locate', 'list', 'show me', 'where is',
            'what files', 'which files', 'how many files',
            'grep', 'search', 'look for', 'count',
            '.py', '.txt', '.js', '.java', '.cpp', '.c', '.h',
            'function', 'class', 'definition', 'route', 'endpoint',
            'codebase', 'project structure', 'source code'
        ]

        question_lower = question.lower()

        matched_types: List[str] = []
        apis_to_use: List[str] = []
        analysis_mode = "quantitative"  # default

        # Context-aware keyword detection
        # Strong quant contexts that override everything
        strong_quant_contexts = [
            'algorithm', 'park', 'system', 'database',
            'calculate', 'predict', 'forecast', 'ratio', 'percentage'
        ]

        # Measurement words (can indicate mixed when combined with qual words)
        measurement_words = ['score', 'metric', 'rating', 'measure', 'index']

        has_strong_quant_context = any(ctx in question_lower for ctx in strong_quant_contexts)
        has_measurement = any(mw in question_lower for mw in measurement_words)

        # Special cases: Certain qual words + measurement = mixed (subjective + quantified)
        # BUT: Only if NOT in a strong quant context (algorithm overrides)
        mixed_indicators = [
            'experience',  # user experience
            'sentiment',   # sentiment analysis
            'perception',  # perception
        ]

        is_mixed_method = False
        if not has_strong_quant_context and has_measurement:
            if any(indicator in question_lower for indicator in mixed_indicators):
                is_mixed_method = True

        # Check for qualitative vs quantitative keywords
        qual_score = sum(1 for kw in qualitative_keywords if kw in question_lower)
        quant_score = sum(1 for kw in quantitative_keywords if kw in question_lower)

        # Financial queries are quantitative by nature (unless explicitly qualitative like "interview")
        has_financial = any(kw in question_lower for kw in financial_keywords)
        if has_financial and qual_score == 1:
            # Single qual keyword + financial = probably mixed
            # e.g., "Interview CEO about earnings" = interview (qual) + earnings/CEO (financial)
            quant_score += 1

        # Adjust for context
        if has_strong_quant_context:
            # Reduce qualitative score if in strong quantitative context
            # e.g., "theme park" or "sentiment analysis algorithm"
            qual_score = max(0, qual_score - 1)

        # Improved mixed detection: use ratio instead of simple comparison
        if is_mixed_method:
            # Special case: qual word + measurement = always mixed
            analysis_mode = "mixed"
        elif qual_score >= 2 and quant_score >= 1:
            # Clear mixed: multiple qual + some quant
            analysis_mode = "mixed"
        elif qual_score > quant_score and qual_score > 0:
            # Predominantly qualitative
            analysis_mode = "qualitative"
        elif qual_score > 0 and quant_score > 0:
            # Some of both - default to mixed
            analysis_mode = "mixed"

        if any(keyword in question_lower for keyword in financial_keywords):
            matched_types.append("financial")
            apis_to_use.append("finsight")

        if any(keyword in question_lower for keyword in research_keywords):
            matched_types.append("research")
            apis_to_use.append("archive")

        # Qualitative queries often involve research
        if analysis_mode in ("qualitative", "mixed") and "research" not in matched_types:
            matched_types.append("research")
            if "archive" not in apis_to_use:
                apis_to_use.append("archive")

        if any(keyword in question_lower for keyword in system_keywords):
            matched_types.append("system")
            apis_to_use.append("shell")

        # Deduplicate while preserving order
        apis_to_use = list(dict.fromkeys(apis_to_use))
        unique_types = list(dict.fromkeys(matched_types))

        if not unique_types:
            request_type = "general"
        elif len(unique_types) == 1:
            request_type = unique_types[0]
        elif {"financial", "research"}.issubset(set(unique_types)):
            request_type = "comprehensive"
            if "system" in unique_types:
                request_type += "+system"
        else:
            request_type = "+".join(unique_types)

        confidence = 0.8 if apis_to_use else 0.5
        if len(unique_types) > 1:
            confidence = 0.85

        return {
            "type": request_type,
            "apis": apis_to_use,
            "confidence": confidence,
            "analysis_mode": analysis_mode  # qualitative, quantitative, or mixed
        }
