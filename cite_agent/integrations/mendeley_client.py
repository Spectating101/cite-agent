#!/usr/bin/env python3
"""
Mendeley API Client - OAuth-based integration
Push papers to Mendeley library via API v1

API Documentation: https://dev.mendeley.com/reference/topics/documents.html
Note: Requires OAuth 2.0 authentication
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MendeleyConfig:
    """Mendeley API configuration"""
    client_id: str
    client_secret: str
    access_token: Optional[str] = None

    @classmethod
    def from_env(cls):
        """Load from environment variables"""
        client_id = os.getenv("MENDELEY_CLIENT_ID")
        client_secret = os.getenv("MENDELEY_CLIENT_SECRET")
        access_token = os.getenv("MENDELEY_ACCESS_TOKEN")

        if not client_id or not client_secret:
            raise ValueError(
                "Mendeley credentials not found. Set MENDELEY_CLIENT_ID and MENDELEY_CLIENT_SECRET.\n"
                "Register app at: https://dev.mendeley.com/myapps.html"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token
        )


class MendeleyClient:
    """
    Mendeley API integration with OAuth 2.0

    Features:
    - Push papers to Mendeley library
    - Create folders/groups
    - Add tags and notes
    - Full text search

    Note: Requires OAuth flow for first-time setup
    Use cite-agent --setup-mendeley to authorize

    Usage:
        config = MendeleyConfig.from_env()
        client = MendeleyClient(config)
        await client.authenticate()  # First time only
        await client.push_paper(paper_data)
    """

    BASE_URL = "https://api.mendeley.com"
    AUTH_URL = "https://api.mendeley.com/oauth/authorize"
    TOKEN_URL = "https://api.mendeley.com/oauth/token"

    def __init__(self, config: MendeleyConfig):
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
        if not self.config.access_token:
            raise ValueError("Not authenticated. Call authenticate() first or set MENDELEY_ACCESS_TOKEN")

        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json"
        }

    async def get_authorization_url(self, redirect_uri: str = "http://localhost:8080/callback") -> str:
        """
        Get OAuth authorization URL for user to visit

        Args:
            redirect_uri: OAuth callback URL

        Returns:
            Authorization URL to visit in browser
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "all"
        }

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{param_str}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str = "http://localhost:8080/callback"
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback
            redirect_uri: Must match the one used in authorization

        Returns:
            Dict with access_token and refresh_token
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }

        try:
            async with self.session.post(
                self.TOKEN_URL,
                json=payload
            ) as response:
                if response.status == 200:
                    tokens = await response.json()
                    self.config.access_token = tokens["access_token"]
                    return {
                        "success": True,
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens.get("refresh_token"),
                        "message": "Successfully authenticated with Mendeley"
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "message": f"Token exchange failed: {error}"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during authentication: {str(e)}"
            }

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test Mendeley API connection

        Returns:
            Dict with connection status and profile info
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        if not self.config.access_token:
            return {
                "success": False,
                "message": "Not authenticated. Run 'cite-agent --setup-mendeley' first."
            }

        try:
            url = f"{self.BASE_URL}/profiles/me"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    profile = await response.json()
                    return {
                        "success": True,
                        "message": f"Connected to Mendeley (User: {profile.get('display_name', 'Unknown')})",
                        "profile": profile
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

    def _paper_to_mendeley_document(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert paper data to Mendeley document format

        Args:
            paper: Paper dict

        Returns:
            Mendeley-formatted document
        """
        doc = {
            "title": paper.get("title", ""),
            "type": "journal",
            "year": int(paper.get("year", 0)) if paper.get("year") else None,
            "abstract": paper.get("abstract", ""),
            "source": paper.get("venue", ""),
            "identifiers": {}
        }

        # DOI
        if paper.get("doi"):
            doc["identifiers"]["doi"] = paper["doi"]

        # Authors
        if paper.get("authors"):
            doc["authors"] = []
            for author in paper["authors"]:
                if isinstance(author, str):
                    parts = author.rsplit(' ', 1)
                    if len(parts) == 2:
                        doc["authors"].append({
                            "first_name": parts[0],
                            "last_name": parts[1]
                        })
                    else:
                        doc["authors"].append({"last_name": author})
                elif isinstance(author, dict):
                    doc["authors"].append({
                        "first_name": author.get("firstName", ""),
                        "last_name": author.get("lastName", author.get("name", ""))
                    })

        # Tags
        if paper.get("tags"):
            doc["tags"] = paper["tags"]

        # Remove None values
        doc = {k: v for k, v in doc.items() if v is not None and v != {}}

        return doc

    async def push_paper(
        self,
        paper: Dict[str, Any],
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push a single paper to Mendeley library

        Args:
            paper: Paper dict
            folder_id: Optional folder to add to

        Returns:
            Dict with success status and document ID
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        doc = self._paper_to_mendeley_document(paper)
        url = f"{self.BASE_URL}/documents"

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=doc
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    doc_id = result["id"]

                    # Add to folder if specified
                    if folder_id:
                        await self._add_to_folder(doc_id, folder_id)

                    return {
                        "success": True,
                        "message": f"Added to Mendeley: {paper.get('title', 'Paper')}",
                        "document_id": doc_id
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
                "message": f"Error pushing to Mendeley: {str(e)}"
            }

    async def _add_to_folder(self, document_id: str, folder_id: str) -> bool:
        """Add document to folder"""
        url = f"{self.BASE_URL}/folders/{folder_id}/documents"
        payload = {"id": document_id}

        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                json=payload
            ) as response:
                return response.status in [200, 201]
        except Exception:
            return False

    async def push_papers_batch(
        self,
        papers: List[Dict[str, Any]],
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push multiple papers to Mendeley

        Args:
            papers: List of paper dicts
            folder_id: Optional folder to add to

        Returns:
            Dict with success count and errors
        """
        results = {
            "success": True,
            "added": 0,
            "failed": 0,
            "errors": []
        }

        for paper in papers:
            result = await self.push_paper(paper, folder_id)
            if result["success"]:
                results["added"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "paper": paper.get("title", "Unknown"),
                    "error": result["message"]
                })

        results["message"] = f"Added {results['added']}/{len(papers)} papers to Mendeley"
        if results["failed"] > 0:
            results["success"] = False
            results["message"] += f" ({results['failed']} failed)"

        return results


# Convenience function
async def push_to_mendeley(
    papers: List[Dict[str, Any]],
    folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to push papers to Mendeley

    Usage:
        result = await push_to_mendeley(papers)
        print(result["message"])
    """
    try:
        config = MendeleyConfig.from_env()

        async with MendeleyClient(config) as client:
            # Test connection
            test = await client.test_connection()
            if not test["success"]:
                return test

            # Push papers
            if len(papers) == 1:
                return await client.push_paper(papers[0], folder_id)
            else:
                return await client.push_papers_batch(papers, folder_id)

    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
