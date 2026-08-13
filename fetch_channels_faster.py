#!/usr/bin/env python3

import asyncio
import json
import os
import re
import sys
import httpx
from yt_dlp import YoutubeDL

INPUT_FILE = "blocklist.txt"
OUTPUT_FILE = "freetube_channels.json"
HANDLES_FILE = "handles_mapping.json"
SAVE_INTERVAL = 25

# Rate Limiting & Concurrency
MAX_HTTP_WORKERS = 12       # Fast direct scraping concurrency
MAX_YTDLP_WORKERS = 2        # Conservative yt-dlp concurrency to prevent 429s

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "logger": QuietLogger(),
    "extract_flat": "in_playlist",
    "skip_download": True,
    "noplaylist": True,
    "playlistend": 0,
    "ignoreerrors": True,
}

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def save_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n[!] Error saving {file_path}: {e}")

async def resolve_fast(client: httpx.AsyncClient, entry: str):
    """
    Scrapes page HTML to directly extract channel_id, title, and avatar icon,
    completely bypassing yt-dlp overhead if successful.
    """
    if entry.startswith("@"):
        url = f"https://www.youtube.com/{entry}"
    else:
        url = f"https://www.youtube.com/channel/{entry}"

    try:
        response = await client.get(url, follow_redirects=True, timeout=6.0)
        if response.status_code != 200:
            return None

        html = response.text

        # Extract Channel ID
        channel_id = None
        match_id = re.search(r'https://www\.youtube\.com/channel/(UC[\w-]{22})', html) or \
                   re.search(r'"channelId":"(UC[\w-]{22})"', html)
        if match_id:
            channel_id = match_id.group(1)

        # Extract Title
        title = None
        match_title = re.search(r'<meta property="og:title" content="([^"]+)">', html)
        if match_title:
            title = match_title.group(1)

        # Extract Thumbnail
        icon = ""
        match_icon = re.search(r'<meta property="og:image" content="([^"]+)">', html)
        if match_icon:
            icon = match_icon.group(1)

        if channel_id and title:
            return {
                "name": channel_id,
                "preferredName": title,
                "icon": icon,
                "iconHref": f"/channel/{channel_id}"
            }
    except Exception:
        pass
    return None

def resolve_ytdlp_fallback(entry: str):
    """Fallback extraction using yt-dlp in a thread worker."""
    if entry.startswith("@"):
        url = f"https://www.youtube.com/{entry}"
    else:
        url = f"https://www.youtube.com/channel/{entry}"

    with YoutubeDL(YDL_OPTS) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            resolved_id = info.get("channel_id") or info.get("id")
            if not resolved_id:
                return None

            title = info.get("channel") or info.get("uploader") or info.get("title") or entry
            thumbs = info.get("thumbnails") or []
            icon = thumbs[-1]["url"] if thumbs else ""

            return {
                "name": resolved_id,
                "preferredName": title,
                "icon": icon,
                "iconHref": f"/channel/{resolved_id}"
            }
        except Exception:
            return None

# ---------------------------------------------------------
# Main Execution Pipeline
# ---------------------------------------------------------
async def main():
    # 1. Load Data
    output = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                output = json.load(f)
        except json.JSONDecodeError:
            output = []

    already_done_ids = {item["name"] for item in output if "name" in item}

    handle_map = {}
    if os.path.exists(HANDLES_FILE):
        try:
            with open(HANDLES_FILE, "r", encoding="utf-8") as f:
                handle_map = json.load(f)
        except json.JSONDecodeError:
            handle_map = {}

    # 2. Parse and Fast Pre-filter
    entries = []
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("!"):
                    entries.append(line)
    else:
        print(f"Error: Could not find {INPUT_FILE}")
        sys.exit(1)

    pending_entries = []
    for e in entries:
        if e.startswith("UC") and e in already_done_ids:
            continue
        if e.startswith("@") and e in handle_map and handle_map[e] in already_done_ids:
            continue
        pending_entries.append(e)

    total_pending = len(pending_entries)
    print(f"Total entries:          {len(entries)}")
    print(f"Already saved channels: {len(already_done_ids)}")
    print(f"Remaining to process:   {total_pending}\n" + "-" * 50)

    if not pending_entries:
        print("Everything is up to date!")
        sys.exit(0)

    # 3. Process Workers
    http_semaphore = asyncio.Semaphore(MAX_HTTP_WORKERS)
    ytdlp_semaphore = asyncio.Semaphore(MAX_YTDLP_WORKERS)
    
    unsaved_changes = 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
        
        async def process_entry(index, entry):
            nonlocal unsaved_changes

            # Check handle cache standard lookup
            if entry.startswith("@") and entry in handle_map:
                resolved_id = handle_map[entry]
                if resolved_id in already_done_ids:
                    return

            # Attempt Fast Regex Scraping
            async with http_semaphore:
                await asyncio.sleep(0.05)  # Slight spread delay
                res = await resolve_fast(client, entry)

            # Fallback to yt-dlp if direct scrape fails
            if not res:
                async with ytdlp_semaphore:
                    res = await asyncio.to_thread(resolve_ytdlp_fallback, entry)

            if res:
                ch_id = res["name"]
                output.append(res)
                already_done_ids.add(ch_id)
                if entry.startswith("@"):
                    handle_map[entry] = ch_id

                unsaved_changes += 1
                print(f"[{index}/{total_pending}] ✓ SAVED: {res['preferredName']}")

                if unsaved_changes >= SAVE_INTERVAL:
                    save_json(OUTPUT_FILE, output)
                    save_json(HANDLES_FILE, handle_map)
                    unsaved_changes = 0
            else:
                print(f"[{index}/{total_pending}] ✗ ERROR/SKIPPED: {entry}")

        try:
            tasks = [process_entry(i, entry) for i, entry in enumerate(pending_entries, start=1)]
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user. Saving current state...")
        finally:
            save_json(OUTPUT_FILE, output)
            save_json(HANDLES_FILE, handle_map)
            print("\nFinal state saved successfully.")

if __name__ == "__main__":
    asyncio.run(main())
