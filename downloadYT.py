#!/usr/bin/env python3
"""
YouTube Audio Downloader
Downloads YouTube audio as MP3 to ~/Music folder.
Splits files larger than 3GB into chunks named "title part N of M.mp3"

Usage:
  downloadYT.py <youtube-url>              Download single video
  downloadYT.py --playlist <playlist-url>  Download playlist and combine into one file
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


YTDLP = Path.home() / '.local' / 'bin' / 'yt-dlp'
FFMPEG = Path.home() / '.local' / 'bin' / 'ffmpeg'
FFPROBE = Path.home() / '.local' / 'bin' / 'ffprobe'
OUTPUT_DIR = Path.home() / 'Music'
MAX_SIZE_BYTES = 3 * 1024 * 1024 * 1024  # 3GB


def get_duration(file_path):
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run([
        str(FFPROBE),
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(file_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def split_file(file_path):
    """Split a large MP3 file into 3GB chunks."""
    file_size = file_path.stat().st_size
    num_chunks = (file_size // MAX_SIZE_BYTES) + 1
    duration = get_duration(file_path)

    if duration is None:
        print(f"Error: Could not get duration of {file_path}")
        return False

    chunk_duration = duration / num_chunks
    stem = file_path.stem

    print(f"Splitting into {num_chunks} parts ({chunk_duration:.1f}s each)...")

    for i in range(num_chunks):
        start_time = i * chunk_duration
        part_name = f"{stem} part {i + 1} of {num_chunks}.mp3"
        output_path = OUTPUT_DIR / part_name

        print(f"  Creating: {part_name}")

        result = subprocess.run([
            str(FFMPEG),
            '-i', str(file_path),
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-acodec', 'copy',
            '-y',
            str(output_path)
        ], capture_output=True)

        if result.returncode != 0:
            print(f"Error splitting file at part {i + 1}")
            return False

    # Remove original large file
    file_path.unlink()
    print(f"Removed original file: {file_path.name}")

    return True


def check_dependencies():
    """Check that required tools are installed."""
    if not YTDLP.exists():
        print(f"Error: yt-dlp not found at {YTDLP}")
        print("Install it with:")
        print("  curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp && chmod +x ~/.local/bin/yt-dlp")
        sys.exit(1)

    if not FFMPEG.exists():
        print(f"Error: ffmpeg not found at {FFMPEG}")
        print("Install it with:")
        print("  curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz")
        print("  tar -xf /tmp/ffmpeg.tar.xz -C /tmp")
        print("  cp /tmp/ffmpeg-*-amd64-static/ffmpeg ~/.local/bin/")
        sys.exit(1)


def check_and_split(output_file):
    """Check if file needs splitting and split if so."""
    if output_file.exists() and output_file.stat().st_size > MAX_SIZE_BYTES:
        print()
        print(f"File is larger than 3GB ({output_file.stat().st_size / (1024**3):.1f}GB), splitting...")
        if split_file(output_file):
            print("Split complete!")
        else:
            print("Split failed.")
            sys.exit(1)


def download_single(url):
    """Download a single video as MP3."""
    print(f"Downloading audio from: {url}")
    print(f"Saving to: {OUTPUT_DIR}")
    print()

    output_template = str(OUTPUT_DIR / '%(title)s.%(ext)s')
    filepath_file = OUTPUT_DIR / '.last_download.txt'

    # Download the file, saving the output path to a temp file
    result = subprocess.run([
        str(YTDLP),
        '--ffmpeg-location', str(FFMPEG),
        '-x',
        '--audio-format', 'mp3',
        '--audio-quality', '0',
        '--print-to-file', 'after_move:filepath', str(filepath_file),
        '-o', output_template,
        url
    ])

    if result.returncode != 0:
        print()
        print("Download failed.")
        sys.exit(1)

    # Get the output filepath from the temp file
    if not filepath_file.exists():
        print("Could not determine output file.")
        sys.exit(1)

    output_file = Path(filepath_file.read_text().strip())
    filepath_file.unlink()  # Clean up temp file

    print()
    print(f"Download complete: {output_file.name}")

    check_and_split(output_file)


def download_playlist(url, output_name=None):
    """Download a playlist and combine all videos into a single MP3."""
    print(f"Downloading playlist from: {url}")
    print()

    # Get playlist info
    print("Fetching playlist info...")
    result = subprocess.run([
        str(YTDLP),
        '--flat-playlist',
        '--print', '%(playlist_title)s',
        '--playlist-items', '1',
        url
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("Error: Could not get playlist info")
        sys.exit(1)

    playlist_title = result.stdout.strip()
    if output_name:
        final_name = output_name
    else:
        final_name = playlist_title

    print(f"Playlist: {playlist_title}")
    print(f"Output will be: {final_name}.mp3")
    print()

    # Create temp directory for individual files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Download all videos with numbered prefixes
        print("Downloading playlist videos...")
        output_template = str(temp_path / '%(playlist_index)03d-%(title)s.%(ext)s')

        result = subprocess.run([
            str(YTDLP),
            '--ffmpeg-location', str(FFMPEG),
            '-x',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', output_template,
            url
        ])

        if result.returncode != 0:
            print()
            print("Download failed.")
            sys.exit(1)

        # Get all downloaded MP3s in order
        mp3_files = sorted(temp_path.glob('*.mp3'))

        if not mp3_files:
            print("No files were downloaded.")
            sys.exit(1)

        print()
        print(f"Downloaded {len(mp3_files)} files. Combining...")

        # Create concat file list for ffmpeg
        concat_file = temp_path / 'concat.txt'
        with open(concat_file, 'w') as f:
            for mp3 in mp3_files:
                # Escape single quotes in filenames
                escaped_path = str(mp3).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

        # Combine all files
        output_file = OUTPUT_DIR / f"{final_name}.mp3"

        result = subprocess.run([
            str(FFMPEG),
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-acodec', 'copy',
            '-y',
            str(output_file)
        ], capture_output=True)

        if result.returncode != 0:
            print("Error combining files.")
            print(result.stderr.decode())
            sys.exit(1)

    print()
    print(f"Combined into: {output_file.name}")
    print(f"Size: {output_file.stat().st_size / (1024**3):.2f} GB")

    check_and_split(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Download YouTube audio as MP3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 'https://www.youtube.com/watch?v=VIDEO_ID'
  %(prog)s --playlist 'https://www.youtube.com/playlist?list=PLAYLIST_ID'
  %(prog)s --playlist 'URL' --name 'My Audiobook'
'''
    )
    parser.add_argument('url', help='YouTube URL')
    parser.add_argument('--playlist', '-p', action='store_true',
                        help='Download entire playlist and combine into one file')
    parser.add_argument('--name', '-n', type=str,
                        help='Output filename (without extension) for playlist mode')

    args = parser.parse_args()

    url = args.url.replace('\\', '')

    check_dependencies()

    if args.playlist:
        download_playlist(url, args.name)
    else:
        download_single(url)


if __name__ == '__main__':
    main()
