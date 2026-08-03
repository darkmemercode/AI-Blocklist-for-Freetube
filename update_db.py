#!/usr/bin/env python3
"""
Injects channel blocklist metadata into FreeTube's settings.db file.
"""

import json
import os
import sys

JSON_FILE = "freetube_channels.json"
DB_FILE = "settings.db"  # Path to target NeDB file

if not os.path.exists(JSON_FILE):
    print(f"Error: Could not find {JSON_FILE}")
    sys.exit(1)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    channels = json.load(f)

channels_json_str = json.dumps(channels, ensure_ascii=False)

db_lines = []
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db_lines = [line.strip() for line in f if line.strip()]

updated = False
new_db_lines = []

for line in db_lines:
    try:
        data = json.loads(line)
        if data.get("_id") == "channelsHidden":
            data["value"] = channels_json_str
            updated = True
        new_db_lines.append(json.dumps(data, ensure_ascii=False))
    except json.JSONDecodeError:
        new_db_lines.append(line)

if not updated:
    new_entry = {"_id": "channelsHidden", "value": channels_json_str}
    new_db_lines.append(json.dumps(new_entry, ensure_ascii=False))

with open(DB_FILE, "w", encoding="utf-8") as f:
    for line in new_db_lines:
        f.write(line + "\n")

print(f"Successfully updated '{DB_FILE}' with {len(channels)} channels!")
