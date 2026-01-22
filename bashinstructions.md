# yt-audio.sh Usage Instructions

## Quick Start

```bash
./yt-audio.sh 'https://www.youtube.com/watch?v=VIDEO_ID'
```

## What It Does

- Downloads audio from a YouTube URL
- Converts it to MP3 format (best quality)
- Saves to `~/Music` folder
- Names the file using the YouTube video title

## Examples

Download a single video:
```bash
./yt-audio.sh 'https://www.youtube.com/watch?v=FM5oCmTmUio'
```

Run from anywhere using full path:
```bash
~/Music/yt-audio.sh 'https://www.youtube.com/watch?v=VIDEO_ID'
```

## Requirements

The script requires `yt-dlp` and `ffmpeg` installed in `~/.local/bin/`. If missing, the script will show installation instructions.

## Optional: Add to PATH

To run the script from any directory without specifying the path:

```bash
# Add to your ~/.bashrc or ~/.zshrc
export PATH="$HOME/Music:$PATH"
```

Then reload your shell:
```bash
source ~/.bashrc
```

Now you can run from anywhere:
```bash
yt-audio.sh 'https://www.youtube.com/watch?v=VIDEO_ID'
```

## Troubleshooting

**"Permission denied"** - Make the script executable:
```bash
chmod +x ~/Music/yt-audio.sh
```

**"yt-dlp not found"** - Install yt-dlp:
```bash
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod +x ~/.local/bin/yt-dlp
```

**"ffmpeg not found"** - Install ffmpeg:
```bash
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz
tar -xf /tmp/ffmpeg.tar.xz -C /tmp
cp /tmp/ffmpeg-*-amd64-static/ffmpeg ~/.local/bin/
chmod +x ~/.local/bin/ffmpeg
```
