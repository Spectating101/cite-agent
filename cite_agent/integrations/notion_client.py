#!/usr/bin/env python3
"""
Notion API Client - Direct integration with Notion workspace
Push papers and research notes directly to Notion databases

API Documentation: https://developers.notion.com/reference/intro
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotionConfig:
    """Notion API configuration"""
    api_key: str
    database_id: Optional[str] = None

    @classmethod
    def from_env(cls):
        """Load from environment variables"""
        api_key = os.getenv("NOTION_API_KEY")

        if not api_key:
            raise ValueError(
                "Notion credentials not found. Set NOTION_API_KEY.\n"
                "Get API key from: https://www.notion.so/my-integrations"
            )

        return cls(
            api_key=api_key,
            database_id=os.getenv("NOTION_DATABASE_ID")
        )


class NotionClient:
    """
    Direct Notion API integration

    Features:
    - Push papers to Notion database
    - Create research notes pages
    - Organize by tags and collections
    - Link related papers

    Usage:
        config = NotionConfig.from_env()
        client = NotionClient(config)
        await client.create_paper_page(paper_data)
    """

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, config: NotionConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test Notion API connection

        Returns:
            Dict with connection status
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Test by listing users (lightweight endpoint)
            url = f"{self.BASE_URL}/users/me"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    user = await response.json()
                    return {
                        "success": True,
                        "message": f"Connected to Notion (User: {user.get('name', 'Unknown')})"
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Connection failed: {error}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

    async def create_database(
        self,
        parent_page_id: str,
        title: str = "Research Papers"
    ) -> Dict[str, Any]:
        """
        Create a new database for papers

        Args:
            parent_page_id: ID of parent Notion page
            title: Database title

        Returns:
            Dict with success status and database_id
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Define database schema for research papers
        payload = {
            "parent": {"page_id": parent_page_id},
            "title": [
                {
                    "type": "text",
                    "text": {"content": title}
                }
            ],
            "properties": {
                "Title": {"title": {}},
                "Authors": {"rich_text": {}},
                "Year": {"number": {}},
                "DOI": {"url": {}},
                "Citation Count": {"number": {}},
                "Venue": {"rich_text": {}},
                "Tags": {"multi_select": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "To Read", "color": "gray"},
                            {"name": "Reading", "color": "blue"},
                            {"name": "Read", "color": "green"},
                            {"name": "Cited", "color": "purple"}
                        ]
                    }
                },
                "Added": {"date": {}}
            }
        }

        url = f"{self.BASE_URL}/databases"

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    database_id = result["id"]
                    return {
                        "success": True,
                        "message": f"Created database: {title}",
                        "database_id": database_id,
                        "url": result.get("url", "")
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Failed to create database: {error}"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating database: {str(e)}"
            }

    def _paper_to_notion_properties(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert paper data to Notion page properties

        Args:
            paper: Paper dict with title, authors, year, doi, abstract, etc.

        Returns:
            Notion-formatted properties
        """
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {"content": paper.get("title", "Untitled")}
                    }
                ]
            }
        }

        # Authors
        if paper.get("authors"):
            authors_str = ", ".join(
                [a if isinstance(a, str) else a.get("name", "") for a in paper["authors"]]
            )
            properties["Authors"] = {
                "rich_text": [
                    {
                        "text": {"content": authors_str}
                    }
                ]
            }

        # Year
        if paper.get("year"):
            properties["Year"] = {"number": int(paper["year"])}

        # DOI
        if paper.get("doi"):
            doi_url = f"https://doi.org/{paper['doi']}" if not paper["doi"].startswith("http") else paper["doi"]
            properties["DOI"] = {"url": doi_url}

        # Citation count
        if paper.get("citation_count"):
            properties["Citation Count"] = {"number": int(paper["citation_count"])}

        # Venue
        if paper.get("venue"):
            properties["Venue"] = {
                "rich_text": [
                    {
                        "text": {"content": paper["venue"]}
                    }
                ]
            }

        # Tags
        if paper.get("tags"):
            properties["Tags"] = {
                "multi_select": [
                    {"name": tag} for tag in paper["tags"]
                ]
            }

        # Status (default to "To Read")
        properties["Status"] = {"select": {"name": "To Read"}}

        # Added date
        properties["Added"] = {
            "date": {
                "start": paper.get("added_date", datetime.now().isoformat())
            }
        }

        return properties

    def _paper_to_notion_content(self, paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert paper abstract to Notion page content blocks

        Args:
            paper: Paper dict

        Returns:
            List of Notion content blocks
        """
        blocks = []

        # Abstract section
        if paper.get("abstract"):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Abstract"}}]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": paper["abstract"]}}]
                }
            })

        # Notes section
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Notes"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": "Add your notes here..."}}]
            }
        })

        # Key findings section
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Key Findings"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"text": {"content": "Finding 1"}}]
            }
        })

        return blocks

    async def create_paper_page(
        self,
        paper: Dict[str, Any],
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new page for a paper in Notion database

        Args:
            paper: Paper dict (title, authors, year, doi, abstract, etc.)
            database_id: Target database ID (uses config default if not provided)

        Returns:
            Dict with success status and page ID
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        db_id = database_id or self.config.database_id
        if not db_id:
            return {
                "success": False,
                "message": "No database_id provided. Set NOTION_DATABASE_ID or pass database_id parameter."
            }

        properties = self._paper_to_notion_properties(paper)
        content = self._paper_to_notion_content(paper)

        payload = {
            "parent": {"database_id": db_id},
            "properties": properties,
            "children": content
        }

        url = f"{self.BASE_URL}/pages"

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    return {
                        "success": True,
                        "message": f"Added to Notion: {paper.get('title', 'Paper')}",
                        "page_id": result["id"],
                        "url": result.get("url", "")
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Failed to create page: {error}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating Notion page: {str(e)}"
            }

    async def create_papers_batch(
        self,
        papers: List[Dict[str, Any]],
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create multiple paper pages in batch

        Args:
            papers: List of paper dicts
            database_id: Target database ID

        Returns:
            Dict with success count and failed papers
        """
        results = {
            "success": True,
            "added": 0,
            "failed": 0,
            "errors": []
        }

        for paper in papers:
            result = await self.create_paper_page(paper, database_id)
            if result["success"]:
                results["added"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "paper": paper.get("title", "Unknown"),
                    "error": result["message"]
                })

        results["message"] = f"Added {results['added']}/{len(papers)} papers to Notion"
        if results["failed"] > 0:
            results["success"] = False
            results["message"] += f" ({results['failed']} failed)"

        return results


# Convenience function for quick usage
async def push_to_notion(
    papers: List[Dict[str, Any]],
    database_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to push papers to Notion

    Usage:
        result = await push_to_notion(papers)
        print(result["message"])
    """
    try:
        config = NotionConfig.from_env()

        async with NotionClient(config) as client:
            # Test connection first
            test = await client.test_connection()
            if not test["success"]:
                return test

            # Push papers
            if len(papers) == 1:
                return await client.create_paper_page(papers[0], database_id)
            else:
                return await client.create_papers_batch(papers, database_id)

    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
