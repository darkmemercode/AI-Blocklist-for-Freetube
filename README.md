# AI-Blocklist-for-FreeTube

A set of Python scripts and a pre-compiled dataset to manage and import channel blocklists directly into [FreeTube](https://freetubeapp.io/).

---

## 📁 Repository Files

* **`blocklist.txt`**: Raw input list of targeted YouTube channel IDs and handles.
* **`fetch_channels.py`**: Fetches channel metadata from YouTube based on `blocklist.txt` and generates `freetube_channels.json`.
* **`freetube_channels.json`**: Pre-built channel blocklist ready for database insertion.
* **`update_db.py`**: Injects the fetched channels into your FreeTube `settings.db` file.

---

## 🚀 How to Use

Follow these steps to generate your channel list and safely inject it into your FreeTube database.

### Prerequisites
* **Python 3.x** installed on your system.
* **FreeTube** installed.

---

### Step 1: Export Your FreeTube Database
1. Open **FreeTube**.
2. Go to **Settings** -> **Data**.
3. Click **Export Database** (or locate your existing `settings.db` file).
4. Save the exported `settings.db` file in the same directory as these scripts.

---

### Step 2: Fetch Channel Data
Run `fetch_channels.py` to retrieve YouTube metadata for the channels listed in `blocklist.txt`. This script outputs the `freetube_channels.json` file needed for the database update with `update_db.py`.

```bash
python fetch_channels.py
python update_db.py
```

---

### Step 3: Import the updated settings.db file into Freetube

## ⚖️ Attribution & License

* **Code License:** [MIT License](LICENSE)
* **Dataset Credit:** The default blocklist input standard is derived from [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt).
* **Dataset License:** Shared under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) license.
