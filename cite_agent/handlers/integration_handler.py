"""
Integration Handler for Zotero, Mendeley, and Notion
Handles conversational integration requests
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class IntegrationHandler:
    """
    Handles conversational integration requests for academic tools

    Detects natural language requests to push papers to:
    - Zotero
    - Mendeley
    - Notion
    """

    def detect_integration_request(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Detect if user wants to push papers to an integration

        Returns dict with:
        - target: "zotero", "mendeley", or "notion"
        - action: "push" or "save"
        - collection: optional collection/folder name

        Returns None if no integration request detected
        """
        question_lower = question.lower()

        # Use regex patterns to match variations with words in between
        # e.g., "push these papers to zotero", "add them to my zotero library"

        # Zotero patterns
        zotero_pattern = r'(add|push|save|send|put|export|store)(?:\s+\w+)*\s+(?:to|in)\s+(?:\w+\s+)*zotero'

        # Mendeley patterns
        mendeley_pattern = r'(add|push|save|send|put|export|store)(?:\s+\w+)*\s+(?:to|in)\s+(?:\w+\s+)*mendeley'

        # Notion patterns
        notion_pattern = r'(add|push|save|send|put|export|store|create)(?:\s+\w+)*\s+(?:to|in)\s+(?:\w+\s+)*notion'

        target = None
        if re.search(zotero_pattern, question_lower):
            target = "zotero"
        elif re.search(mendeley_pattern, question_lower):
            target = "mendeley"
        elif re.search(notion_pattern, question_lower):
            target = "notion"

        if not target:
            return None

        # Extract collection/folder name if mentioned
        collection = None
        # Patterns like: "add to zotero in ML collection", "save to notion database Research"
        collection_match = re.search(r'(?:in|to|under)\s+(?:collection|folder|database)?\s*["\']?([a-zA-Z0-9\s\-_]+)["\']?', question_lower)
        if collection_match:
            collection = collection_match.group(1).strip()

        return {
            "target": target,
            "action": "push",
            "collection": collection
        }

    def extract_papers_from_context(self, api_results: Dict[str, Any], question: str) -> List[Dict[str, Any]]:
        """
        Extract paper data from api_results

        Supports:
        - Papers from recent search_academic_papers results
        - Papers from conversation history
        - Papers mentioned by position ("first paper", "second paper")
        """
        papers = []

        # Check if we have research results in api_results
        if "research" in api_results:
            research_data = api_results["research"]
            if isinstance(research_data, dict):
                results = research_data.get("results") or research_data.get("papers") or []
                papers.extend(results)

        # Check knowledge base for position references ("first paper", "that paper", etc.)
        question_lower = question.lower()
        if any(ref in question_lower for ref in ["first paper", "second paper", "third paper", "that paper", "this paper", "the paper"]):
            try:
                from cite_agent.paper_knowledge import get_knowledge_base
                kb = get_knowledge_base()

                if "first paper" in question_lower:
                    paper_data = kb.get_paper_by_position(0)
                    if paper_data:
                        papers = [paper_data]
                elif "second paper" in question_lower:
                    paper_data = kb.get_paper_by_position(1)
                    if paper_data:
                        papers = [paper_data]
                elif "third paper" in question_lower:
                    paper_data = kb.get_paper_by_position(2)
                    if paper_data:
                        papers = [paper_data]
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Could not get paper from knowledge base: {e}")

        return papers

    async def push_to_integration(
        self,
        target: str,
        papers: List[Dict[str, Any]],
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push papers to integration (Zotero, Mendeley, or Notion)

        Args:
            target: "zotero", "mendeley", or "notion"
            papers: List of paper dicts
            collection: Optional collection/folder/database name

        Returns:
            Result dict with success status and message
        """
        if not papers:
            return {
                "success": False,
                "message": "No papers found to push. Please search for papers first.",
                "integration": target
            }

        try:
            # Import integration modules
            from cite_agent.integrations import (
                push_to_zotero,
                push_to_notion,
                push_to_mendeley
            )

            # Push to appropriate integration
            if target == "zotero":
                result = await push_to_zotero(papers, collection_name=collection)
            elif target == "mendeley":
                result = await push_to_mendeley(papers, folder_name=collection)
            elif target == "notion":
                result = await push_to_notion(papers, database_id=collection)
            else:
                return {
                    "success": False,
                    "message": f"Unknown integration target: {target}",
                    "integration": target
                }

            # Add integration name to result
            result["integration"] = target
            return result

        except ImportError as e:
            return {
                "success": False,
                "message": f"Integration module not available: {e}",
                "integration": target
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to push to {target}: {str(e)}",
                "integration": target
            }
