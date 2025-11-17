#!/usr/bin/env python3
"""
Citation Verification Module for Cite Agent
Verifies that citations are real, DOIs resolve, and papers exist.

Provides:
- DOI resolution and validation
- CrossRef API integration for paper metadata
- Citation format verification
- Paper existence checks
"""

import re
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import time


@dataclass
class VerificationResult:
    """Result of citation verification"""
    valid: bool
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    verification_method: str = "unknown"
    confidence: float = 0.0


class CitationVerifier:
    """
    Verifies citations using DOI resolution and CrossRef API.
    """

    # DOI regex pattern
    DOI_PATTERN = re.compile(r'10\.\d{4,}/[^\s]+')

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cite_agent" / "verification_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

        # Rate limiting
        self._last_request_time = 0.0
        self._min_request_interval = 1.0  # 1 second between requests

    def extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text"""
        match = self.DOI_PATTERN.search(text)
        if match:
            doi = match.group(0)
            # Clean up trailing punctuation
            doi = doi.rstrip('.,;:)')
            return doi
        return None

    def extract_all_dois(self, text: str) -> List[str]:
        """Extract all DOIs from text"""
        matches = self.DOI_PATTERN.findall(text)
        # Clean up each DOI
        return [doi.rstrip('.,;:)') for doi in matches]

    async def verify_doi(self, doi: str) -> VerificationResult:
        """
        Verify a DOI by resolving it through CrossRef.

        Uses https://api.crossref.org/works/{doi}
        """
        # Check cache first
        if doi in self._cache:
            cached = self._cache[doi]
            return VerificationResult(**cached)

        # Rate limiting
        await self._rate_limit()

        try:
            import aiohttp

            url = f"https://api.crossref.org/works/{doi}"
            headers = {
                "User-Agent": "CiteAgent/1.4.8 (https://github.com/Spectating101/cite-agent; mailto:contact@citeagent.dev)"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        work = data.get("message", {})

                        # Extract metadata
                        title = work.get("title", ["Unknown"])[0] if work.get("title") else "Unknown"

                        # Authors
                        authors_list = []
                        for author in work.get("author", []):
                            given = author.get("given", "")
                            family = author.get("family", "")
                            if given and family:
                                authors_list.append(f"{given} {family}")
                            elif family:
                                authors_list.append(family)

                        # Year
                        published = work.get("published-print") or work.get("published-online") or work.get("created")
                        year = None
                        if published and "date-parts" in published:
                            date_parts = published["date-parts"][0]
                            if date_parts:
                                year = date_parts[0]

                        # Journal
                        journal = work.get("container-title", [""])[0] if work.get("container-title") else ""

                        result = VerificationResult(
                            valid=True,
                            doi=doi,
                            title=title,
                            authors=authors_list,
                            year=year,
                            journal=journal,
                            url=f"https://doi.org/{doi}",
                            verification_method="crossref",
                            confidence=1.0
                        )

                        # Cache result
                        self._cache[doi] = asdict(result)
                        self._save_cache()

                        return result

                    elif response.status == 404:
                        return VerificationResult(
                            valid=False,
                            doi=doi,
                            error="DOI not found in CrossRef",
                            verification_method="crossref",
                            confidence=0.9
                        )
                    else:
                        return VerificationResult(
                            valid=False,
                            doi=doi,
                            error=f"CrossRef API returned status {response.status}",
                            verification_method="crossref",
                            confidence=0.5
                        )

        except asyncio.TimeoutError:
            return VerificationResult(
                valid=False,
                doi=doi,
                error="Request timed out",
                verification_method="crossref",
                confidence=0.3
            )
        except ImportError:
            return VerificationResult(
                valid=False,
                doi=doi,
                error="aiohttp not available for DOI verification",
                verification_method="none",
                confidence=0.0
            )
        except Exception as e:
            return VerificationResult(
                valid=False,
                doi=doi,
                error=str(e),
                verification_method="crossref",
                confidence=0.2
            )

    async def verify_citation(self, citation_text: str) -> VerificationResult:
        """
        Verify a citation string.

        First tries to extract and verify DOI.
        Falls back to heuristic validation.
        """
        # Try DOI extraction first
        doi = self.extract_doi(citation_text)
        if doi:
            return await self.verify_doi(doi)

        # Heuristic validation for citations without DOI
        return self._heuristic_validation(citation_text)

    def _heuristic_validation(self, citation_text: str) -> VerificationResult:
        """
        Heuristic validation for citations without DOI.

        Checks for:
        - Author names (Capitalized words)
        - Year (4-digit number 1900-2099)
        - Title (quoted or in sentence case)
        - Journal/venue name
        """
        confidence = 0.0
        errors = []

        # Check for year
        year_match = re.search(r'\b(19|20)\d{2}\b', citation_text)
        if year_match:
            confidence += 0.25
            year = int(year_match.group())
        else:
            errors.append("No year found")
            year = None

        # Check for author pattern (Last, F. or Last F.)
        author_pattern = r'[A-Z][a-z]+(?:,?\s+[A-Z]\.?)'
        authors = re.findall(author_pattern, citation_text)
        if authors:
            confidence += 0.25
        else:
            errors.append("No author pattern found")

        # Check for title (quoted text or sentence-case phrase)
        title_match = re.search(r'"([^"]+)"|\bIn:\s*([^,\.]+)', citation_text)
        if title_match:
            confidence += 0.25
            title = title_match.group(1) or title_match.group(2)
        else:
            # Look for capitalized words that could be a title
            words = citation_text.split()
            if len(words) > 5:
                confidence += 0.15
                title = None
            else:
                errors.append("No title pattern found")
                title = None

        # Check for journal indicators
        journal_indicators = ['Journal', 'Conference', 'Proceedings', 'IEEE', 'ACM', 'arXiv']
        if any(ind in citation_text for ind in journal_indicators):
            confidence += 0.25
        else:
            errors.append("No journal/venue indicator found")

        valid = confidence >= 0.5

        return VerificationResult(
            valid=valid,
            year=year,
            title=title,
            authors=authors if authors else None,
            error="; ".join(errors) if errors else None,
            verification_method="heuristic",
            confidence=confidence
        )

    async def verify_paper_exists(self, title: str, authors: List[str] = None, year: int = None) -> VerificationResult:
        """
        Verify that a paper exists by searching CrossRef.

        Uses title search with optional author/year filtering.
        """
        await self._rate_limit()

        try:
            import aiohttp
            import urllib.parse

            # Build query
            query = urllib.parse.quote(title)
            url = f"https://api.crossref.org/works?query.title={query}&rows=5"

            headers = {
                "User-Agent": "CiteAgent/1.4.8 (https://github.com/Spectating101/cite-agent; mailto:contact@citeagent.dev)"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("message", {}).get("items", [])

                        if not items:
                            return VerificationResult(
                                valid=False,
                                title=title,
                                error="No matching papers found",
                                verification_method="crossref_search",
                                confidence=0.7
                            )

                        # Find best match
                        best_match = None
                        best_score = 0.0

                        for item in items:
                            score = self._compute_match_score(title, authors, year, item)
                            if score > best_score:
                                best_score = score
                                best_match = item

                        if best_match and best_score > 0.6:
                            item_title = best_match.get("title", [""])[0]
                            item_doi = best_match.get("DOI", "")

                            # Extract authors
                            item_authors = []
                            for author in best_match.get("author", []):
                                given = author.get("given", "")
                                family = author.get("family", "")
                                if given and family:
                                    item_authors.append(f"{given} {family}")
                                elif family:
                                    item_authors.append(family)

                            # Year
                            published = best_match.get("published-print") or best_match.get("published-online")
                            item_year = None
                            if published and "date-parts" in published:
                                date_parts = published["date-parts"][0]
                                if date_parts:
                                    item_year = date_parts[0]

                            return VerificationResult(
                                valid=True,
                                doi=item_doi,
                                title=item_title,
                                authors=item_authors,
                                year=item_year,
                                url=f"https://doi.org/{item_doi}" if item_doi else None,
                                verification_method="crossref_search",
                                confidence=best_score
                            )
                        else:
                            return VerificationResult(
                                valid=False,
                                title=title,
                                error="No sufficiently matching papers found",
                                verification_method="crossref_search",
                                confidence=best_score
                            )

                    else:
                        return VerificationResult(
                            valid=False,
                            title=title,
                            error=f"CrossRef search returned status {response.status}",
                            verification_method="crossref_search",
                            confidence=0.3
                        )

        except Exception as e:
            return VerificationResult(
                valid=False,
                title=title,
                error=str(e),
                verification_method="crossref_search",
                confidence=0.2
            )

    def _compute_match_score(self, query_title: str, query_authors: Optional[List[str]],
                             query_year: Optional[int], item: Dict[str, Any]) -> float:
        """Compute match score between query and CrossRef item"""
        score = 0.0

        # Title similarity (simple word overlap)
        item_title = item.get("title", [""])[0].lower()
        query_words = set(query_title.lower().split())
        item_words = set(item_title.split())

        if query_words and item_words:
            overlap = len(query_words & item_words)
            title_score = overlap / max(len(query_words), len(item_words))
            score += title_score * 0.6

        # Author match
        if query_authors:
            item_authors = []
            for author in item.get("author", []):
                item_authors.append(author.get("family", "").lower())

            query_author_names = [a.split()[-1].lower() for a in query_authors]
            if item_authors and query_author_names:
                author_overlap = len(set(query_author_names) & set(item_authors))
                author_score = author_overlap / max(len(query_author_names), len(item_authors))
                score += author_score * 0.3

        # Year match
        if query_year:
            published = item.get("published-print") or item.get("published-online")
            if published and "date-parts" in published:
                date_parts = published["date-parts"][0]
                if date_parts:
                    item_year = date_parts[0]
                    if item_year == query_year:
                        score += 0.1
                    elif abs(item_year - query_year) <= 1:
                        score += 0.05

        return score

    async def _rate_limit(self):
        """Enforce rate limiting for API requests"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _save_cache(self):
        """Save verification cache to disk"""
        cache_file = self.cache_dir / "verifications.json"
        with open(cache_file, 'w') as f:
            json.dump(self._cache, f)

    def _load_cache(self):
        """Load verification cache from disk"""
        cache_file = self.cache_dir / "verifications.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        valid_count = sum(1 for v in self._cache.values() if v.get("valid", False))
        return {
            "total_verifications": len(self._cache),
            "valid_citations": valid_count,
            "invalid_citations": len(self._cache) - valid_count,
            "cache_size_bytes": sum(len(json.dumps(v)) for v in self._cache.values())
        }

    def clear_cache(self):
        """Clear verification cache"""
        self._cache = {}
        cache_file = self.cache_dir / "verifications.json"
        if cache_file.exists():
            cache_file.unlink()


# Global instance
_verifier: Optional[CitationVerifier] = None


def get_verifier() -> CitationVerifier:
    """Get or create global citation verifier"""
    global _verifier
    if _verifier is None:
        _verifier = CitationVerifier()
    return _verifier


async def verify_doi(doi: str) -> VerificationResult:
    """Verify a DOI"""
    verifier = get_verifier()
    return await verifier.verify_doi(doi)


async def verify_citation(citation_text: str) -> VerificationResult:
    """Verify a citation string"""
    verifier = get_verifier()
    return await verifier.verify_citation(citation_text)


async def verify_paper_exists(title: str, authors: List[str] = None, year: int = None) -> VerificationResult:
    """Verify paper existence"""
    verifier = get_verifier()
    return await verifier.verify_paper_exists(title, authors, year)


def extract_dois(text: str) -> List[str]:
    """Extract DOIs from text"""
    verifier = get_verifier()
    return verifier.extract_all_dois(text)


def verification_stats() -> Dict[str, Any]:
    """Get verification statistics"""
    verifier = get_verifier()
    return verifier.get_stats()
