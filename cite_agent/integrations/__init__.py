"""
Academic Tool Integrations Module
Direct API connections to Zotero, Mendeley, Notion, etc.
"""

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
