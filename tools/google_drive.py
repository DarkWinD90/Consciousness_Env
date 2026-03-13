#!/usr/bin/env python3
"""Google Drive API utility for uploading, downloading, listing, and searching files.

Setup (one-time):
    1. Go to https://console.cloud.google.com/
    2. Create a project (or select an existing one)
    3. Enable the Google Drive API:
       APIs & Services → Library → search "Google Drive API" → Enable
    4. Create OAuth 2.0 credentials:
       APIs & Services → Credentials → Create Credentials → OAuth client ID
       - Application type: Desktop app
       - Download the JSON file
       - Save it as: tools/credentials.json
    5. Install dependencies:
       pip install google-auth google-auth-oauthlib google-api-python-client
    6. Run any command — a browser window will open for authentication:
       python tools/google_drive.py list

Usage:
    python tools/google_drive.py list [--folder FOLDER_ID] [--limit N]
    python tools/google_drive.py search "query string"
    python tools/google_drive.py upload local_file.pdf [--folder FOLDER_ID] [--name "Remote Name"]
    python tools/google_drive.py download FILE_ID [--output local_path]
    python tools/google_drive.py info FILE_ID
"""

import argparse
import io
import os
import sys
from pathlib import Path

# Allow OAuth over HTTP for localhost (required for remote/headless environments)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_PATH = Path(__file__).parent / "token.json"
CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"


def get_service():
    """Authenticate and return a Google Drive API service instance."""
    import json
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build

    if not CREDENTIALS_PATH.exists():
        print(f"ERROR: {CREDENTIALS_PATH} not found.", file=sys.stderr)
        print("Download OAuth credentials from Google Cloud Console.", file=sys.stderr)
        print("See docstring at top of this file for setup instructions.", file=sys.stderr)
        sys.exit(1)

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Manual copy-paste flow for remote/headless environments
            flow = Flow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                scopes=SCOPES,
                redirect_uri="http://localhost",
            )
            auth_url, _ = flow.authorization_url(prompt="consent")
            print("\n1. Open this URL in your browser:\n")
            print(f"   {auth_url}\n")
            print("2. Sign in and authorize access")
            print("3. The browser will redirect to a localhost URL that won't load — that's OK")
            print("4. Copy the FULL URL from your browser's address bar and paste it here:\n")
            redirect_response = input("Paste the full redirect URL: ").strip()
            flow.fetch_token(authorization_response=redirect_response)
            creds = flow.credentials
        TOKEN_PATH.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def cmd_list(args):
    """List files in Drive or a specific folder."""
    service = get_service()
    query = f"'{args.folder}' in parents" if args.folder else None
    results = (
        service.files()
        .list(
            q=query,
            pageSize=args.limit,
            fields="files(id, name, mimeType, size, modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    files = results.get("files", [])
    if not files:
        print("No files found.")
        return
    print(f"{'Name':<50} {'Type':<35} {'Size':>10}  {'Modified':<20}  ID")
    print("-" * 140)
    for f in files:
        size = f.get("size", "-")
        if size != "-":
            size = _human_size(int(size))
        modified = f.get("modifiedTime", "-")[:19].replace("T", " ")
        print(f"{f['name']:<50} {f['mimeType']:<35} {size:>10}  {modified:<20}  {f['id']}")


def cmd_search(args):
    """Search for files by name."""
    service = get_service()
    query = f"name contains '{args.query}' and trashed = false"
    results = (
        service.files()
        .list(
            q=query,
            pageSize=args.limit,
            fields="files(id, name, mimeType, size, modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    files = results.get("files", [])
    if not files:
        print(f"No files matching '{args.query}'.")
        return
    print(f"{'Name':<50} {'Type':<35} {'Size':>10}  {'Modified':<20}  ID")
    print("-" * 140)
    for f in files:
        size = f.get("size", "-")
        if size != "-":
            size = _human_size(int(size))
        modified = f.get("modifiedTime", "-")[:19].replace("T", " ")
        print(f"{f['name']:<50} {f['mimeType']:<35} {size:>10}  {modified:<20}  {f['id']}")


def cmd_upload(args):
    """Upload a file to Drive."""
    from googleapiclient.http import MediaFileUpload

    service = get_service()
    local_path = Path(args.file)
    if not local_path.exists():
        print(f"ERROR: {local_path} not found.", file=sys.stderr)
        sys.exit(1)

    file_metadata = {"name": args.name or local_path.name}
    if args.folder:
        file_metadata["parents"] = [args.folder]

    media = MediaFileUpload(str(local_path), resumable=True)
    result = service.files().create(body=file_metadata, media_body=media, fields="id, name, webViewLink").execute()
    print(f"Uploaded: {result['name']}")
    print(f"File ID:  {result['id']}")
    print(f"Link:     {result.get('webViewLink', 'N/A')}")


def cmd_download(args):
    """Download a file from Drive."""
    from googleapiclient.http import MediaIoBaseDownload

    service = get_service()

    # Get file metadata for the name
    meta = service.files().get(fileId=args.file_id, fields="name, mimeType").execute()
    output_path = Path(args.output) if args.output else Path(meta["name"])

    # Handle Google Docs types (export instead of download)
    export_map = {
        "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
        "application/vnd.google-apps.spreadsheet": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xlsx",
        ),
        "application/vnd.google-apps.presentation": ("application/pdf", ".pdf"),
    }

    mime = meta["mimeType"]
    if mime in export_map:
        export_mime, ext = export_map[mime]
        if not args.output:
            output_path = output_path.with_suffix(ext)
        request = service.files().export_media(fileId=args.file_id, mimeType=export_mime)
    else:
        request = service.files().get_media(fileId=args.file_id)

    fh = io.FileIO(str(output_path), "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}%")
    fh.close()
    print(f"Saved to: {output_path}")


def cmd_info(args):
    """Get detailed info about a file."""
    service = get_service()
    f = (
        service.files()
        .get(
            fileId=args.file_id,
            fields="id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink, parents",
        )
        .execute()
    )
    print(f"Name:     {f['name']}")
    print(f"ID:       {f['id']}")
    print(f"Type:     {f['mimeType']}")
    print(f"Size:     {_human_size(int(f['size'])) if 'size' in f else 'N/A'}")
    print(f"Created:  {f.get('createdTime', 'N/A')}")
    print(f"Modified: {f.get('modifiedTime', 'N/A')}")
    print(f"Owner:    {f['owners'][0]['displayName'] if 'owners' in f else 'N/A'}")
    print(f"Link:     {f.get('webViewLink', 'N/A')}")
    print(f"Parents:  {f.get('parents', [])}")


def _human_size(nbytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


def main():
    parser = argparse.ArgumentParser(description="Google Drive API utility")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List files")
    p_list.add_argument("--folder", help="Folder ID to list")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = sub.add_parser("search", help="Search files by name")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=20, help="Max results")
    p_search.set_defaults(func=cmd_search)

    # upload
    p_upload = sub.add_parser("upload", help="Upload a file")
    p_upload.add_argument("file", help="Local file path")
    p_upload.add_argument("--folder", help="Destination folder ID")
    p_upload.add_argument("--name", help="Remote file name (default: local name)")
    p_upload.set_defaults(func=cmd_upload)

    # download
    p_download = sub.add_parser("download", help="Download a file")
    p_download.add_argument("file_id", help="Google Drive file ID")
    p_download.add_argument("--output", help="Local output path")
    p_download.set_defaults(func=cmd_download)

    # info
    p_info = sub.add_parser("info", help="Get file info")
    p_info.add_argument("file_id", help="Google Drive file ID")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
