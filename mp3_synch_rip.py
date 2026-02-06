#!/usr/bin/env python3
"""
MP3-Synch-Rip: Download audio and sync with kids' devices
"""

import os
import sys
import json
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Dict

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Constants
DEFAULT_SYNC_PATH = "/path/to/device"


class MP3SynchRip:
    """Main class for downloading and syncing audio files."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize with configuration file."""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_file)
        self.download_dir = Path(self.config.get("download_directory", "./downloads"))
        self.sync_dir = Path(self.config.get("sync_directory", ""))
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file {config_file} not found. Creating from example...")
            if os.path.exists("config.example.json"):
                shutil.copy("config.example.json", config_file)
                self.logger.info(f"Created {config_file}. Please edit it with your settings.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def download_audio(self, url: str) -> bool:
        """Download audio from URL using yt-dlp."""
        self.logger.info(f"Downloading audio from: {url}")
        
        # Create download directory if it doesn't exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.config.get('audio_format', 'mp3'),
                'preferredquality': self.config.get('audio_quality', '192'),
            }],
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.logger.info(f"Successfully downloaded: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def download_all(self) -> int:
        """Download all URLs from config."""
        urls = self.config.get('urls', [])
        if not urls:
            self.logger.warning("No URLs found in config file.")
            return 0
        
        success_count = 0
        for url in urls:
            if self.download_audio(url):
                success_count += 1
        
        self.logger.info(f"Downloaded {success_count}/{len(urls)} files successfully.")
        return success_count
    
    def sync_to_device(self) -> bool:
        """Sync downloaded files to device."""
        if not self.sync_dir or str(self.sync_dir) == DEFAULT_SYNC_PATH:
            self.logger.error("Sync directory not configured. Please update config.json")
            return False
        
        if not self.download_dir.exists():
            self.logger.error(f"Download directory {self.download_dir} does not exist.")
            return False
        
        # Create sync directory if it doesn't exist
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all audio files
        audio_extensions = ['.mp3', '.m4a', '.wav', '.flac', '.ogg']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(self.download_dir.glob(f'*{ext}'))
        
        if not audio_files:
            self.logger.warning(f"No audio files found in {self.download_dir}")
            return False
        
        self.logger.info(f"Syncing {len(audio_files)} files to {self.sync_dir}")
        
        # Copy files to sync directory
        success_count = 0
        failed_files = []
        
        for audio_file in audio_files:
            try:
                dest = self.sync_dir / audio_file.name
                shutil.copy2(audio_file, dest)
                self.logger.info(f"Copied: {audio_file.name}")
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to copy {audio_file.name}: {e}")
                failed_files.append(audio_file.name)
        
        if failed_files:
            self.logger.warning(f"Sync completed with errors. Failed files: {', '.join(failed_files)}")
            return False
        
        self.logger.info(f"Sync completed successfully! {success_count} files copied.")
        return True
    
    def run(self, download: bool = True, sync: bool = True):
        """Run the download and sync process."""
        if download:
            self.download_all()
        
        if sync:
            self.sync_to_device()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MP3-Synch-Rip: Download audio and sync with kids' devices"
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file (default: config.json)'
    )
    parser.add_argument(
        '--download-only', '-d',
        action='store_true',
        help='Only download, do not sync'
    )
    parser.add_argument(
        '--sync-only', '-s',
        action='store_true',
        help='Only sync existing files, do not download'
    )
    parser.add_argument(
        '--url', '-u',
        help='Download single URL (ignores config URLs)'
    )
    
    args = parser.parse_args()
    
    app = MP3SynchRip(args.config)
    
    if args.url:
        # Download single URL
        app.download_audio(args.url)
        if not args.download_only:
            app.sync_to_device()
    else:
        # Run normal process
        download = not args.sync_only
        sync = not args.download_only
        app.run(download=download, sync=sync)


if __name__ == "__main__":
    main()
