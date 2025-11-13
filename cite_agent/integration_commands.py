#!/usr/bin/env python3
"""
CLI commands for academic tool integrations
Provides easy access to Zotero, Mendeley, Notion APIs
"""

import asyncio
import os
from typing import List, Dict, Any, Optional

from cite_agent.integrations import (
    ZoteroClient,
    NotionClient,
    MendeleyClient,
    push_to_zotero,
    push_to_notion,
    push_to_mendeley
)


def setup_integration_credentials():
    """
    Interactive setup for integration credentials

    Guides user through setting up:
    - Zotero API key
    - Notion API key
    - Mendeley OAuth
    """
    print("=" * 60)
    print("  Academic Tool Integration Setup")
    print("=" * 60)
    print()

    # Check existing credentials
    has_zotero = os.getenv("ZOTERO_API_KEY") and os.getenv("ZOTERO_USER_ID")
    has_notion = os.getenv("NOTION_API_KEY")
    has_mendeley = os.getenv("MENDELEY_ACCESS_TOKEN")

    print("Current status:")
    print(f"  Zotero: {'✅ Configured' if has_zotero else '❌ Not configured'}")
    print(f"  Notion: {'✅ Configured' if has_notion else '❌ Not configured'}")
    print(f"  Mendeley: {'✅ Configured' if has_mendeley else '❌ Not configured'}")
    print()

    # Zotero setup
    if not has_zotero:
        print("─" * 60)
        print("Zotero Setup")
        print("─" * 60)
        print()
        print("1. Go to: https://www.zotero.org/settings/keys")
        print("2. Click 'Create new private key'")
        print("3. Name: 'cite-agent'")
        print("4. Permissions: Allow library access, Allow write access")
        print("5. Copy the API key")
        print()

        api_key = input("Paste your Zotero API key (or press Enter to skip): ").strip()

        if api_key:
            print()
            print("Now we need your Zotero User ID:")
            print("1. Go to: https://www.zotero.org/settings/keys")
            print("2. Look for 'Your userID for use in API calls is XXXXXX'")
            print()

            user_id = input("Enter your Zotero User ID: ").strip()

            if user_id:
                # Save to env file
                env_file = os.path.expanduser("~/.cite-agent.env")
                with open(env_file, "a") as f:
                    f.write(f"\n# Zotero Integration\n")
                    f.write(f"ZOTERO_API_KEY={api_key}\n")
                    f.write(f"ZOTERO_USER_ID={user_id}\n")

                print(f"✅ Zotero credentials saved to {env_file}")
                print()

    # Notion setup
    if not has_notion:
        print("─" * 60)
        print("Notion Setup")
        print("─" * 60)
        print()
        print("1. Go to: https://www.notion.so/my-integrations")
        print("2. Click '+ New integration'")
        print("3. Name: 'cite-agent'")
        print("4. Select workspace and submit")
        print("5. Copy the 'Internal Integration Token'")
        print()
        print("6. Go to your Notion page for research papers")
        print("7. Click '...' → 'Add connections' → Select 'cite-agent'")
        print()

        api_key = input("Paste your Notion Integration Token (or press Enter to skip): ").strip()

        if api_key:
            print()
            print("Optional: Enter your Notion database ID")
            print("(Find it in the database URL after the workspace name)")
            print()

            database_id = input("Enter Notion database ID (or press Enter to skip): ").strip()

            # Save to env file
            env_file = os.path.expanduser("~/.cite-agent.env")
            with open(env_file, "a") as f:
                f.write(f"\n# Notion Integration\n")
                f.write(f"NOTION_API_KEY={api_key}\n")
                if database_id:
                    f.write(f"NOTION_DATABASE_ID={database_id}\n")

            print(f"✅ Notion credentials saved to {env_file}")
            print()

    # Mendeley setup (more complex due to OAuth)
    if not has_mendeley:
        print("─" * 60)
        print("Mendeley Setup")
        print("─" * 60)
        print()
        print("Mendeley requires OAuth 2.0 (more complex)")
        print()
        print("Setup steps:")
        print("1. Go to: https://dev.mendeley.com/myapps.html")
        print("2. Create new app: 'cite-agent'")
        print("3. Redirect URL: http://localhost:8080/callback")
        print("4. Copy Client ID and Client Secret")
        print()

        client_id = input("Enter Mendeley Client ID (or press Enter to skip): ").strip()

        if client_id:
            client_secret = input("Enter Mendeley Client Secret: ").strip()

            # Save to env file
            env_file = os.path.expanduser("~/.cite-agent.env")
            with open(env_file, "a") as f:
                f.write(f"\n# Mendeley Integration\n")
                f.write(f"MENDELEY_CLIENT_ID={client_id}\n")
                f.write(f"MENDELEY_CLIENT_SECRET={client_secret}\n")

            print(f"✅ Mendeley app credentials saved to {env_file}")
            print()
            print("To complete setup, run: cite-agent --authorize-mendeley")
            print()

    print("=" * 60)
    print("Setup complete! Integration credentials saved.")
    print()
    print("To use integrations:")
    print("  cite-agent 'find papers on AI' --push-to zotero")
    print("  cite-agent 'search ESG papers' --push-to notion")
    print("=" * 60)


async def test_integrations():
    """Test all configured integrations"""
    print("Testing integrations...")
    print()

    # Test Zotero
    try:
        from cite_agent.integrations.zotero_client import ZoteroConfig, ZoteroClient

        config = ZoteroConfig.from_env()
        async with ZoteroClient(config) as client:
            result = await client.test_connection()
            print(f"Zotero: {result['message']}")
    except Exception as e:
        print(f"Zotero: ❌ {str(e)}")

    # Test Notion
    try:
        from cite_agent.integrations.notion_client import NotionConfig, NotionClient

        config = NotionConfig.from_env()
        async with NotionClient(config) as client:
            result = await client.test_connection()
            print(f"Notion: {result['message']}")
    except Exception as e:
        print(f"Notion: ❌ {str(e)}")

    # Test Mendeley
    try:
        from cite_agent.integrations.mendeley_client import MendeleyConfig, MendeleyClient

        config = MendeleyConfig.from_env()
        async with MendeleyClient(config) as client:
            result = await client.test_connection()
            print(f"Mendeley: {result['message']}")
    except Exception as e:
        print(f"Mendeley: ❌ {str(e)}")


async def push_papers_to_integration(
    papers: List[Dict[str, Any]],
    target: str,
    collection_name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Push papers to specified integration

    Args:
        papers: List of paper dicts
        target: "zotero", "notion", or "mendeley"
        collection_name: Optional collection/folder name
        tags: Optional tags to add

    Returns:
        Result dict with success status
    """
    target = target.lower()

    if target == "zotero":
        result = await push_to_zotero(papers, collection_name, tags)

    elif target == "notion":
        result = await push_to_notion(papers)

    elif target == "mendeley":
        result = await push_to_mendeley(papers)

    else:
        result = {
            "success": False,
            "message": f"Unknown target: {target}. Use 'zotero', 'notion', or 'mendeley'"
        }

    return result


def format_integration_result(result: Dict[str, Any]) -> str:
    """Format integration result for CLI output"""
    if result["success"]:
        output = f"✅ {result['message']}\n"

        if "library_url" in result:
            output += f"   View: {result['library_url']}\n"

        if "url" in result:
            output += f"   View: {result['url']}\n"

        if "added" in result and "failed" in result:
            output += f"   Added: {result['added']}, Failed: {result['failed']}\n"

        if result.get("errors"):
            output += "\n   Errors:\n"
            for error in result["errors"][:3]:  # Show first 3
                if isinstance(error, dict):
                    output += f"   - {error.get('paper', 'Unknown')}: {error.get('error', 'Unknown error')}\n"
                else:
                    output += f"   - {error}\n"

        return output
    else:
        return f"❌ {result['message']}\n"


# Mendeley OAuth flow
async def authorize_mendeley():
    """Interactive Mendeley OAuth authorization"""
    from cite_agent.integrations.mendeley_client import MendeleyConfig, MendeleyClient
    import webbrowser

    print("=" * 60)
    print("  Mendeley OAuth Authorization")
    print("=" * 60)
    print()

    try:
        config = MendeleyConfig.from_env()

        async with MendeleyClient(config) as client:
            # Get authorization URL
            redirect_uri = "http://localhost:8080/callback"
            auth_url = await client.get_authorization_url(redirect_uri)

            print("Opening browser for authorization...")
            print()
            print("If browser doesn't open, visit:")
            print(auth_url)
            print()

            # Open browser
            webbrowser.open(auth_url)

            print("After authorizing, you'll be redirected to:")
            print(f"{redirect_uri}?code=XXXXX")
            print()
            code = input("Paste the 'code' parameter from the URL: ").strip()

            if code:
                # Exchange code for token
                result = await client.exchange_code_for_token(code, redirect_uri)

                if result["success"]:
                    # Save access token
                    env_file = os.path.expanduser("~/.cite-agent.env")
                    with open(env_file, "a") as f:
                        f.write(f"MENDELEY_ACCESS_TOKEN={result['access_token']}\n")
                        if result.get("refresh_token"):
                            f.write(f"MENDELEY_REFRESH_TOKEN={result['refresh_token']}\n")

                    print()
                    print("✅ Successfully authorized Mendeley!")
                    print(f"   Credentials saved to {env_file}")
                else:
                    print(f"❌ Authorization failed: {result['message']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
