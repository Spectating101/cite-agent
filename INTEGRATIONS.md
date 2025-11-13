# Academic Tool Integrations Guide

**Direct API connectivity to Zotero, Mendeley, Notion, and more.**

Push papers directly to your reference manager or note-taking app with one command.

---

## 🎯 Supported Integrations

| Tool | Status | Push Method | Authentication |
|------|--------|-------------|----------------|
| **Zotero** | ✅ Full support | Direct API | API Key |
| **Mendeley** | ✅ Full support | Direct API | OAuth 2.0 |
| **Notion** | ✅ Full support | Direct API | Integration Token |
| **EndNote** | ⚠️ File export only | XML file | N/A |
| **Obsidian** | ✅ Full support | Markdown files | N/A |
| **NotebookLM** | ❌ Not available | N/A | No public API |

---

## 📚 Quick Start

### 1. Setup Integration Credentials

```bash
cite-agent --setup-integrations
```

This interactive wizard will guide you through:
- Getting API keys
- Configuring authentication
- Testing connections

### 2. Push Papers Directly

```bash
# Find papers and push to Zotero
cite-agent "find papers on transformers" --push-to zotero

# Push to Notion with collection
cite-agent "ESG investing papers" --push-to notion

# Push to Mendeley
cite-agent "machine learning healthcare" --push-to mendeley
```

---

## 🔐 Zotero Integration

### Setup (5 minutes)

**Step 1: Get API Key**
1. Go to [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys)
2. Click "Create new private key"
3. Name it: `cite-agent`
4. Permissions:
   - ✅ Allow library access
   - ✅ Allow write access
5. Click "Save Key"
6. Copy the API key (you'll only see it once!)

**Step 2: Get User ID**
1. On the same page, look for: "Your userID for use in API calls is `XXXXXX`"
2. Copy this number

**Step 3: Configure cite-agent**
```bash
# Set environment variables
export ZOTERO_API_KEY="your_api_key_here"
export ZOTERO_USER_ID="your_user_id_here"

# Or add to ~/.cite-agent.env
echo "ZOTERO_API_KEY=your_key" >> ~/.cite-agent.env
echo "ZOTERO_USER_ID=your_id" >> ~/.cite-agent.env
```

### Usage

**Push single paper:**
```bash
cite-agent "find BERT paper" --push-to zotero
```

**Push with collection:**
```bash
cite-agent "transformers attention" --push-to zotero --collection "Deep Learning"
```

**Push with tags:**
```bash
cite-agent "ESG papers" --push-to zotero --tags "sustainability,finance"
```

**Python API:**
```python
from cite_agent.integrations import push_to_zotero

papers = [
    {
        "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."],
        "year": 2017,
        "doi": "10.48550/arXiv.1706.03762",
        "abstract": "...",
        "venue": "NeurIPS"
    }
]

result = await push_to_zotero(papers, collection_name="Transformers")
print(result["message"])
# ✅ Added 1 papers to Zotero
```

---

## 📝 Notion Integration

### Setup (5 minutes)

**Step 1: Create Notion Integration**
1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "+ New integration"
3. Name: `cite-agent`
4. Select your workspace
5. Click "Submit"
6. Copy the "Internal Integration Token"

**Step 2: Share Database with Integration**
1. Go to your Notion page where you want to store papers
2. Click "..." menu (top right)
3. Click "Add connections"
4. Select "cite-agent"

**Step 3: Get Database ID** (optional but recommended)
1. Open the database in Notion
2. Look at the URL: `https://notion.so/workspace/XXXXXXX?v=...`
3. Copy the `XXXXXXX` part (that's your database ID)

**Step 4: Configure cite-agent**
```bash
export NOTION_API_KEY="your_integration_token"
export NOTION_DATABASE_ID="your_database_id"  # Optional

# Or add to ~/.cite-agent.env
echo "NOTION_API_KEY=your_token" >> ~/.cite-agent.env
echo "NOTION_DATABASE_ID=your_db_id" >> ~/.cite-agent.env
```

### Usage

**Push to default database:**
```bash
cite-agent "machine learning papers" --push-to notion
```

**Push to specific database:**
```bash
cite-agent "ESG research" --push-to notion --database "abc123def456"
```

**Python API:**
```python
from cite_agent.integrations import push_to_notion

papers = [...]  # Your papers

result = await push_to_notion(papers, database_id="your_db_id")
print(result["message"])
```

**What gets created in Notion:**
- Page title: Paper title
- Properties: Authors, Year, DOI, Citations, Venue, Tags
- Content blocks: Abstract, Notes section, Key Findings section

---

## 📖 Mendeley Integration

### Setup (10 minutes - OAuth required)

**Step 1: Register App**
1. Go to [https://dev.mendeley.com/myapps.html](https://dev.mendeley.com/myapps.html)
2. Click "Create new app"
3. Name: `cite-agent`
4. Description: "CLI research assistant"
5. Redirect URL: `http://localhost:8080/callback`
6. Click "Create"
7. Copy Client ID and Client Secret

**Step 2: Configure cite-agent**
```bash
export MENDELEY_CLIENT_ID="your_client_id"
export MENDELEY_CLIENT_SECRET="your_client_secret"

# Or add to ~/.cite-agent.env
echo "MENDELEY_CLIENT_ID=your_id" >> ~/.cite-agent.env
echo "MENDELEY_CLIENT_SECRET=your_secret" >> ~/.cite-agent.env
```

**Step 3: Authorize** (one-time)
```bash
cite-agent --authorize-mendeley
```

This will:
1. Open your browser
2. Ask you to log in to Mendeley
3. Request permission to access your library
4. Return an access token
5. Save the token automatically

### Usage

**Push papers:**
```bash
cite-agent "deep learning papers" --push-to mendeley
```

**Python API:**
```python
from cite_agent.integrations import push_to_mendeley

result = await push_to_mendeley(papers, folder_id="optional_folder")
print(result["message"])
```

---

## 🎨 Obsidian Integration

Obsidian doesn't have an API (it's file-based), but cite-agent can create perfectly formatted markdown files with backlinks.

### Setup

No API key needed! Just set your Obsidian vault path:

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/ObsidianVault"
```

### Usage

**Export with backlinks:**
```bash
cite-agent "find AI papers" --export obsidian
```

**What you get:**
```markdown
---
title: Attention Is All You Need
authors: Vaswani, Shazeer, Parmar
year: 2017
tags: transformers, attention, nlp
citation_count: 70000
---

# Attention Is All You Need

**Authors:** [[Vaswani]] · [[Shazeer]] · [[Parmar]]

**Year:** 2017 · **Citations:** 70,000

**Published in:** [[NeurIPS]]

**Tags:** #transformers #attention #nlp

## Abstract

We propose a new simple network architecture...

## Notes

*Add your notes here*

## Related Papers

- [[BERT]]
- [[GPT-3]]
```

Files are saved to: `$OBSIDIAN_VAULT_PATH/Papers/AuthorYear-Title.md`

---

## 🚀 Advanced Usage

### Batch Push Multiple Tools

```bash
# Find papers once, push to multiple tools
cite-agent "transformers NLP" \
  --push-to zotero \
  --push-to notion \
  --export obsidian
```

### Programmatic Usage

```python
from cite_agent import EnhancedNocturnalAgent
from cite_agent.integrations import push_to_zotero, push_to_notion

async def research_workflow():
    # Step 1: Find papers
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    result = await agent.search_academic_papers("machine learning healthcare", limit=20)
    papers = result.get("papers", [])

    # Step 2: Push to Zotero
    zotero_result = await push_to_zotero(
        papers,
        collection_name="ML Healthcare",
        tags=["machine-learning", "healthcare"]
    )
    print(zotero_result["message"])

    # Step 3: Push to Notion for notes
    notion_result = await push_to_notion(papers)
    print(notion_result["message"])

    await agent.close()
```

### Error Handling

```python
result = await push_to_zotero(papers)

if result["success"]:
    print(f"✅ {result['message']}")
    if result.get("failed", 0) > 0:
        print(f"⚠️ {result['failed']} papers failed")
        for error in result.get("errors", []):
            print(f"  - {error['paper']}: {error['error']}")
else:
    print(f"❌ {result['message']}")
```

---

## 🔧 Troubleshooting

### Zotero: "Authentication failed"

**Check:**
1. API key is correct (no extra spaces)
2. User ID is correct (numeric only)
3. API key has write permissions

**Test connection:**
```bash
cite-agent --test-integrations
```

### Notion: "Database not found"

**Fix:**
1. Make sure you shared the database with your integration
2. Check database ID is correct
3. Try creating a new database:
   ```python
   from cite_agent.integrations import NotionClient
   client = NotionClient.from_env()
   result = await client.create_database(parent_page_id="...")
   ```

### Mendeley: "OAuth failed"

**Common issues:**
1. Redirect URL must be EXACTLY: `http://localhost:8080/callback`
2. Make sure you copy the full authorization code
3. Code expires after 10 minutes - request a new one

**Re-authorize:**
```bash
cite-agent --authorize-mendeley
```

---

## 📊 Feature Comparison

| Feature | Zotero | Mendeley | Notion |
|---------|--------|----------|--------|
| Push papers | ✅ | ✅ | ✅ |
| Collections/Folders | ✅ | ✅ | ✅ via properties |
| Tags | ✅ | ✅ | ✅ |
| Notes | ✅ | ✅ | ✅ (rich text) |
| PDFs | ❌ (metadata only) | ❌ (metadata only) | ❌ |
| Collaboration | ✅ Groups | ✅ Groups | ✅ Shared pages |
| Desktop sync | ✅ Auto | ✅ Auto | ✅ Auto |
| Mobile access | ✅ iOS/Android | ✅ iOS/Android | ✅ iOS/Android |
| Citation formats | ✅ 9000+ styles | ✅ 9000+ styles | ❌ Manual |
| Word plugin | ✅ | ✅ | ❌ |

---

## 💡 Recommended Workflows

### For Literature Review
```bash
# Find papers on topic
cite-agent "sustainable finance ESG" \
  --push-to zotero \
  --collection "Thesis - Literature Review" \
  --tags "esg,sustainability,finance"

# Export to Notion for note-taking
cite-agent --last-results --push-to notion
```

### For Reading List
```bash
# Find influential papers
cite-agent "seminal papers deep learning" \
  --push-to mendeley \
  --folder "To Read"

# Also save to Obsidian for annotations
cite-agent --last-results --export obsidian
```

### For Team Collaboration
```bash
# Push to shared Zotero group
export ZOTERO_LIBRARY_TYPE=group
export ZOTERO_GROUP_ID=12345

cite-agent "COVID-19 economics" --push-to zotero
```

---

## 🔒 Security & Privacy

**API Keys:**
- Stored in `~/.cite-agent.env` (permissions: 600)
- Never logged or transmitted except to official APIs
- Can be revoked anytime from provider dashboards

**Data Privacy:**
- Paper metadata only (no PDFs uploaded)
- Direct API calls (no cite-agent servers involved)
- Local file reading stays local

**Best Practices:**
1. Don't commit `.env` files to git
2. Use separate API keys for different projects
3. Revoke unused keys regularly
4. Enable 2FA on your Zotero/Mendeley/Notion accounts

---

## 📞 Support

**Questions?**
- Zotero API docs: https://www.zotero.org/support/dev/web_api/v3/start
- Mendeley API docs: https://dev.mendeley.com/
- Notion API docs: https://developers.notion.com/

**Issues?**
```bash
cite-agent --test-integrations  # Diagnose problems
```

Report bugs: https://github.com/Spectating101/cite-agent/issues

---

**Built for researchers who want seamless tool integration.** 🚀
