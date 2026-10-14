# AI Channel Blocklist for FreeTube

Import a blocklist of 21,000+ AI-generated YouTube channels into [FreeTube](https://freetubeapp.io/).

The list comes from [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt). That list only contains channel handles (e.g. `@youtube`), but FreeTube needs more (channel ID, name, icon). The scripts here fetch that data and write it into your FreeTube `settings.db`.

## Requirements

* Python 3
* FreeTube
* Dependencies: `pip install yt-dlp httpx`

## Quick Start (pre-built list)

Fastest option. The list may be slightly out of date; for the latest, see [Update to the Latest List](#update-to-the-latest-list).

1. In FreeTube, go to **Settings → Data → Export Settings**. Save `settings.db` in the same folder as the scripts.
2. Download `freetube_channels.json` from this repo into the same folder.
3. Run:
   ```bash
   python update_db.py
   ```
4. In FreeTube, go to **Settings → Data → Import Settings** and select the updated `settings.db`.
5. Restart FreeTube.

**Tip:** Untick **Settings → Distraction Free → Show Added Items** to keep 20k+ blocked channels out of your UI.

## Update to the Latest List

1. Export `settings.db` from FreeTube (as above).
2. Copy the full contents of the [AiSList blocklist](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt) into `blocklist.txt`, replacing the old contents.
3. Run:
   ```bash
   python fetch_channels_faster.py
   python update_db.py
   ```
4. Import the updated `settings.db` into FreeTube and restart.

**How long does it take?** The first run takes 1–2 hours. Later runs take a few minutes, since channels already in the cache-file `handles_mapping.json` are skipped.

## Files

| File | Purpose |
|---|---|
| `blocklist.txt` | Input list of channel handles |
| `fetch_channels_faster.py` | Fetches channel data (recommended) |
| `fetch_channels.py` | Slower original version of the fetcher |
| `freetube_channels.json` | Pre-built list in FreeTube's format |
| `handles_mapping.json` | Cache of handle → channel ID, speeds up re-runs |
| `update_db.py` | Writes the channels into `settings.db` |

## License & Credit

* Code: [MIT License](LICENSE)
* Dataset: derived from [AiSList by Override92](https://github.com/Override92/AiSList/blob/main/AiSList/aislist_blocklist.txt), shared under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
