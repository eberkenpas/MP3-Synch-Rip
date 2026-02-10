# Music Management Project

## Overview
A toolkit for downloading audio from YouTube and syncing to an Innioasis Y1 MP3 player.

## Components

### Scripts
- `downloadYT.py` - YouTube download script with playlist support and auto-splitting. Usage: `./downloadYT.py '<youtube-url>'` or `./downloadYT.py -p '<playlist-url>'`
- `synchToMP3.py` - Sync music to Y1 device. Usage: `python3 synchToMP3.py`
- `yt-audio.sh` - Legacy shell script (no auto-splitting)

### Folder Structure
- `Audiobooks/` - Audiobook files (syncs to device's Audiobooks folder)
- Root level - Music and soundtrack files

### Documentation
- `readme.md` - Prerequisites, quick start examples, and manual yt-dlp reference
- `bashinstructions.md` - Quick usage guide for downloadYT.py

### Dependencies (installed in `~/.local/bin/`)
- `yt-dlp` - YouTube downloader
- `ffmpeg` - Audio conversion
- `ffprobe` - Audio file analysis (used for splitting)

## Progress

### Completed
- [x] Set up yt-dlp installation (no sudo required)
- [x] Set up ffmpeg installation (static binary)
- [x] Created `yt-audio.sh` wrapper script
- [x] Created documentation files
- [x] Successfully downloaded test files:
  - Heir to the Empire audiobook
  - Harry Potter Book 6 (Parts 1 & 2)
  - Movie soundtracks (Crimson Tide, Clear and Present Danger)
- [x] Created `synchToMP3.py` script for Y1 device sync
- [x] Organized audiobooks into `Audiobooks/` subfolder
- [x] Created `downloadYT.py` Python script with auto-splitting for large files (>3GB)
- [x] Add progress bar to sync tool for file transfers
- [x] Add YouTube playlist support to downloadYT.py (downloads and combines into single file)
- [x] Downloaded Arc Raiders soundtrack collection
- [x] Downloaded Kathy Joseph's History of Electricity series
- [x] Updated readme.md with playlist usage examples

### Future Ideas
- [ ] Add batch download from text file
- [ ] Add option for different audio formats (opus, m4a, etc.)
- [ ] Add M3U playlist generation for Y1 device
- [ ] Add backup script to archive current Music folder
- [ ] Generate M3U playlists for split parts

## Next Steps
- [ ] Configure downloads to target media server at `192.168.50.182:5000`
- [ ] Modify scripts to optionally download directly to server
- [ ] Add sync capability between local Music folder and server
- [ ] Investigate server API/protocol for remote uploads

## Target Device
**Innioasis Y1 MP3 Player** (128GB)
- Mounts at `/media/<user>/<device-id>`
- Identified by `Android/data/com.innioasis.y1` folder
- Supports M3U playlist import
- Supported formats: MP3, M4A, FLAC, OGG, WAV, AAC, WMA, APE

## Quick Reference

Download audio from YouTube:
```bash
./downloadYT.py 'https://www.youtube.com/watch?v=VIDEO_ID'
```

Download playlist as single combined file (great for audiobooks):
```bash
./downloadYT.py -p 'https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID'
./downloadYT.py -p -n 'Custom Name' 'https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID'
```

Sync music to Y1 device:
```bash
python3 synchToMP3.py
```
The sync script shows a preview of changes and asks for confirmation before copying/deleting any files.

Update yt-dlp:
```bash
~/.local/bin/yt-dlp -U
```
