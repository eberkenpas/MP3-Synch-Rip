#!/usr/bin/env python3
"""
Tests for MP3-Synch-Rip
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mp3_synch_rip import MP3SynchRip


class TestMP3SynchRip(unittest.TestCase):
    """Test cases for MP3SynchRip class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.download_dir = Path(self.temp_dir) / "downloads"
        self.sync_dir = Path(self.temp_dir) / "sync"
        
        # Create test config
        self.test_config = {
            "download_directory": str(self.download_dir),
            "sync_directory": str(self.sync_dir),
            "audio_format": "mp3",
            "audio_quality": "192",
            "urls": [
                "https://www.youtube.com/watch?v=test1",
                "https://www.youtube.com/watch?v=test2"
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test initialization."""
        app = MP3SynchRip(str(self.config_file))
        self.assertEqual(app.download_dir, self.download_dir)
        self.assertEqual(app.sync_dir, self.sync_dir)
    
    def test_load_config(self):
        """Test config loading."""
        app = MP3SynchRip(str(self.config_file))
        self.assertEqual(app.config['audio_format'], 'mp3')
        self.assertEqual(app.config['audio_quality'], '192')
        self.assertEqual(len(app.config['urls']), 2)
    
    @patch('mp3_synch_rip.yt_dlp.YoutubeDL')
    def test_download_audio(self, mock_ytdl):
        """Test audio download."""
        # Mock yt-dlp
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.download.return_value = None
        
        app = MP3SynchRip(str(self.config_file))
        result = app.download_audio("https://www.youtube.com/watch?v=test")
        
        self.assertTrue(result)
        mock_instance.download.assert_called_once()
        self.assertTrue(self.download_dir.exists())
    
    @patch('mp3_synch_rip.yt_dlp.YoutubeDL')
    def test_download_audio_failure(self, mock_ytdl):
        """Test audio download failure handling."""
        # Mock yt-dlp to raise exception
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.download.side_effect = Exception("Download failed")
        
        app = MP3SynchRip(str(self.config_file))
        result = app.download_audio("https://www.youtube.com/watch?v=test")
        
        self.assertFalse(result)
    
    @patch('mp3_synch_rip.yt_dlp.YoutubeDL')
    def test_download_all(self, mock_ytdl):
        """Test downloading all URLs from config."""
        # Mock yt-dlp
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.download.return_value = None
        
        app = MP3SynchRip(str(self.config_file))
        count = app.download_all()
        
        self.assertEqual(count, 2)
        self.assertEqual(mock_instance.download.call_count, 2)
    
    def test_sync_to_device(self):
        """Test syncing files to device."""
        app = MP3SynchRip(str(self.config_file))
        
        # Create some dummy audio files
        self.download_dir.mkdir(parents=True, exist_ok=True)
        test_files = ['song1.mp3', 'song2.mp3', 'song3.m4a']
        for filename in test_files:
            (self.download_dir / filename).write_text("dummy audio content")
        
        result = app.sync_to_device()
        
        self.assertTrue(result)
        self.assertTrue(self.sync_dir.exists())
        
        # Check files were copied
        for filename in test_files:
            self.assertTrue((self.sync_dir / filename).exists())
    
    def test_sync_no_files(self):
        """Test sync with no audio files."""
        app = MP3SynchRip(str(self.config_file))
        
        # Create empty download directory
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        result = app.sync_to_device()
        
        self.assertFalse(result)
    
    def test_sync_unconfigured(self):
        """Test sync with unconfigured sync directory."""
        # Create config with default sync dir
        config = self.test_config.copy()
        config['sync_directory'] = '/path/to/device'
        
        config_file = Path(self.temp_dir) / "test_config2.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        app = MP3SynchRip(str(config_file))
        result = app.sync_to_device()
        
        self.assertFalse(result)


class TestConfigHandling(unittest.TestCase):
    """Test configuration file handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
    
    def test_missing_config_with_example(self):
        """Test handling of missing config when example exists."""
        # Create example config
        example_config = {
            "download_directory": "./downloads",
            "sync_directory": "/path/to/device",
            "audio_format": "mp3",
            "audio_quality": "192",
            "urls": []
        }
        
        with open("config.example.json", 'w') as f:
            json.dump(example_config, f)
        
        # Try to initialize without config.json (should exit)
        with self.assertRaises(SystemExit):
            MP3SynchRip("config.json")
        
        # Check that config.json was created
        self.assertTrue(os.path.exists("config.json"))


if __name__ == '__main__':
    unittest.main()
