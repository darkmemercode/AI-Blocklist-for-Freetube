# AI-Blocklist-for-FreeTube

A set of Python scripts and a pre-compiled dataset to manage and import channel blocklists directly into [FreeTube](https://freetubeapp.io/).

---

## 📁 Repository Files

* **`blocklist.txt`**: Raw input list of targeted YouTube channel IDs and handles curated by [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt).
* **`fetch_channels.py`**: Fetches channel metadata from YouTube based on `blocklist.txt` and generates `freetube_channels.json`.
* **`fetch_channels_faster.py`**: A faster and more efficient version of `fetch_channels.py` that also creates a `handles_mapping.json` file that allows for faster re-runs when updating the blocklist.
* **`freetube_channels.json`**: Pre-built channel blocklist with >21,000 AI-channels ready for database insertion.
* **`handles_mapping.json`**: Cache mapping YouTube handles (@username) to their respective permanent Channel IDs (UC...) to speed up subsequent script runs.
* **`update_db.py`**: Injects the fetched channels into your FreeTube `settings.db` file.

---

## ⚡ Quick Start (Recommended for Most Users)

If you just want the blocklist working as fast as possible, you can skip fetching channel data yourself and use the pre-built dataset instead:

1. Export your FreeTube database (see [Step 1](#step-1-export-your-freetube-database) below).
2. Download `freetube_channels.json` from this repo.
3. Run `update_db.py`.

> **Note:** This uses the channel list from the last time it was scraped, so it may not include the newest additions. If you want the most up-to-date list, follow the full steps below instead.

---

## 🚀 How to Use

Follow these steps to generate your own up-to-date channel list and safely import it into your FreeTube database.

### Prerequisites
* **Python 3.x** installed on your system.
* **Install required dependencies:**
```bash
pip install yt-dlp httpx
```
* **FreeTube** installed.

---

### Step 1: Export Your FreeTube Database
1. Open **FreeTube**.
2. Go to **Settings** → **Data**.
3. Click **Export Settings** (or locate your existing `settings.db` file).
4. Save the exported `settings.db` file in the same directory as the python scripts.

---

### Step 2: Fetch Channel Data
Run `fetch_channels.py` or `fetch_channels_faster.py` to retrieve YouTube metadata for the channels listed in `blocklist.txt`. This generates the `freetube_channels.json` file needed for the database update in `update_db.py`.

```bash
# Option A: Use the faster, optimized script (Recommended)
python fetch_channels_faster.py
python update_db.py
```

```bash
# Option B: Use the standard script
python fetch_channels.py
python update_db.py
```

---

### Step 3: Import the Updated `settings.db` File
1. Go to **Settings** → **Data**.
2. Click **Import Settings** and select your updated `settings.db` file (or manually replace the file in your FreeTube data directory).
3. *Optional:* Go to **Settings** → **Distraction Free** and untick **Show Added Items** to keep your UI clean without showing all 20k+ channels when looking through your settings.
4. Restart FreeTube to apply the changes.

---

## ⚖️ Attribution & License

* **Code License:** [MIT License](LICENSE)
* **Dataset Credit:** The default blocklist input is derived from [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt).
* **Dataset License:** Shared under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) license.
