#!/usr/bin/env python3
"""
External Integrations Module - "Holy Shit" Level Features
Connectors for Zotero, Stripe, PDF management, and more

Makes this agent INSANELY better than any competition.
"""

import asyncio
import json
import os
import hashlib
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ZOTERO CONNECTOR - One-click export to Zotero library
# ============================================================================

@dataclass
class ZoteroItem:
    """Zotero item representation"""
    item_type: str = "journalArticle"
    title: str = ""
    creators: List[Dict[str, str]] = field(default_factory=list)
    abstract_note: str = ""
    publication_title: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    date: str = ""
    DOI: str = ""
    url: str = ""
    extra: str = ""
    tags: List[Dict[str, str]] = field(default_factory=list)

    def to_zotero_json(self) -> Dict[str, Any]:
        """Convert to Zotero JSON format"""
        return {
            "itemType": self.item_type,
            "title": self.title,
            "creators": self.creators,
            "abstractNote": self.abstract_note,
            "publicationTitle": self.publication_title,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "date": self.date,
            "DOI": self.DOI,
            "url": self.url,
            "extra": self.extra,
            "tags": self.tags
        }


class ZoteroConnector:
    """
    Zotero integration - Export papers directly to Zotero library
    Supports both local Zotero and Zotero Web API
    """

    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize Zotero connector

        Args:
            api_key: Zotero API key (get from https://www.zotero.org/settings/keys)
            user_id: Zotero user ID
        """
        self.api_key = api_key or os.getenv("ZOTERO_API_KEY")
        self.user_id = user_id or os.getenv("ZOTERO_USER_ID")
        self.base_url = "https://api.zotero.org"

    def paper_to_zotero_item(self, paper: Dict[str, Any]) -> ZoteroItem:
        """
        Convert paper dict to Zotero item

        Args:
            paper: Paper dictionary

        Returns:
            ZoteroItem ready for export
        """
        # Parse authors
        creators = []
        authors = paper.get('authors', [])
        if isinstance(authors, list):
            for author in authors:
                if isinstance(author, dict):
                    name = author.get('name', '')
                elif isinstance(author, str):
                    name = author
                else:
                    continue

                # Split name into first/last
                parts = name.split()
                if len(parts) >= 2:
                    creators.append({
                        "creatorType": "author",
                        "firstName": " ".join(parts[:-1]),
                        "lastName": parts[-1]
                    })
                else:
                    creators.append({
                        "creatorType": "author",
                        "firstName": "",
                        "lastName": name
                    })

        # Create Zotero item
        item = ZoteroItem(
            item_type="journalArticle",
            title=paper.get('title', 'Untitled'),
            creators=creators,
            abstract_note=paper.get('abstract', '')[:10000],  # Zotero limit
            publication_title=paper.get('venue', ''),
            date=str(paper.get('year', '')),
            DOI=paper.get('doi', ''),
            url=paper.get('url', ''),
            extra=f"Citation count: {paper.get('citation_count', 0)}\nQuality score: {paper.get('quality_score', 0)}/100"
        )

        # Add tags
        if paper.get('venue'):
            item.tags.append({"tag": paper['venue']})

        quality_tier = paper.get('quality_tier', '')
        if quality_tier:
            item.tags.append({"tag": f"quality:{quality_tier}"})

        return item

    def export_to_bibtex_file(
        self,
        papers: List[Dict[str, Any]],
        output_path: str = "references.bib"
    ) -> str:
        """
        Export papers to BibTeX file (Zotero can import this)

        Args:
            papers: List of paper dicts
            output_path: Output file path

        Returns:
            Path to created file
        """
        from .workflow import Paper

        bibtex_entries = []
        for paper_dict in papers:
            # Convert to Paper object
            paper = Paper(
                title=paper_dict.get('title', 'Unknown'),
                authors=paper_dict.get('authors', []),
                year=paper_dict.get('year', 0),
                doi=paper_dict.get('doi'),
                url=paper_dict.get('url'),
                venue=paper_dict.get('venue'),
                abstract=paper_dict.get('abstract')
            )
            bibtex_entries.append(paper.to_bibtex())

        # Write to file
        content = "\n\n".join(bibtex_entries)
        Path(output_path).write_text(content, encoding='utf-8')

        return output_path

    def export_to_json(
        self,
        papers: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Export papers to Zotero JSON format

        Args:
            papers: List of paper dicts
            output_path: Optional output file path

        Returns:
            Path to created file or JSON string
        """
        # Convert all papers to Zotero items
        items = [self.paper_to_zotero_item(paper).to_zotero_json() for paper in papers]

        # Create Zotero JSON export format
        export_data = {
            "items": items,
            "collections": [],
            "version": 3
        }

        json_str = json.dumps(export_data, indent=2)

        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
            return output_path

        return json_str

    async def export_to_zotero_api(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Export papers directly to Zotero via API

        Args:
            papers: List of paper dicts

        Returns:
            Result dictionary with success/failure info
        """
        if not self.api_key or not self.user_id:
            return {
                "success": False,
                "error": "Zotero API key and user ID required. Set ZOTERO_API_KEY and ZOTERO_USER_ID environment variables."
            }

        # Convert papers to Zotero items
        items = [self.paper_to_zotero_item(paper).to_zotero_json() for paper in papers]

        # Send to Zotero API
        url = f"{self.base_url}/users/{self.user_id}/items"
        headers = {
            "Zotero-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=items, headers=headers) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "count": len(items),
                            "message": f"Successfully exported {len(items)} papers to Zotero"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Zotero API error ({response.status}): {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Export failed: {str(e)}"
            }


# ============================================================================
# PDF MANAGEMENT - Download and parse academic PDFs
# ============================================================================

class PDFManager:
    """
    PDF download and analysis system
    Auto-fetch full papers and extract content
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize PDF manager"""
        self.cache_dir = Path(cache_dir or Path.home() / ".cite_agent" / "pdf_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_pdf_path(self, paper_id: str) -> Path:
        """Get cached PDF path"""
        safe_id = re.sub(r'[^\w\-]', '_', paper_id)
        return self.cache_dir / f"{safe_id}.pdf"

    async def download_pdf(
        self,
        url: str,
        paper_id: str,
        timeout: int = 30
    ) -> Optional[Path]:
        """
        Download PDF from URL

        Args:
            url: PDF URL
            paper_id: Paper identifier
            timeout: Download timeout in seconds

        Returns:
            Path to downloaded PDF or None if failed
        """
        pdf_path = self.get_pdf_path(paper_id)

        # Check cache
        if pdf_path.exists():
            return pdf_path

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.read()
                        pdf_path.write_bytes(content)
                        return pdf_path
        except Exception as e:
            logger.error(f"PDF download failed: {e}")

        return None

    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        try:
            # Try PyPDF2 first
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            logger.warning("PyPDF2 not installed, trying pdfplumber")
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")

        try:
            # Fallback to pdfplumber
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except ImportError:
            logger.warning("pdfplumber not installed, PDF text extraction unavailable")
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")

        return None

    async def get_paper_full_text(
        self,
        paper: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get full text of paper (download + extract)

        Args:
            paper: Paper dictionary with url/doi

        Returns:
            Full text or None if unavailable
        """
        # Try to find PDF URL
        pdf_url = paper.get('pdf_url') or paper.get('url')
        if not pdf_url:
            return None

        paper_id = paper.get('paper_id') or paper.get('id') or paper.get('doi', 'unknown')

        # Download
        pdf_path = await self.download_pdf(pdf_url, paper_id)
        if not pdf_path:
            return None

        # Extract text
        return self.extract_text_from_pdf(pdf_path)


# ============================================================================
# STRIPE INTEGRATION - Monetization ready
# ============================================================================

class StripeIntegration:
    """
    Stripe payment integration for monetization
    Supports: Premium features, API credits, subscriptions
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe integration"""
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        self.pricing = {
            "free": {
                "papers_per_month": 50,
                "api_calls_per_day": 100,
                "exports": True,
                "pdf_download": False,
                "price": 0
            },
            "pro": {
                "papers_per_month": 500,
                "api_calls_per_day": 1000,
                "exports": True,
                "pdf_download": True,
                "zotero_sync": True,
                "email_digests": True,
                "price": 20  # $20/month
            },
            "enterprise": {
                "papers_per_month": "unlimited",
                "api_calls_per_day": 10000,
                "exports": True,
                "pdf_download": True,
                "zotero_sync": True,
                "email_digests": True,
                "custom_integrations": True,
                "dedicated_support": True,
                "price": 200  # $200/month
            }
        }

    def get_pricing_plans(self) -> Dict[str, Any]:
        """Get available pricing plans"""
        return self.pricing

    def check_feature_access(
        self,
        user_tier: str,
        feature: str
    ) -> bool:
        """
        Check if user has access to feature

        Args:
            user_tier: User's subscription tier
            feature: Feature to check

        Returns:
            True if user has access
        """
        plan = self.pricing.get(user_tier, self.pricing['free'])
        return plan.get(feature, False)

    async def create_checkout_session(
        self,
        user_id: str,
        plan: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session

        Args:
            user_id: User identifier
            plan: Pricing plan (pro/enterprise)
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel

        Returns:
            Checkout session info
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Stripe API key not configured"
            }

        plan_info = self.pricing.get(plan)
        if not plan_info or plan_info['price'] == 0:
            return {
                "success": False,
                "error": f"Invalid plan: {plan}"
            }

        # In production, create actual Stripe session
        # For now, return mock data
        return {
            "success": True,
            "checkout_url": f"https://checkout.stripe.com/mock/{user_id}/{plan}",
            "session_id": f"cs_mock_{user_id}_{plan}",
            "price": plan_info['price']
        }


# ============================================================================
# CITATION MANAGERS - Support multiple platforms
# ============================================================================

class CitationManagerExporter:
    """
    Export to multiple citation managers
    Supports: Zotero, Mendeley, EndNote, RefWorks
    """

    def __init__(self):
        """Initialize citation manager exporter"""
        self.zotero = ZoteroConnector()

    def export_to_mendeley(
        self,
        papers: List[Dict[str, Any]],
        output_path: str = "mendeley_import.bib"
    ) -> str:
        """
        Export to Mendeley-compatible BibTeX

        Args:
            papers: List of papers
            output_path: Output file path

        Returns:
            Path to created file
        """
        # Mendeley uses standard BibTeX
        return self.zotero.export_to_bibtex_file(papers, output_path)

    def export_to_endnote(
        self,
        papers: List[Dict[str, Any]],
        output_path: str = "endnote_import.xml"
    ) -> str:
        """
        Export to EndNote XML format

        Args:
            papers: List of papers
            output_path: Output file path

        Returns:
            Path to created file
        """
        # EndNote XML format
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<xml>\n<records>\n'

        for paper in papers:
            xml_content += '<record>\n'
            xml_content += '<ref-type name="Journal Article">17</ref-type>\n'
            xml_content += f'<titles><title>{self._escape_xml(paper.get("title", ""))}</title></titles>\n'

            # Authors
            if paper.get('authors'):
                xml_content += '<contributors><authors>\n'
                for author in paper.get('authors', []):
                    author_name = author.get('name', author) if isinstance(author, dict) else author
                    xml_content += f'<author>{self._escape_xml(author_name)}</author>\n'
                xml_content += '</authors></contributors>\n'

            # Other fields
            if paper.get('year'):
                xml_content += f'<dates><year>{paper["year"]}</year></dates>\n'
            if paper.get('venue'):
                xml_content += f'<periodical><full-title>{self._escape_xml(paper["venue"])}</full-title></periodical>\n'
            if paper.get('doi'):
                xml_content += f'<electronic-resource-num>{paper["doi"]}</electronic-resource-num>\n'
            if paper.get('url'):
                xml_content += f'<urls><related-urls><url>{paper["url"]}</url></related-urls></urls>\n'

            xml_content += '</record>\n'

        xml_content += '</records>\n</xml>'

        Path(output_path).write_text(xml_content, encoding='utf-8')
        return output_path

    def export_to_ris(
        self,
        papers: List[Dict[str, Any]],
        output_path: str = "papers.ris"
    ) -> str:
        """
        Export to RIS format (supported by RefWorks, Mendeley, Zotero)

        Args:
            papers: List of papers
            output_path: Output file path

        Returns:
            Path to created file
        """
        ris_content = ""

        for paper in papers:
            ris_content += "TY  - JOUR\n"  # Journal Article
            ris_content += f"TI  - {paper.get('title', 'Untitled')}\n"

            # Authors
            for author in paper.get('authors', []):
                author_name = author.get('name', author) if isinstance(author, dict) else author
                ris_content += f"AU  - {author_name}\n"

            # Other fields
            if paper.get('year'):
                ris_content += f"PY  - {paper['year']}\n"
            if paper.get('venue'):
                ris_content += f"JO  - {paper['venue']}\n"
            if paper.get('doi'):
                ris_content += f"DO  - {paper['doi']}\n"
            if paper.get('url'):
                ris_content += f"UR  - {paper['url']}\n"
            if paper.get('abstract'):
                ris_content += f"AB  - {paper['abstract']}\n"

            ris_content += "ER  - \n\n"

        Path(output_path).write_text(ris_content, encoding='utf-8')
        return output_path

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# ============================================================================
# KNOWLEDGE BASE EXPORTERS - Obsidian, Notion, etc.
# ============================================================================

class KnowledgeBaseExporter:
    """
    Export research to knowledge bases
    Supports: Obsidian, Notion, Roam Research
    """

    def export_to_obsidian(
        self,
        papers: List[Dict[str, Any]],
        vault_path: Optional[str] = None,
        folder: str = "Research Papers"
    ) -> List[str]:
        """
        Export papers as Obsidian notes with backlinks

        Args:
            papers: List of papers
            vault_path: Path to Obsidian vault
            folder: Folder within vault

        Returns:
            List of created file paths
        """
        if not vault_path:
            vault_path = Path.home() / "ObsidianVault"

        vault = Path(vault_path) / folder
        vault.mkdir(parents=True, exist_ok=True)

        created_files = []

        for paper in papers:
            title = paper.get('title', 'Untitled')
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
            filename = f"{safe_title}.md"
            filepath = vault / filename

            # Create Obsidian-style markdown
            content = f"# {title}\n\n"
            content += f"**Type**: #paper\n"
            content += f"**Year**: [[{paper.get('year', 'Unknown')}]]\n"
            if paper.get('venue'):
                content += f"**Venue**: [[{paper['venue']}]]\n"
            content += f"**Quality Score**: {paper.get('quality_score', 0)}/100\n\n"

            # Authors with backlinks
            if paper.get('authors'):
                content += "**Authors**: "
                author_links = [f"[[{a.get('name', a) if isinstance(a, dict) else a}]]" for a in paper['authors'][:5]]
                content += ", ".join(author_links)
                content += "\n\n"

            # Links
            if paper.get('doi'):
                content += f"**DOI**: [{paper['doi']}](https://doi.org/{paper['doi']})\n"
            if paper.get('url'):
                content += f"**URL**: {paper['url']}\n"
            content += "\n"

            # Abstract
            if paper.get('abstract'):
                content += "## Abstract\n\n"
                content += paper['abstract'] + "\n\n"

            # Notes section
            content += "## Notes\n\n"
            content += "- \n\n"

            # Tags
            tags = ['#research']
            if paper.get('quality_tier'):
                tags.append(f"#quality-{paper['quality_tier']}")
            content += f"\n\n{' '.join(tags)}\n"

            filepath.write_text(content, encoding='utf-8')
            created_files.append(str(filepath))

        return created_files

    def export_to_notion_csv(
        self,
        papers: List[Dict[str, Any]],
        output_path: str = "notion_import.csv"
    ) -> str:
        """
        Export as CSV for Notion database import

        Args:
            papers: List of papers
            output_path: Output file path

        Returns:
            Path to created file
        """
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Title', 'Authors', 'Year', 'Venue', 'DOI', 'URL',
                'Quality Score', 'Citation Count', 'Abstract'
            ])
            writer.writeheader()

            for paper in papers:
                authors = ', '.join([
                    a.get('name', a) if isinstance(a, dict) else a
                    for a in paper.get('authors', [])
                ])

                writer.writerow({
                    'Title': paper.get('title', ''),
                    'Authors': authors,
                    'Year': paper.get('year', ''),
                    'Venue': paper.get('venue', ''),
                    'DOI': paper.get('doi', ''),
                    'URL': paper.get('url', ''),
                    'Quality Score': paper.get('quality_score', 0),
                    'Citation Count': paper.get('citation_count', 0),
                    'Abstract': paper.get('abstract', '')[:500]  # Truncate for CSV
                })

        return output_path
