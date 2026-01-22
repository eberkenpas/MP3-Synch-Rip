#!/bin/bash

# YouTube Audio Downloader
# Downloads YouTube audio as MP3 to ~/Music folder

YTDLP="$HOME/.local/bin/yt-dlp"
FFMPEG="$HOME/.local/bin/ffmpeg"
OUTPUT_DIR="$HOME/Music"

# Check for URL argument
if [ -z "$1" ]; then
    echo "Usage: $0 <youtube-url>"
    echo "Example: $0 'https://www.youtube.com/watch?v=VIDEO_ID'"
    exit 1
fi

URL="$1"

# Check if yt-dlp is installed
if [ ! -f "$YTDLP" ]; then
    echo "Error: yt-dlp not found at $YTDLP"
    echo "Install it with:"
    echo "  curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp && chmod +x ~/.local/bin/yt-dlp"
    exit 1
fi

# Check if ffmpeg is installed
if [ ! -f "$FFMPEG" ]; then
    echo "Error: ffmpeg not found at $FFMPEG"
    echo "Install it with:"
    echo "  curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz"
    echo "  tar -xf /tmp/ffmpeg.tar.xz -C /tmp"
    echo "  cp /tmp/ffmpeg-*-amd64-static/ffmpeg ~/.local/bin/"
    exit 1
fi

echo "Downloading audio from: $URL"
echo "Saving to: $OUTPUT_DIR"
echo ""

"$YTDLP" \
    --ffmpeg-location "$FFMPEG" \
    -x \
    --audio-format mp3 \
    --audio-quality 0 \
    -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
    "$URL"

if [ $? -eq 0 ]; then
    echo ""
    echo "Download complete!"
else
    echo ""
    echo "Download failed."
    exit 1
fi
