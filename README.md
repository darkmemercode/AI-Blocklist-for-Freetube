# AI-Blocklist-for-FreeTube

A set of Python scripts and a pre-compiled dataset to manage and import channel blocklists directly into [FreeTube](https://freetubeapp.io/).

---

## 📁 Repository Files

* **`blocklist.txt`**: Copy of the raw input list of targeted YouTube channel handles (e.g. @youtube) curated by [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt).
* **`fetch_channels.py`**: Fetches channel metadata from YouTube based on `blocklist.txt` and generates `freetube_channels.json`.
* **`fetch_channels_faster.py`**: A faster and more efficient version of `fetch_channels.py` that also creates a `handles_mapping.json` file that allows for faster re-runs when updating the blocklist.
* **`freetube_channels.json`**: Pre-built channel blocklist with >21,000 AI-channels ready for database insertion.
* **`handles_mapping.json`**: Cache mapping YouTube handles (@username) to their respective permanent Channel IDs (UC...) to speed up subsequent script runs when updating the list.
* **`update_db.py`**: Injects the fetched channels into your FreeTube `settings.db` file.

---

## ⚡ Quick Start (Recommended for Most Users)

If you just want the blocklist working as fast as possible, you can skip fetching channel data yourself and use the pre-built dataset instead:

1. Export your FreeTube database (see [Step 1](#step-1-export-your-freetube-database) below).
2. Download `freetube_channels.json` from this repo.
3. Run `update_db.py`.

> **Note:** This uses the channel list from the last time I downloaded the list, so it may not include the newest additions. If you want the most up-to-date list, follow the full steps below instead.

---

## 🤔 Why the Scripts Are Needed

The public [AiSList blocklist by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt) isn't in a format FreeTube can use directly — it only lists channel handles (e.g. `@youtube`).

FreeTube's database needs more than that to recognize a channel. Each entry requires:
* **Channel ID** (`UC...`) — the channel's permanent identifier.
* **Preferred name** — the channel name shown in the UI.
* **Icon** — the channel's avatar/icon.
* **Icon href** — a link to that icon.

None of this is included in the raw handle list, so [`fetch_channels_faster.py`](fetch_channels_faster.py) fetches it for every channel using `httpx` (fast HTML scraping) with a `yt-dlp` fallback for entries that fail to resolve. The results are saved to `freetube_channels.json` in the exact format FreeTube expects.

Since the list currently contains 21,000+ channels, manually adding them to `settings.db` one by one isn't practical — that's what [`update_db.py`](update_db.py) automates. That said, nothing stops you from adding channels manually if you only need a handful.

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
4. Save the exported `settings.db` file in the same directory as these scripts.
5. Create a `blocklist.txt` file in the same directory and copy and paste the contents of [AiSList blocklist by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt) into it. Save the file.
---

### Step 2: Fetch Channel Data
- Run `fetch_channels.py` or `fetch_channels_faster.py` to retrieve YouTube metadata for the channels listed in `blocklist.txt`. 
- `fetch_channels_faster.py` typically takes 1–2 hours on the full 21,000-entry list. 
> **Note:** Most entries resolve quickly via direct page scraping, but channels that fail this fast path fall back to a more conservative yt-dlp-based lookup (limited to 2 concurrent workers to avoid triggering YouTube's rate limiting), which accounts for most of the runtime.
- This generates the `freetube_channels.json` file needed for the database update in `update_db.py`.

```bash
# Option A: Use the optimized script (Recommended)
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
1. In FreeTube go to **Settings** → **Data**.
2. Click **Import Settings** and select your updated `settings.db` file (or manually replace the file in your FreeTube data directory).
3. *Optional:* Go to **Settings** → **Distraction Free** and untick **Show Added Items** to keep your UI clean without showing all 20k+ channels.
4. Restart FreeTube to apply the changes.

---

### Step 4: Updating the Blocklist Later

To pick up new channels added to the source list:

1. Open [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt) and copy its full contents.
2. Paste them into your local `blocklist.txt`, replacing the old contents.
3. Redo **Step 2** and **Step 3**:
   ```bash
   python fetch_channels_faster.py
   python update_db.py
   ```
   Then re-import the updated `settings.db` into FreeTube as described in Step 3.

> **Note:** Reruns are much faster than the initial fetch. `fetch_channels_faster.py` skips any channel ID already present in `freetube_channels.json`, and uses `handles_mapping.json` to instantly resolve `@handles` it has seen before without hitting YouTube again. In practice this means only the *newly added* channels in the updated list need to be fetched, so an update run typically takes a few minutes rather than the full 1–2 hours needed for a first-time fetch.

---

## ⚖️ Attribution & License

* **Code License:** [MIT License](LICENSE)
* **Dataset Credit:** The default blocklist input is derived from [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt).
* **Dataset License:** Shared under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) license.
