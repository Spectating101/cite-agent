#!/usr/bin/env python3
"""
Tests for academic tool integrations
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from cite_agent.integrations import (
    ZoteroClient,
    NotionClient,
    MendeleyClient
)


@pytest.fixture
def sample_papers():
    """Sample paper data for testing"""
    return [
        {
            "title": "Attention Is All You Need",
            "authors": ["Vaswani", "Shazeer", "Parmar"],
            "year": 2017,
            "doi": "10.48550/arXiv.1706.03762",
            "abstract": "We propose a new simple network architecture...",
            "venue": "NeurIPS",
            "citation_count": 70000,
            "tags": ["transformers", "attention"]
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors": ["Devlin", "Chang", "Lee", "Toutanova"],
            "year": 2019,
            "doi": "10.18653/v1/N19-1423",
            "abstract": "We introduce BERT...",
            "venue": "NAACL",
            "citation_count": 50000,
            "tags": ["bert", "nlp"]
        }
    ]


class TestZoteroClient:
    """Test Zotero API client"""

    def test_paper_to_zotero_item(self, sample_papers):
        """Test paper conversion to Zotero format"""
        from cite_agent.integrations.zotero_client import ZoteroClient, ZoteroConfig

        config = ZoteroConfig(api_key="test_key", user_id="12345")
        client = ZoteroClient(config)

        item = client._paper_to_zotero_item(sample_papers[0])

        assert item["itemType"] == "journalArticle"
        assert item["title"] == "Attention Is All You Need"
        assert len(item["creators"]) == 3
        assert item["date"] == "2017"
        assert item["DOI"] == "10.48550/arXiv.1706.03762"
        assert "transformers" in [tag["tag"] for tag in item["tags"]]

    def test_headers_generation(self):
        """Test API header generation"""
        from cite_agent.integrations.zotero_client import ZoteroClient, ZoteroConfig

        config = ZoteroConfig(api_key="test_api_key", user_id="12345")
        client = ZoteroClient(config)

        headers = client._get_headers()

        assert headers["Zotero-API-Key"] == "test_api_key"
        assert headers["Zotero-API-Version"] == "3"
        assert headers["Content-Type"] == "application/json"

    def test_library_url_generation(self):
        """Test library URL construction"""
        from cite_agent.integrations.zotero_client import ZoteroClient, ZoteroConfig

        config = ZoteroConfig(api_key="test", user_id="12345", library_type="user")
        client = ZoteroClient(config)

        url = client._get_library_url()
        assert url == "https://api.zotero.org/users/12345"

        # Test group library
        config.library_type = "group"
        url = client._get_library_url()
        assert url == "https://api.zotero.org/groups/12345"

    @pytest.mark.asyncio
    async def test_push_paper_mock(self, sample_papers):
        """Test pushing a paper (mocked)"""
        from cite_agent.integrations.zotero_client import ZoteroClient, ZoteroConfig

        config = ZoteroConfig(api_key="test_key", user_id="12345")

        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={
                "successful": {"0": "ABC123"}
            })

            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

            async with ZoteroClient(config) as client:
                result = await client.push_paper(sample_papers[0])

                assert result["success"] is True
                assert "Added to Zotero" in result["message"]
                assert result["item_key"] == "ABC123"


class TestNotionClient:
    """Test Notion API client"""

    def test_paper_to_notion_properties(self, sample_papers):
        """Test paper conversion to Notion properties format"""
        from cite_agent.integrations.notion_client import NotionClient, NotionConfig

        config = NotionConfig(api_key="test_key")
        client = NotionClient(config)

        properties = client._paper_to_notion_properties(sample_papers[0])

        assert properties["Title"]["title"][0]["text"]["content"] == "Attention Is All You Need"
        assert properties["Year"]["number"] == 2017
        assert properties["DOI"]["url"] == "https://doi.org/10.48550/arXiv.1706.03762"
        assert properties["Citation Count"]["number"] == 70000
        assert len(properties["Tags"]["multi_select"]) == 2

    def test_paper_to_notion_content(self, sample_papers):
        """Test paper conversion to Notion content blocks"""
        from cite_agent.integrations.notion_client import NotionClient, NotionConfig

        config = NotionConfig(api_key="test_key")
        client = NotionClient(config)

        blocks = client._paper_to_notion_content(sample_papers[0])

        # Check that blocks are created
        assert len(blocks) > 0

        # Find abstract heading
        abstract_headings = [
            b for b in blocks
            if b.get("type") == "heading_2" and
            "Abstract" in b["heading_2"]["rich_text"][0]["text"]["content"]
        ]
        assert len(abstract_headings) == 1

    @pytest.mark.asyncio
    async def test_create_paper_page_mock(self, sample_papers):
        """Test creating a Notion page (mocked)"""
        from cite_agent.integrations.notion_client import NotionClient, NotionConfig

        config = NotionConfig(api_key="test_key", database_id="db123")

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={
                "id": "page123",
                "url": "https://notion.so/page123"
            })

            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

            async with NotionClient(config) as client:
                result = await client.create_paper_page(sample_papers[0])

                assert result["success"] is True
                assert "Added to Notion" in result["message"]
                assert result["page_id"] == "page123"


class TestMendeleyClient:
    """Test Mendeley API client"""

    def test_paper_to_mendeley_document(self, sample_papers):
        """Test paper conversion to Mendeley format"""
        from cite_agent.integrations.mendeley_client import MendeleyClient, MendeleyConfig

        config = MendeleyConfig(
            client_id="test_id",
            client_secret="test_secret",
            access_token="test_token"
        )
        client = MendeleyClient(config)

        doc = client._paper_to_mendeley_document(sample_papers[0])

        assert doc["title"] == "Attention Is All You Need"
        assert doc["type"] == "journal"
        assert doc["year"] == 2017
        assert doc["identifiers"]["doi"] == "10.48550/arXiv.1706.03762"
        assert len(doc["authors"]) == 3
        assert "transformers" in doc["tags"]

    def test_get_authorization_url(self):
        """Test OAuth authorization URL generation"""
        from cite_agent.integrations.mendeley_client import MendeleyClient, MendeleyConfig

        config = MendeleyConfig(client_id="test123", client_secret="secret456")
        client = MendeleyClient(config)

        url = asyncio.run(client.get_authorization_url())

        assert "client_id=test123" in url
        assert "response_type=code" in url
        assert "scope=all" in url


class TestIntegrationConvenience:
    """Test convenience functions"""

    @pytest.mark.asyncio
    async def test_push_to_zotero_no_credentials(self, sample_papers):
        """Test push_to_zotero without credentials"""
        from cite_agent.integrations import push_to_zotero

        with patch.dict('os.environ', {}, clear=True):
            result = await push_to_zotero(sample_papers)

            assert result["success"] is False
            assert "credentials not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_push_to_notion_no_credentials(self, sample_papers):
        """Test push_to_notion without credentials"""
        from cite_agent.integrations import push_to_notion

        with patch.dict('os.environ', {}, clear=True):
            result = await push_to_notion(sample_papers)

            assert result["success"] is False
            assert "credentials not found" in result["message"].lower()


class TestIntegrationCommands:
    """Test CLI integration commands"""

    def test_format_integration_result_success(self):
        """Test formatting successful results"""
        from cite_agent.integration_commands import format_integration_result

        result = {
            "success": True,
            "message": "Added 5 papers",
            "added": 5,
            "failed": 0
        }

        output = format_integration_result(result)

        assert "✅" in output
        assert "Added 5 papers" in output
        assert "Added: 5" in output

    def test_format_integration_result_partial(self):
        """Test formatting partial success results"""
        from cite_agent.integration_commands import format_integration_result

        result = {
            "success": False,
            "message": "Added 3/5 papers (2 failed)",
            "added": 3,
            "failed": 2,
            "errors": [
                {"paper": "Paper A", "error": "Duplicate"},
                {"paper": "Paper B", "error": "Invalid DOI"}
            ]
        }

        output = format_integration_result(result)

        assert "❌" in output
        assert "2 failed" in output or "Failed: 2" in output

    def test_format_integration_result_failure(self):
        """Test formatting failure results"""
        from cite_agent.integration_commands import format_integration_result

        result = {
            "success": False,
            "message": "Authentication failed"
        }

        output = format_integration_result(result)

        assert "❌" in output
        assert "Authentication failed" in output


# Integration test (requires real credentials - skip by default)
@pytest.mark.skip(reason="Requires real API credentials")
@pytest.mark.asyncio
async def test_zotero_real_connection():
    """Test real Zotero connection (requires credentials)"""
    from cite_agent.integrations import ZoteroClient, ZoteroConfig

    config = ZoteroConfig.from_env()
    async with ZoteroClient(config) as client:
        result = await client.test_connection()
        assert result["success"] is True


@pytest.mark.skip(reason="Requires real API credentials")
@pytest.mark.asyncio
async def test_notion_real_connection():
    """Test real Notion connection (requires credentials)"""
    from cite_agent.integrations import NotionClient, NotionConfig

    config = NotionConfig.from_env()
    async with NotionClient(config) as client:
        result = await client.test_connection()
        assert result["success"] is True
