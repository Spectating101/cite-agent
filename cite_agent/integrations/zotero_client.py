#!/usr/bin/env python3
"""
Zotero API Client - Direct integration with Zotero library
Push papers directly to user's Zotero library via Web API v3

API Documentation: https://www.zotero.org/support/dev/web_api/v3/start
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ZoteroConfig:
    """Zotero API configuration"""
    api_key: str
    user_id: str
    library_type: str = "user"  # or "group"

    @classmethod
    def from_env(cls):
        """Load from environment variables"""
        api_key = os.getenv("ZOTERO_API_KEY")
        user_id = os.getenv("ZOTERO_USER_ID")

        if not api_key or not user_id:
            raise ValueError(
                "Zotero credentials not found. Set ZOTERO_API_KEY and ZOTERO_USER_ID.\n"
                "Get API key from: https://www.zotero.org/settings/keys"
            )

        return cls(api_key=api_key, user_id=user_id)


class ZoteroClient:
    """
    Direct Zotero API integration

    Features:
    - Push papers directly to Zotero library
    - Create collections
    - Add tags
    - Sync with Zotero desktop app

    Usage:
        config = ZoteroConfig.from_env()
        client = ZoteroClient(config)
        await client.push_paper(paper_data)
    """

    BASE_URL = "https://api.zotero.org"

    def __init__(self, config: ZoteroConfig):
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
            "Zotero-API-Key": self.config.api_key,
            "Zotero-API-Version": "3",
            "Content-Type": "application/json"
        }

    def _get_library_url(self) -> str:
        """Get base library URL"""
        return f"{self.BASE_URL}/{self.config.library_type}s/{self.config.user_id}"

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test Zotero API connection

        Returns:
            Dict with connection status and library info
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            url = f"{self._get_library_url()}/items?limit=1"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    total_items = response.headers.get('Total-Results', '0')
                    return {
                        "success": True,
                        "message": f"Connected to Zotero library ({total_items} items)",
                        "library_size": int(total_items)
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

    def _paper_to_zotero_item(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert paper data to Zotero item format

        Args:
            paper: Paper dict with title, authors, year, doi, abstract, etc.

        Returns:
            Zotero-formatted item
        """
        # Parse authors into firstName/lastName
        creators = []
        for author in paper.get("authors", []):
            if isinstance(author, str):
                # Simple string author
                parts = author.rsplit(' ', 1)  # Split on last space
                if len(parts) == 2:
                    creators.append({
                        "creatorType": "author",
                        "firstName": parts[0],
                        "lastName": parts[1]
                    })
                else:
                    creators.append({
                        "creatorType": "author",
                        "name": author  # Single-field mode
                    })
            elif isinstance(author, dict):
                # Already structured
                creators.append({
                    "creatorType": "author",
                    "firstName": author.get("firstName", ""),
                    "lastName": author.get("lastName", author.get("name", ""))
                })

        item = {
            "itemType": "journalArticle",
            "title": paper.get("title", ""),
            "creators": creators,
            "abstractNote": paper.get("abstract", ""),
            "publicationTitle": paper.get("venue", ""),
            "date": str(paper.get("year", "")),
            "DOI": paper.get("doi", ""),
            "url": paper.get("url", ""),
            "accessDate": paper.get("added_date", ""),
            "extra": f"Citation count: {paper.get('citation_count', 0)}"
        }

        # Add tags if present
        if paper.get("tags"):
            item["tags"] = [{"tag": tag} for tag in paper["tags"]]

        # Remove empty fields
        item = {k: v for k, v in item.items() if v}

        return item

    async def push_paper(
        self,
        paper: Dict[str, Any],
        collection_key: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Push a single paper to Zotero library

        Args:
            paper: Paper dict (title, authors, year, doi, abstract, etc.)
            collection_key: Optional Zotero collection to add to
            tags: Optional additional tags

        Returns:
            Dict with success status and item key
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Convert paper to Zotero format
        item = self._paper_to_zotero_item(paper)

        # Add additional tags
        if tags:
            existing_tags = item.get("tags", [])
            existing_tags.extend([{"tag": tag} for tag in tags])
            item["tags"] = existing_tags

        # Add to collection if specified
        if collection_key:
            item["collections"] = [collection_key]

        # Prepare request
        url = f"{self._get_library_url()}/items"
        payload = [item]  # API expects array

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    item_key = result.get("successful", {}).get("0", {})
                    return {
                        "success": True,
                        "message": f"Added to Zotero: {paper.get('title', 'Paper')}",
                        "item_key": item_key,
                        "library_url": f"https://www.zotero.org/{self.config.library_type}s/{self.config.user_id}/items/{item_key}"
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Failed to add paper: {error}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error pushing to Zotero: {str(e)}"
            }

    async def push_papers_batch(
        self,
        papers: List[Dict[str, Any]],
        collection_key: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Push multiple papers to Zotero in batch

        Args:
            papers: List of paper dicts
            collection_key: Optional collection to add to
            tags: Optional tags for all papers

        Returns:
            Dict with success count and failed papers
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Convert all papers
        items = []
        for paper in papers:
            item = self._paper_to_zotero_item(paper)

            if tags:
                existing_tags = item.get("tags", [])
                existing_tags.extend([{"tag": tag} for tag in tags])
                item["tags"] = existing_tags

            if collection_key:
                item["collections"] = [collection_key]

            items.append(item)

        # Zotero API limit: 50 items per request
        batch_size = 50
        results = {
            "success": True,
            "added": 0,
            "failed": 0,
            "errors": []
        }

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            url = f"{self._get_library_url()}/items"

            try:
                async with self.session.post(
                    url,
                    headers=self._get_headers(),
                    json=batch
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        results["added"] += len(result.get("successful", {}))
                        results["failed"] += len(result.get("failed", {}))

                        if result.get("failed"):
                            results["errors"].extend(result["failed"].values())
                    else:
                        error = await response.text()
                        results["failed"] += len(batch)
                        results["errors"].append(f"Batch {i//batch_size + 1}: {error}")
            except Exception as e:
                results["failed"] += len(batch)
                results["errors"].append(f"Batch {i//batch_size + 1}: {str(e)}")

        results["message"] = f"Added {results['added']}/{len(papers)} papers to Zotero"
        if results["failed"] > 0:
            results["success"] = False
            results["message"] += f" ({results['failed']} failed)"

        return results

    async def create_collection(self, name: str, parent_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new collection in Zotero

        Args:
            name: Collection name
            parent_key: Optional parent collection key

        Returns:
            Dict with success status and collection key
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        collection = {
            "name": name,
            "parentCollection": parent_key
        }

        if not parent_key:
            del collection["parentCollection"]

        url = f"{self._get_library_url()}/collections"

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=[collection]
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    collection_key = result.get("successful", {}).get("0", {})
                    return {
                        "success": True,
                        "message": f"Created collection: {name}",
                        "collection_key": collection_key
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Failed to create collection: {error}"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating collection: {str(e)}"
            }

    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections in library

        Returns:
            List of collection dicts with key and name
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self._get_library_url()}/collections"

        try:
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    collections = await response.json()
                    return [
                        {
                            "key": col["key"],
                            "name": col["data"]["name"],
                            "num_items": col["meta"].get("numItems", 0)
                        }
                        for col in collections
                    ]
                else:
                    return []
        except Exception:
            return []


# Convenience function for quick usage
async def push_to_zotero(
    papers: List[Dict[str, Any]],
    collection_name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Quick function to push papers to Zotero

    Usage:
        result = await push_to_zotero(papers, collection_name="ESG Research")
        print(result["message"])
    """
    try:
        config = ZoteroConfig.from_env()

        async with ZoteroClient(config) as client:
            # Test connection first
            test = await client.test_connection()
            if not test["success"]:
                return test

            # Create collection if specified
            collection_key = None
            if collection_name:
                result = await client.create_collection(collection_name)
                if result["success"]:
                    collection_key = result["collection_key"]

            # Push papers
            if len(papers) == 1:
                return await client.push_paper(papers[0], collection_key, tags)
            else:
                return await client.push_papers_batch(papers, collection_key, tags)

    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
