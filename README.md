# MP3-Synch-Rip

A Python application to download audio from online sources and synchronize with kids' devices.

## Features

- Download audio from YouTube and other supported platforms
- Convert to MP3 or other audio formats
- Automatically sync downloaded files to connected devices
- Configurable audio quality and format
- Batch processing from URL lists
- Detailed logging

## Requirements

- Python 3.7+
- ffmpeg (for audio conversion)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/eberkenpas/MP3-Synch-Rip.git
cd MP3-Synch-Rip
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg:
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Configuration

1. Copy the example configuration file:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your settings:
```json
{
  "download_directory": "./downloads",
  "sync_directory": "/path/to/device",
  "audio_format": "mp3",
  "audio_quality": "192",
  "urls": [
    "https://www.youtube.com/watch?v=example1",
    "https://www.youtube.com/watch?v=example2"
  ]
}
```

### Configuration Options

- `download_directory`: Where to save downloaded audio files
- `sync_directory`: Path to your device (e.g., `/media/user/DEVICE` or `D:\Music`)
- `audio_format`: Output format (`mp3`, `m4a`, `wav`, etc.)
- `audio_quality`: Bitrate in kbps (e.g., `128`, `192`, `320`)
- `urls`: List of URLs to download

## Usage

### Basic Usage

Download and sync all URLs from config:
```bash
python mp3_synch_rip.py
```

### Download Only

Download without syncing to device:
```bash
python mp3_synch_rip.py --download-only
```

### Sync Only

Sync existing files without downloading:
```bash
python mp3_synch_rip.py --sync-only
```

### Download Single URL

Download a specific URL:
```bash
python mp3_synch_rip.py --url "https://www.youtube.com/watch?v=example"
```

### Custom Config File

Use a different configuration file:
```bash
python mp3_synch_rip.py --config my_config.json
```

## Command Line Options

```
usage: mp3_synch_rip.py [-h] [--config CONFIG] [--download-only] [--sync-only] [--url URL]

MP3-Synch-Rip: Download audio and sync with kids' devices

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Configuration file (default: config.json)
  --download-only, -d   Only download, do not sync
  --sync-only, -s       Only sync existing files, do not download
  --url URL, -u URL     Download single URL (ignores config URLs)
```

## Testing

Run the test suite:
```bash
python test_mp3_synch_rip.py
```

## How It Works

1. **Download**: Uses `yt-dlp` to download audio from supported platforms
2. **Convert**: Automatically converts to your specified format using ffmpeg
3. **Sync**: Copies downloaded files to your device directory

## Supported Platforms

Thanks to `yt-dlp`, this tool supports 1000+ websites including:
- YouTube
- SoundCloud
- Vimeo
- And many more

See the [full list of supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg (see Installation section above).

### "Sync directory not configured"
Update the `sync_directory` in your `config.json` file.

### "Permission denied" when syncing
Ensure your device is mounted and you have write permissions to the sync directory.

## License

This project is open source. Please check the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.