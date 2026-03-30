#!/usr/bin/env python3
"""
Google Docs MCP Server
Provides tools for Claude to create, read, and edit Google Docs.
"""

import asyncio
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes required
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

TOKEN_FILE = Path(os.environ.get("GOOGLE_TOKEN_FILE", Path.home() / ".google_docs_mcp_token.json"))
CREDENTIALS_FILE = Path(os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json"))

server = Server("google-docs-mcp")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_credentials() -> Credentials:
    """Load, refresh, or create OAuth2 credentials."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Google OAuth credentials file not found: {CREDENTIALS_FILE}\n"
                    "Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return creds


def docs_service():
    return build("docs", "v1", credentials=get_credentials())


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def extract_text(doc: dict) -> str:
    """Convert a Docs API document body to a plain-text string."""
    parts: list[str] = []
    for elem in doc.get("body", {}).get("content", []):
        paragraph = elem.get("paragraph")
        if paragraph:
            for pe in paragraph.get("elements", []):
                tr = pe.get("textRun")
                if tr:
                    parts.append(tr.get("content", ""))
    return "".join(parts)


def doc_end_index(doc: dict) -> int:
    """Return the last writable index in a document body."""
    content = doc["body"]["content"]
    return content[-1]["endIndex"] - 1


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_documents",
            description=(
                "List Google Docs documents in your Drive. "
                "Optionally filter by a search query."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Full-text search query to filter documents (optional).",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 20).",
                        "default": 20,
                    },
                },
            },
        ),
        types.Tool(
            name="create_document",
            description="Create a new Google Docs document with an optional initial body.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the new document.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Initial text content to insert (optional).",
                    },
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="get_document",
            description="Read the full text content of a Google Docs document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The Google Docs document ID (from its URL).",
                    },
                },
                "required": ["document_id"],
            },
        ),
        types.Tool(
            name="append_text",
            description="Append text to the end of a Google Docs document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The Google Docs document ID.",
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to append.",
                    },
                },
                "required": ["document_id", "text"],
            },
        ),
        types.Tool(
            name="replace_text",
            description="Find and replace all occurrences of a string in a Google Doc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The Google Docs document ID.",
                    },
                    "find": {
                        "type": "string",
                        "description": "Text to search for.",
                    },
                    "replace": {
                        "type": "string",
                        "description": "Replacement text.",
                    },
                    "match_case": {
                        "type": "boolean",
                        "description": "Case-sensitive match (default true).",
                        "default": True,
                    },
                },
                "required": ["document_id", "find", "replace"],
            },
        ),
        types.Tool(
            name="set_content",
            description=(
                "Overwrite ALL content in a Google Docs document with new text. "
                "This erases existing content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The Google Docs document ID.",
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the document.",
                    },
                },
                "required": ["document_id", "content"],
            },
        ),
        types.Tool(
            name="delete_document",
            description="Permanently delete a Google Docs document from Drive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The Google Docs document ID to delete.",
                    },
                },
                "required": ["document_id"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    try:
        match name:
            case "list_documents":
                return _list_documents(arguments)
            case "create_document":
                return _create_document(arguments)
            case "get_document":
                return _get_document(arguments)
            case "append_text":
                return _append_text(arguments)
            case "replace_text":
                return _replace_text(arguments)
            case "set_content":
                return _set_content(arguments)
            case "delete_document":
                return _delete_document(arguments)
            case _:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    except HttpError as exc:
        return [types.TextContent(type="text", text=f"Google API error: {exc}")]
    except FileNotFoundError as exc:
        return [types.TextContent(type="text", text=str(exc))]
    except Exception as exc:
        return [types.TextContent(type="text", text=f"Error: {exc}")]


def _list_documents(args: dict) -> list[types.TextContent]:
    drive = drive_service()
    q = "mimeType='application/vnd.google-apps.document' and trashed=false"
    if args.get("query"):
        safe_q = args["query"].replace("'", "\\'")
        q += f" and fullText contains '{safe_q}'"

    results = drive.files().list(
        q=q,
        pageSize=args.get("max_results", 20),
        fields="files(id, name, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
    ).execute()

    files = results.get("files", [])
    if not files:
        return [types.TextContent(type="text", text="No documents found.")]

    lines = [f"Found {len(files)} document(s):\n"]
    for f in files:
        lines.append(f"**{f['name']}**")
        lines.append(f"  ID: `{f['id']}`")
        lines.append(f"  Modified: {f.get('modifiedTime', 'unknown')}")
        lines.append(f"  URL: {f.get('webViewLink', 'N/A')}\n")

    return [types.TextContent(type="text", text="\n".join(lines))]


def _create_document(args: dict) -> list[types.TextContent]:
    docs = docs_service()
    title = args["title"]

    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    if args.get("content"):
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": args["content"]}}]},
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return [types.TextContent(type="text", text=f"Created **{title}**\nID: `{doc_id}`\nURL: {url}")]


def _get_document(args: dict) -> list[types.TextContent]:
    docs = docs_service()
    doc = docs.documents().get(documentId=args["document_id"]).execute()
    title = doc.get("title", "Untitled")
    text = extract_text(doc)
    return [types.TextContent(type="text", text=f"# {title}\n\n{text}")]


def _append_text(args: dict) -> list[types.TextContent]:
    docs = docs_service()
    doc_id = args["document_id"]
    doc = docs.documents().get(documentId=doc_id).execute()
    index = doc_end_index(doc)

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": index}, "text": args["text"]}}]},
    ).execute()
    return [types.TextContent(type="text", text=f"Text appended to `{doc_id}`.")]


def _replace_text(args: dict) -> list[types.TextContent]:
    docs = docs_service()
    docs.documents().batchUpdate(
        documentId=args["document_id"],
        body={
            "requests": [{
                "replaceAllText": {
                    "containsText": {
                        "text": args["find"],
                        "matchCase": args.get("match_case", True),
                    },
                    "replaceText": args["replace"],
                }
            }]
        },
    ).execute()
    return [types.TextContent(
        type="text",
        text=f"Replaced '{args['find']}' → '{args['replace']}' in `{args['document_id']}`.",
    )]


def _set_content(args: dict) -> list[types.TextContent]:
    docs = docs_service()
    doc_id = args["document_id"]
    doc = docs.documents().get(documentId=doc_id).execute()
    end = doc_end_index(doc)

    requests: list[dict] = []
    if end > 1:
        requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end}}})
    requests.append({"insertText": {"location": {"index": 1}, "text": args["content"]}})

    docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
    return [types.TextContent(type="text", text=f"Content of `{doc_id}` replaced.")]


def _delete_document(args: dict) -> list[types.TextContent]:
    drive = drive_service()
    drive.files().delete(fileId=args["document_id"]).execute()
    return [types.TextContent(type="text", text=f"Document `{args['document_id']}` deleted.")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
