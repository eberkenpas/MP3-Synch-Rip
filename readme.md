# Downloading YouTube Audio with yt-dlp

## Prerequisites

Install yt-dlp (download binary):
```bash
mkdir -p ~/.local/bin
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod +x ~/.local/bin/yt-dlp
```

Install ffmpeg and ffprobe (static binaries, no sudo required):
```bash
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz
tar -xf /tmp/ffmpeg.tar.xz -C /tmp
cp /tmp/ffmpeg-*-amd64-static/ffmpeg ~/.local/bin/
cp /tmp/ffmpeg-*-amd64-static/ffprobe ~/.local/bin/
```

## Quick Start

Use the `downloadYT.py` script:
```bash
./downloadYT.py 'https://www.youtube.com/watch?v=VIDEO_ID'
```

Files larger than 3GB are automatically split into parts (e.g., "Title part 1 of 2.mp3").

## Manual Download

```bash
~/.local/bin/yt-dlp --ffmpeg-location ~/.local/bin/ffmpeg -x --audio-format mp3 --audio-quality 0 -o "OUTPUT_NAME.%(ext)s" "YOUTUBE_URL"
```

### Example

```bash
~/.local/bin/yt-dlp --ffmpeg-location ~/.local/bin/ffmpeg -x --audio-format mp3 --audio-quality 0 -o "Heir_to_the_Empire_Audiobook.%(ext)s" "https://www.youtube.com/watch?v=FM5oCmTmUio"
```

## Options Explained

| Option | Description |
|--------|-------------|
| `-x` | Extract audio only |
| `--audio-format mp3` | Convert to MP3 format |
| `--audio-quality 0` | Best quality (0-10, 0 is best) |
| `-o "NAME.%(ext)s"` | Output filename template |
| `--ffmpeg-location` | Path to ffmpeg binary |

## List Available Formats

To see all available formats before downloading:
```bash
~/.local/bin/yt-dlp -F "YOUTUBE_URL"
```
