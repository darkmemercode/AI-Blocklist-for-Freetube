#!/usr/bin/env python3
"""
Fetches channel metadata from YouTube using yt-dlp and formats it into JSON.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import random
import sys
import threading
import time
from yt_dlp import YoutubeDL

INPUT_FILE = "blocklist.txt"
OUTPUT_FILE = "freetube_channels.json"
SAVE_INTERVAL = 25  # Save to disk every 25 successful additions
MAX_WORKERS = 4     # Worker count to stay within YouTube HTTP rate limits

lock = threading.Lock()
thread_local = threading.local()

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

def get_ydl():
    if not hasattr(thread_local, "ydl"):
        thread_local.ydl = YoutubeDL(YDL_OPTS)
    return thread_local.ydl

def save_output(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n[!] Error saving to disk: {e}")

# Load existing output if present
output = []
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            output = json.load(f)
    except json.JSONDecodeError:
        output = []

already_done_ids = {item["name"] for item in output if "name" in item}

# Load input file entries
entries = []
if os.path.exists(INPUT_FILE):
    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            entries.append(line)
else:
    print(f"Error: Could not find {INPUT_FILE}")
    sys.exit(1)

pending_entries = [e for e in entries if not (e.startswith("UC") and e in already_done_ids)]

print(f"Total entries in blocklist: {len(entries)}")
print(f"Already saved channels:     {len(already_done_ids)}")
print(f"Remaining to process:       {len(pending_entries)}\n")
print("-" * 50)

if not pending_entries:
    print("Everything is up to date!")
    sys.exit(0)

def process_entry(task_data):
    index, entry, total = task_data
    with lock:
        print(f"[{index}/{total}] ⏳ Fetching: {entry}")

    if entry.startswith("@"):
        url = "https://www.youtube.com/" + entry
    elif entry.startswith("UC"):
        url = "https://www.youtube.com/channel/" + entry
    else:
        return {"status": "invalid", "entry": entry, "index": index}

    ydl = get_ydl()
    max_retries = 3
    backoff_delay = 5

    info = None
    for attempt in range(max_retries + 1):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            info = ydl.extract_info(url, download=False)
            break
        except Exception as e:
            error_str = str(e).lower()
            if ("429" in error_str or "too many requests" in error_str) and attempt < max_retries:
                with lock:
                    print(f"[{index}/{total}] ⚠️ Rate limited on {entry}. Retrying in {backoff_delay}s...")
                time.sleep(backoff_delay)
                backoff_delay *= 2
            else:
                return {"status": "error", "entry": entry, "error": str(e), "index": index}

    if not info:
        return {"status": "no_id", "entry": entry, "index": index}

    channel_id = info.get("channel_id") or info.get("id")
    if not channel_id:
        return {"status": "no_id", "entry": entry, "index": index}

    with lock:
        if channel_id in already_done_ids:
            return {"status": "skipped", "entry": entry, "channel_id": channel_id, "index": index}

    title = info.get("channel") or info.get("uploader") or info.get("title") or entry
    thumbs = info.get("thumbnails") or []
    icon = thumbs[-1]["url"] if thumbs else ""

    item = {
        "name": channel_id,
        "preferredName": title,
        "icon": icon,
        "iconHref": f"/channel/{channel_id}"
    }

    return {"status": "success", "item": item, "title": title, "channel_id": channel_id, "index": index}

total_pending = len(pending_entries)
unsaved_changes = 0

try:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = [(i, entry, total_pending) for i, entry in enumerate(pending_entries, start=1)]
        futures = {executor.submit(process_entry, task): task for task in tasks}
        
        for future in as_completed(futures):
            result = future.result()
            status = result["status"]
            idx = result["index"]
            
            with lock:
                if status == "success":
                    output.append(result["item"])
                    already_done_ids.add(result["channel_id"])
                    unsaved_changes += 1
                    print(f"[{idx}/{total_pending}] ✓ SAVED: {result['title']}")
                    if unsaved_changes >= SAVE_INTERVAL:
                        save_output(output)
                        unsaved_changes = 0
                elif status == "skipped":
                    print(f"[{idx}/{total_pending}] - ALREADY EXISTS: {result['entry']}")
                elif status == "invalid":
                    print(f"[{idx}/{total_pending}] ✗ INVALID FORMAT: {result['entry']}")
                elif status == "no_id":
                    print(f"[{idx}/{total_pending}] ✗ NO ID FOUND: {result['entry']}")
                elif status == "error":
                    print(f"[{idx}/{total_pending}] ✗ ERROR on {result['entry']}: {result.get('error', 'Unknown')}")

except KeyboardInterrupt:
    print("\n\n[!] Process interrupted by user (Ctrl+C). Saving current progress...")
finally:
    print("\nExecuting final save...")
    save_output(output)
    print(f"Done! Total channels currently in {OUTPUT_FILE}: {len(output)}")
