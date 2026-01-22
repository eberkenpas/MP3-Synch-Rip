#!/usr/bin/env python3
"""
Demo script showing MP3-Synch-Rip functionality
"""

import json
import tempfile
import shutil
from pathlib import Path
from mp3_synch_rip import MP3SynchRip

def demo():
    """Demonstrate the application features."""
    print("=" * 60)
    print("MP3-Synch-Rip Demo")
    print("=" * 60)
    
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    download_dir = Path(temp_dir) / "downloads"
    sync_dir = Path(temp_dir) / "device"
    config_file = Path(temp_dir) / "demo_config.json"
    
    try:
        # Create demo config
        config = {
            "download_directory": str(download_dir),
            "sync_directory": str(sync_dir),
            "audio_format": "mp3",
            "audio_quality": "192",
            "urls": []
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n1. Created demo configuration at: {config_file}")
        print(f"   Download directory: {download_dir}")
        print(f"   Sync directory: {sync_dir}")
        
        # Initialize app
        app = MP3SynchRip(str(config_file))
        print("\n2. Initialized MP3SynchRip application")
        
        # Create some demo audio files
        download_dir.mkdir(parents=True, exist_ok=True)
        demo_files = ['song1.mp3', 'song2.mp3', 'podcast.m4a']
        
        print("\n3. Creating demo audio files:")
        for filename in demo_files:
            file_path = download_dir / filename
            file_path.write_text(f"Demo audio content for {filename}")
            print(f"   - {filename}")
        
        # Test sync functionality
        print("\n4. Testing sync functionality...")
        result = app.sync_to_device()
        
        if result:
            print("   ✓ Sync completed successfully!")
            print(f"\n5. Files in sync directory ({sync_dir}):")
            for file in sorted(sync_dir.glob('*')):
                print(f"   - {file.name}")
        else:
            print("   ✗ Sync failed")
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    demo()
