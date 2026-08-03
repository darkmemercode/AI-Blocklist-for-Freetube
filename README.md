# AI-Blocklist-for-Freetube

A set of Python scripts and a pre-compiled dataset to manage and import channel blocklists directly into [FreeTube](https://freetubeapp.io/).

---

## 📁 Repository Files

* **`freetube_channels.json`**: Pre-built channel blocklist ready for database insertion.
* **`blocklist.txt`**: Raw input list of channel IDs/handles.
* **`update_db.py`**: Injects `freetube_channels.json` into a FreeTube `settings.db` file.
* **`fetch_channels.py`**: Fetches channel metadata from YouTube for custom lists.

---

## 🚀 How to Apply the Blocklist to FreeTube

Follow these steps to safely inject the channel list into your FreeTube database:

### Step 1: Export your FreeTube Database
1. Open **FreeTube**.
2. Go to **Settings** (gear icon in the sidebar).
3. Select the **Data Settings** section.
4. Click on **Export Database** (or export your `settings.db` file).
5. Save the `settings.db` file into the same directory as these scripts.

### Step 2: Apply the Changes
1. Make sure Python 3 is installed on your system.
2. Run the update script in your terminal/command prompt:
   ```bash
   python update_db.py
