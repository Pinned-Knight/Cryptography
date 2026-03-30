# Google Docs MCP Server

An MCP (Model Context Protocol) server that lets Claude create, read, and edit your Google Docs.

## Tools available

| Tool | Description |
|------|-------------|
| `list_documents` | List your Google Docs, with optional search filter |
| `create_document` | Create a new Google Doc with optional initial content |
| `get_document` | Read the full text of a document |
| `append_text` | Append text to the end of a document |
| `replace_text` | Find-and-replace text across a document |
| `set_content` | Overwrite all content in a document |
| `delete_document` | Permanently delete a document |

---

## Setup

### 1. Enable the Google APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or select an existing one).
3. Go to **APIs & Services → Library** and enable:
   - **Google Docs API**
   - **Google Drive API**

### 2. Create OAuth 2.0 credentials

1. Go to **APIs & Services → Credentials**.
2. Click **Create Credentials → OAuth client ID**.
3. Choose **Desktop app**, give it a name, and click **Create**.
4. Download the JSON file and save it as `credentials.json` in this directory
   (or set `GOOGLE_CREDENTIALS_FILE` to its path).

> **First run**: A browser window will open for you to log in and grant access.
> The token is saved to `~/.google_docs_mcp_token.json` for reuse.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Claude Code

Add this server to your Claude Code MCP config. Edit `~/.claude/mcp.json`
(or `claude_desktop_config.json` for the desktop app):

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "python",
      "args": ["/absolute/path/to/google-docs-mcp/server.py"],
      "env": {
        "GOOGLE_CREDENTIALS_FILE": "/absolute/path/to/google-docs-mcp/credentials.json"
      }
    }
  }
}
```

Restart Claude Code after editing the config.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` (current dir) | Path to your OAuth client JSON |
| `GOOGLE_TOKEN_FILE` | `~/.google_docs_mcp_token.json` | Where the access token is stored |

---

## Usage examples

Once connected, you can ask Claude things like:

- *"List my recent Google Docs"*
- *"Create a new doc called 'Meeting Notes' with today's agenda"*
- *"Read the doc with ID `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms`"*
- *"Append a summary section to my doc"*
- *"Replace all occurrences of 'Q3' with 'Q4' in the report doc"*
- *"Overwrite the draft doc with this new version"*

The document ID is the long string in a Google Docs URL:
`https://docs.google.com/document/d/**<document_id>**/edit`
