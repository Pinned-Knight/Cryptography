# Google Docs MCP Server

An MCP (Model Context Protocol) server that lets Claude create, read, and edit
your Google Docs — authenticated entirely from your phone, no desktop browser needed.

## Tools available

| Tool | Description |
|------|-------------|
| `list_documents` | List your Google Docs (with optional search) |
| `create_document` | Create a new Google Doc with optional initial content |
| `get_document` | Read the full text of a document |
| `append_text` | Append text to the end of a document |
| `replace_text` | Find-and-replace text across a document |
| `set_content` | Overwrite all content in a document |
| `delete_document` | Permanently delete a document |

---

## Setup

### 1. Enable Google APIs (on your phone or any browser)

1. Open [console.cloud.google.com](https://console.cloud.google.com).
2. Create or select a project.
3. **APIs & Services → Library** → enable **Google Docs API** and **Google Drive API**.

### 2. Create OAuth credentials

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
2. Choose the client type based on which auth method you prefer:

   | Method | Client type to choose | Experience |
   |--------|-----------------------|------------|
   | **Device flow** (recommended) | `TVs and Limited Input devices` | Short code shown in terminal → enter on phone, tap your account. No paste needed. |
   | **Console flow** | `Desktop app` | URL printed in terminal → open on phone, approve, paste the short code back. |

3. Download the JSON file and save it as `credentials.json` in this folder
   (or anywhere — just set `GOOGLE_CREDENTIALS_FILE` to its path).

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Authenticate (one-time, from your phone)

Run the auth script once. It will never open a browser on your machine.

**Device flow** (recommended — no copy-paste):
```bash
python auth.py --method device --credentials credentials.json
```
```
======================================================
  Open on your phone : https://google.com/device
  Enter this code    : XXXX-XXXX
======================================================
Waiting for you to approve on your phone...
```
Open `https://google.com/device` on your phone, enter the code, and tap your Google account. Done.

**Console flow** (if you used Desktop app credentials):
```bash
python auth.py --method console --credentials credentials.json
```
Paste the URL into your phone's browser, approve, then paste the code back into the terminal.

The token is saved to `~/.google_docs_mcp_token.json`. Future runs (and token refreshes)
are automatic — you won't need to re-authenticate unless you revoke access.

### 5. Configure Claude Code

Add this to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "python",
      "args": ["/absolute/path/to/google-docs-mcp/server.py"]
    }
  }
}
```

Restart Claude Code. The server uses the saved token automatically.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | Path to your OAuth client JSON |
| `GOOGLE_TOKEN_FILE` | `~/.google_docs_mcp_token.json` | Where the access token is stored |

---

## Re-authenticating

If you ever need to re-auth (e.g. you revoked access):
```bash
python auth.py --method device --credentials credentials.json
```

---

## Usage examples

Once connected, ask Claude things like:

- *"List my recent Google Docs"*
- *"Create a doc called 'Meeting Notes' with today's agenda"*
- *"Read the document with ID `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms`"*
- *"Append a summary section to my report doc"*
- *"Replace 'Q3' with 'Q4' everywhere in the budget doc"*
- *"Search my docs for anything about the project proposal"*

The document ID is the string in a Google Docs URL:
`https://docs.google.com/document/d/**<document_id>**/edit`
