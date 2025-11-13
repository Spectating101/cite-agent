"""
Academic Tool Integrations Module
Direct API connections to Zotero, Mendeley, Notion, etc.
"""

# Load environment variables from ~/.cite-agent.env
from cite_agent.env_loader import load_integration_env
load_integration_env()

from .zotero_client import ZoteroClient, push_to_zotero
from .notion_client import NotionClient, push_to_notion
from .mendeley_client import MendeleyClient, push_to_mendeley

__all__ = [
    'ZoteroClient',
    'NotionClient',
    'MendeleyClient',
    'push_to_zotero',
    'push_to_notion',
    'push_to_mendeley'
]
