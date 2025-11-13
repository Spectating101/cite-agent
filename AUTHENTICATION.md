# Authentication Guide: How Users "Login" to Integrations

This guide shows exactly how users connect their Zotero, Mendeley, and Notion accounts to cite-agent.

---

## 🎯 Quick Summary

**No traditional "username/password" login.** Instead, users use **API tokens** that they generate once from each service.

**Authentication is a one-time 5-minute setup:**
1. Run `cite-agent --setup-integrations`
2. Follow prompts to get API keys
3. Paste them when asked
4. Done! Works forever (until token revoked)

**Credentials stored in:** `~/.cite-agent.env` (secure, user-only file)

---

## 📚 Step-by-Step: First-Time Setup

### For Your Professor Who Uses Zotero

**Step 1: Run Setup Command**
```bash
cite-agent --setup-integrations
```

**Step 2: Follow Interactive Prompts**

The wizard will show:
```
═══════════════════════════════════════════════════
  Academic Tool Integration Setup
═══════════════════════════════════════════════════

Current status:
  Zotero: ❌ Not configured
  Notion: ❌ Not configured
  Mendeley: ❌ Not configured

────────────────────────────────────────────────────
Zotero Setup
────────────────────────────────────────────────────

1. Go to: https://www.zotero.org/settings/keys
2. Click 'Create new private key'
3. Name: 'cite-agent'
4. Permissions: Allow library access, Allow write access
5. Click 'Save Key'
6. Copy the API key

Paste your Zotero API key (or press Enter to skip): █
```

**Step 3: User Visits Link and Gets API Key**

On Zotero website:
- Logs in to their Zotero account
- Goes to Settings → API Keys
- Creates new key with write permissions
- Copies the generated key (looks like: `a1b2c3d4e5f6...`)

**Step 4: User Pastes API Key**
```bash
Paste your Zotero API key: a1b2c3d4e5f6g7h8i9j0

Now we need your Zotero User ID:
1. Go to: https://www.zotero.org/settings/keys
2. Look for 'Your userID for use in API calls is XXXXXX'

Enter your Zotero User ID: 123456

✅ Zotero credentials saved to /home/user/.cite-agent.env
```

**Step 5: Test Connection**
```bash
cite-agent --test-integrations

Zotero: ✅ Connected to Zotero library (2,451 items)
```

**Done!** Now they can use it:
```bash
cite-agent "transformers NLP" --push-to zotero
# Papers appear instantly in their Zotero library
```

---

## 🔐 What Gets Saved?

**File:** `~/.cite-agent.env` (in user's home directory)

**Permissions:** 600 (user can read/write, nobody else can access)

**Contents:**
```bash
# Zotero Integration
ZOTERO_API_KEY=a1b2c3d4e5f6g7h8i9j0
ZOTERO_USER_ID=123456

# Notion Integration
NOTION_API_KEY=secret_abc123def456
NOTION_DATABASE_ID=789xyz

# Mendeley Integration
MENDELEY_CLIENT_ID=123
MENDELEY_CLIENT_SECRET=abc
MENDELEY_ACCESS_TOKEN=token_xyz
```

**Security:**
- File is readable only by the user (chmod 600)
- Never transmitted except to official APIs
- Can be revoked anytime from provider dashboards
- No password storage - only API tokens

---

## 📝 Notion Setup (If They Want Notion)

**Step 1: Create Integration**
```bash
cite-agent --setup-integrations
# Choose Notion when prompted
```

Prompts show:
```
────────────────────────────────────────────────────
Notion Setup
────────────────────────────────────────────────────

1. Go to: https://www.notion.so/my-integrations
2. Click '+ New integration'
3. Name: 'cite-agent'
4. Select workspace and submit
5. Copy the 'Internal Integration Token'

6. Go to your Notion page for research papers
7. Click '...' → 'Add connections' → Select 'cite-agent'

Paste your Notion Integration Token (or press Enter to skip): █
```

**Step 2: User Creates Integration**
- Visits Notion integrations page
- Creates new integration named "cite-agent"
- Copies secret token (looks like: `secret_abc123...`)

**Step 3: User Shares Database**
- Goes to their research database in Notion
- Clicks "..." menu → "Add connections"
- Selects "cite-agent"

**Step 4: Paste Token**
```bash
Paste your Notion Integration Token: secret_abc123def456

Optional: Enter your Notion database ID
(Find it in the database URL after the workspace name)

Enter Notion database ID (or press Enter to skip): 789xyz

✅ Notion credentials saved to /home/user/.cite-agent.env
```

**Done!** Now they can push papers to Notion:
```bash
cite-agent "sustainable finance" --push-to notion
# Creates beautiful pages in their Notion database
```

---

## 🔓 Mendeley Setup (OAuth - Slightly More Complex)

**Step 1: Create App**
```bash
cite-agent --setup-integrations
# Choose Mendeley when prompted
```

Shows:
```
────────────────────────────────────────────────────
Mendeley Setup
────────────────────────────────────────────────────

Mendeley requires OAuth 2.0 (more complex)

Setup steps:
1. Go to: https://dev.mendeley.com/myapps.html
2. Create new app: 'cite-agent'
3. Redirect URL: http://localhost:8080/callback
4. Copy Client ID and Client Secret

Enter Mendeley Client ID (or press Enter to skip): █
```

**Step 2: User Registers App**
- Goes to Mendeley developer portal
- Creates app with callback URL
- Gets Client ID and Secret

**Step 3: Paste Credentials**
```bash
Enter Mendeley Client ID: 123
Enter Mendeley Client Secret: abc456

✅ Mendeley app credentials saved to /home/user/.cite-agent.env

To complete setup, run: cite-agent --authorize-mendeley
```

**Step 4: Run OAuth Authorization**
```bash
cite-agent --authorize-mendeley
```

This:
1. Opens browser automatically
2. User logs in to Mendeley
3. Approves "cite-agent" access
4. Gets redirected to localhost with code
5. User copies code from URL
6. Pastes into terminal
7. Token saved automatically

```
═══════════════════════════════════════════════════
  Mendeley OAuth Authorization
═══════════════════════════════════════════════════

Opening browser for authorization...

After authorizing, you'll be redirected to:
http://localhost:8080/callback?code=XXXXX

Paste the 'code' parameter from the URL: XXXXX

✅ Successfully authorized Mendeley!
   Credentials saved to /home/user/.cite-agent.env
```

**Done!** Can now use Mendeley:
```bash
cite-agent "machine learning healthcare" --push-to mendeley
```

---

## 🧪 Testing Connections

**Anytime users want to check if their authentication is working:**
```bash
cite-agent --test-integrations

Testing integrations...

Zotero: ✅ Connected to Zotero library (2,451 items)
Notion: ✅ Connected to Notion (User: John Smith)
Mendeley: ✅ Connected to Mendeley (User: Jane Doe)
```

If any fail:
```bash
Zotero: ❌ Zotero credentials not found. Set ZOTERO_API_KEY and ZOTERO_USER_ID.
Get API key from: https://www.zotero.org/settings/keys
```

**Fix:** Just run `cite-agent --setup-integrations` again to reconfigure.

---

## 💡 User Experience Design

### What Makes This Good UX:

1. **No Manual Environment Variables**
   - Don't need to know what `export` means
   - Don't need to edit `.bashrc` or `.zshrc`
   - Just run setup wizard once

2. **Clear Step-by-Step Guidance**
   - Links to exact pages
   - Screenshots in INTEGRATIONS.md
   - Can't get lost

3. **Persistent Across Sessions**
   - Setup once, works forever
   - No need to "login" every time
   - Credentials load automatically

4. **Easy Testing**
   - `--test-integrations` shows status
   - Clear error messages
   - Link to reconfigure if needed

5. **Secure by Default**
   - File permissions set to 600 automatically
   - Only user can read credentials
   - Standard location (~/.cite-agent.env)

---

## 🔄 Updating/Revoking Credentials

**If user wants to change API key:**
```bash
# Option 1: Rerun setup
cite-agent --setup-integrations

# Option 2: Edit file directly
nano ~/.cite-agent.env
```

**If user wants to revoke access:**
1. Go to provider website (Zotero/Notion/Mendeley)
2. Delete the "cite-agent" API key/integration
3. cite-agent will show authentication error
4. Run `cite-agent --setup-integrations` to reconfigure

---

## 📞 Common Questions

**Q: Do I need to login every time I use cite-agent?**
A: No! Setup once, credentials persist forever (until revoked).

**Q: Is my password stored?**
A: No! Only API tokens (not passwords). Tokens can be revoked anytime.

**Q: What if I don't want to use Zotero?**
A: Just skip it during setup. You can configure only the tools you use.

**Q: Can I use cite-agent without any integrations?**
A: Yes! Integrations are optional. You can still search papers and get responses without pushing to any tool.

**Q: Where is my data stored?**
A: Credentials: `~/.cite-agent.env` (secure, local file)
Papers: Your Zotero/Mendeley/Notion accounts (not on cite-agent servers)

**Q: Is this secure?**
A: Yes:
- File permissions: 600 (user-only)
- Tokens (not passwords) stored
- Can be revoked anytime
- Direct API calls (no cite-agent middleman)

---

## 🎓 Example: Professor's First Use

**Professor receives email:**
> "Try cite-agent! Install with: pip install cite-agent"

**Professor runs:**
```bash
pip install cite-agent
cite-agent --setup-integrations
```

**Setup wizard (5 minutes):**
1. Opens Zotero settings in browser
2. Creates API key
3. Copies and pastes
4. Done

**First query:**
```bash
cite-agent "ESG investing performance" --push-to zotero
```

**Result:**
```
🤖 Processing: ESG investing performance

📝 Response:
Found 5 papers on ESG investing performance:
1. "ESG and Financial Performance" (Friede et al., 2023)
   ...

🔄 Pushing to Zotero...
✅ Added to Zotero: ESG and Financial Performance
   View: https://www.zotero.org/users/123456/items/ABC123

📊 Tokens used: 234 (Daily usage: 2.3%)
```

**Professor opens Zotero:**
- Paper appears instantly
- Title, authors, abstract all filled in
- Ready to cite in Word

**Professor's reaction:** 🤯 "This is magic!"

---

**Bottom line:** Authentication is a one-time, 5-minute interactive setup. No technical knowledge required. Works like installing an app on your phone — authenticate once, use forever.
