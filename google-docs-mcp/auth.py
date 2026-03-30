#!/usr/bin/env python3
"""
One-time Google OAuth sign-in for the Google Docs MCP server.

Run this script once from any terminal (phone-friendly: no desktop
browser required — just open the printed URL on your phone).

Usage:
    python auth.py [--credentials credentials.json] [--token ~/.google_docs_mcp_token.json]
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_TOKEN_FILE = Path.home() / ".google_docs_mcp_token.json"
DEFAULT_CREDENTIALS_FILE = Path("credentials.json")


# ---------------------------------------------------------------------------
# Device-flow auth (phone-friendly: no local browser required)
# ---------------------------------------------------------------------------

def _post(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read())


def device_flow(client_id: str, client_secret: str) -> dict:
    """
    OAuth 2.0 Device Authorization Grant.
    Prints a short URL + code — user enters on phone, no local browser needed.
    Requires the OAuth client to be 'TVs and Limited Input devices' type.
    """
    # Step 1 – request device code
    resp = _post(
        "https://oauth2.googleapis.com/device/code",
        {"client_id": client_id, "scope": " ".join(SCOPES)},
    )
    if "error" in resp:
        raise RuntimeError(f"Device code request failed: {resp}")

    print("\n" + "=" * 55)
    print(f"  Open on your phone : {resp['verification_url']}")
    print(f"  Enter this code    : {resp['user_code']}")
    print("=" * 55)
    print("\nWaiting for you to approve on your phone...\n")

    # Step 2 – poll until approved or expired
    interval = resp.get("interval", 5)
    deadline = time.time() + resp.get("expires_in", 1800)

    while time.time() < deadline:
        time.sleep(interval)
        token = _post(
            "https://oauth2.googleapis.com/token",
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "device_code": resp["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )
        error = token.get("error")
        if not error:
            return token
        if error == "authorization_pending":
            print("  Still waiting...", flush=True)
            continue
        if error == "slow_down":
            interval += 5
            continue
        raise RuntimeError(f"Auth failed: {token}")

    raise TimeoutError("Device authorization timed out (code expired).")


def console_flow(credentials_file: Path) -> dict:
    """
    Standard OAuth 2.0 Authorization Code flow via console.
    Prints a long URL — user opens on phone, approves, then pastes the code back.
    Works with 'Desktop app' OAuth client type.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
    creds = flow.run_console()          # prints URL, reads code from stdin
    # Return a dict matching the device-flow token shape so save_token() works
    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }


# ---------------------------------------------------------------------------
# Token persistence
# ---------------------------------------------------------------------------

def save_token(token: dict, credentials_file: Path, token_file: Path) -> None:
    """Build a google.oauth2.credentials-compatible JSON and save it."""
    # If device flow returned tokens, we still need client info
    if "client_id" not in token or "client_secret" not in token:
        creds_data = json.loads(credentials_file.read_text())
        info = creds_data.get("installed") or creds_data.get("web") or {}
        token.setdefault("client_id", info.get("client_id", ""))
        token.setdefault("client_secret", info.get("client_secret", ""))
        token.setdefault("token_uri", info.get("token_uri", "https://oauth2.googleapis.com/token"))

    token.setdefault("scopes", SCOPES)

    token_file.write_text(json.dumps(token, indent=2))
    print(f"\nToken saved to: {token_file}")
    print("You can now start the MCP server.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Authenticate with Google (phone-friendly).")
    parser.add_argument(
        "--credentials",
        default=os.environ.get("GOOGLE_CREDENTIALS_FILE", str(DEFAULT_CREDENTIALS_FILE)),
        help="Path to your OAuth credentials JSON (from Google Cloud Console).",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GOOGLE_TOKEN_FILE", str(DEFAULT_TOKEN_FILE)),
        help="Where to save the access token (default: ~/.google_docs_mcp_token.json).",
    )
    parser.add_argument(
        "--method",
        choices=["device", "console"],
        default="device",
        help=(
            "'device' (default): shows a short code — approve on phone, no paste needed. "
            "Requires 'TVs and Limited Input devices' OAuth client type. "
            "'console': prints a URL — open on phone, paste code back. "
            "Works with 'Desktop app' OAuth client type."
        ),
    )
    args = parser.parse_args()

    credentials_file = Path(args.credentials)
    token_file = Path(args.token)

    if not credentials_file.exists():
        print(
            f"ERROR: credentials file not found: {credentials_file}\n\n"
            "To get it:\n"
            "  1. Go to console.cloud.google.com (works on phone)\n"
            "  2. APIs & Services → Credentials → Create Credentials → OAuth client ID\n"
            "  3. For --method device : choose 'TVs and Limited Input devices'\n"
            "     For --method console: choose 'Desktop app'\n"
            "  4. Download the JSON and pass it via --credentials\n",
            file=sys.stderr,
        )
        sys.exit(1)

    creds_data = json.loads(credentials_file.read_text())
    info = creds_data.get("installed") or creds_data.get("web") or {}
    client_id = info.get("client_id", "")
    client_secret = info.get("client_secret", "")

    if args.method == "device":
        print("Using device flow (phone-friendly, no paste needed)...")
        token = device_flow(client_id, client_secret)
    else:
        print("Using console flow (open URL on phone, paste code here)...")
        token = console_flow(credentials_file)

    save_token(token, credentials_file, token_file)


if __name__ == "__main__":
    main()
