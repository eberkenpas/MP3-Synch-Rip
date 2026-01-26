#!/usr/bin/env python3
"""
Sync MP3 files from ~/Music to Innioasis Y1 MP3 player.

- Copies MP3s from ~/Music to device root
- Copies MP3s from ~/Music/Audiobooks to device /Audiobooks
- Removes MP3s from device that aren't in source
- Does not create or modify folders
"""

import os
import shutil
import sys
from pathlib import Path


# Files to exclude from sync
EXCLUDE_FILES = {
    'synchToMP3.py',
    'readme.md',
    'bashinstructions.md',
    'Claude.md',
    'yt-audio.sh',
}


def find_y1_device():
    """Search for connected Innioasis Y1 device."""
    media_base = Path('/media')

    if not media_base.exists():
        return None

    for user_dir in media_base.iterdir():
        if not user_dir.is_dir():
            continue
        try:
            mount_points = list(user_dir.iterdir())
        except PermissionError:
            continue
        for mount_point in mount_points:
            if not mount_point.is_dir():
                continue

            # Check for Y1 identifier: Android/data/com.innioasis.y1
            y1_marker = mount_point / 'Android' / 'data' / 'com.innioasis.y1'
            if y1_marker.exists():
                return mount_point

            # Alternative check: Themes folder with Y1-specific files
            themes_dir = mount_point / 'Themes'
            if themes_dir.exists():
                y1_files = ['globalWallpaper.jpg', 'UsbBackground.jpg', 'desktopWallpaper.jpg']
                if any((mount_point / f).exists() for f in y1_files):
                    return mount_point

    return None


def format_size(size_bytes):
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_device_free_space(device_path):
    """Get free space on device."""
    stat = os.statvfs(device_path)
    return stat.f_frsize * stat.f_bavail


def get_source_mp3s(music_dir):
    """
    Get MP3 files from source, mapped to their destination paths.
    Returns dict: {dest_rel_path: source_absolute_path}
    """
    music_path = Path(music_dir)
    mp3s = {}

    # Get MP3s from root of Music folder (map to device root)
    for item in music_path.iterdir():
        if item.is_file() and item.suffix.lower() == '.mp3':
            if item.name not in EXCLUDE_FILES:
                # Destination is just the filename (device root)
                mp3s[Path(item.name)] = item

    # Get MP3s from Audiobooks subfolder (map to device /Audiobooks)
    audiobooks_dir = music_path / 'Audiobooks'
    if audiobooks_dir.exists():
        for item in audiobooks_dir.iterdir():
            if item.is_file() and item.suffix.lower() == '.mp3':
                # Destination is Audiobooks/filename
                mp3s[Path('Audiobooks') / item.name] = item

    return mp3s


def get_device_mp3s(device_path):
    """
    Get MP3 files currently on device (root and Audiobooks only).
    Returns dict: {rel_path: absolute_path}
    """
    device = Path(device_path)
    mp3s = {}

    # Get MP3s from device root
    for item in device.iterdir():
        if item.is_file() and item.suffix.lower() == '.mp3':
            mp3s[Path(item.name)] = item

    # Get MP3s from device Audiobooks folder
    audiobooks_dir = device / 'Audiobooks'
    if audiobooks_dir.exists():
        for item in audiobooks_dir.iterdir():
            if item.is_file() and item.suffix.lower() == '.mp3':
                mp3s[Path('Audiobooks') / item.name] = item

    return mp3s


def sync_files(source_mp3s, device_path):
    """Copy MP3 files to device. Only copies to existing folders."""
    device = Path(device_path)

    copied = 0
    skipped = 0
    errors = []

    for dest_rel, src_file in source_mp3s.items():
        dest_file = device / dest_rel

        # Check if destination folder exists (don't create folders)
        if not dest_file.parent.exists():
            print(f"  [SKIP] {dest_rel} (folder doesn't exist on device)")
            skipped += 1
            continue

        # Check if file already exists and is same size
        if dest_file.exists():
            if dest_file.stat().st_size == src_file.stat().st_size:
                print(f"  [SKIP] {dest_rel} (already synced)")
                skipped += 1
                continue

        # Copy file
        try:
            print(f"  [COPY] {dest_rel}")
            shutil.copy2(src_file, dest_file)
            copied += 1
        except Exception as e:
            print(f"  [ERROR] {dest_rel}: {e}")
            errors.append((dest_rel, str(e)))
            # Clean up partial file on error
            if dest_file.exists():
                try:
                    dest_file.unlink()
                except:
                    pass

    return copied, skipped, errors


def remove_orphans(source_mp3s, device_mp3s):
    """Remove MP3s from device that don't exist in source."""
    removed = 0
    errors = []

    source_names = set(source_mp3s.keys())

    for dest_rel, device_file in device_mp3s.items():
        if dest_rel not in source_names:
            try:
                print(f"  [DELETE] {dest_rel}")
                device_file.unlink()
                removed += 1
            except Exception as e:
                print(f"  [ERROR] Could not delete {dest_rel}: {e}")
                errors.append((dest_rel, str(e)))

    return removed, errors


def main():
    music_dir = Path.home() / 'Music'

    print("=" * 60)
    print("Innioasis Y1 Music Sync")
    print("=" * 60)
    print()

    # Find Y1 device
    print("Searching for Innioasis Y1 device...")
    device_path = find_y1_device()

    if not device_path:
        print("ERROR: No Innioasis Y1 device found.")
        print("Make sure the device is connected and mounted.")
        sys.exit(1)

    print(f"Found Y1 device at: {device_path}")
    print()

    # Get device free space
    free_space = get_device_free_space(device_path)
    print(f"Device free space: {format_size(free_space)}")
    print()

    # Get source and device MP3s
    print(f"Scanning {music_dir} for MP3 files...")
    source_mp3s = get_source_mp3s(music_dir)
    device_mp3s = get_device_mp3s(device_path)

    if not source_mp3s and not device_mp3s:
        print("No MP3 files to sync.")
        sys.exit(0)

    # Determine what needs to be done
    source_names = set(source_mp3s.keys())
    device_names = set(device_mp3s.keys())

    to_copy = []
    to_update = []
    to_skip = []
    to_delete = list(device_names - source_names)

    for dest_rel, src_file in source_mp3s.items():
        dest_file = device_path / dest_rel
        if dest_rel not in device_names:
            to_copy.append(dest_rel)
        elif dest_file.exists() and dest_file.stat().st_size != src_file.stat().st_size:
            to_update.append(dest_rel)
        else:
            to_skip.append(dest_rel)

    # Show summary
    print(f"Found {len(source_mp3s)} source MP3(s)")
    print()
    print("Sync plan:")
    print("-" * 40)
    if to_copy:
        print(f"  To copy:   {len(to_copy)} file(s)")
        for f in to_copy:
            size = format_size(source_mp3s[f].stat().st_size)
            print(f"    + {f} ({size})")
    if to_update:
        print(f"  To update: {len(to_update)} file(s)")
        for f in to_update:
            print(f"    ~ {f}")
    if to_skip:
        print(f"  Up to date: {len(to_skip)} file(s)")
    if to_delete:
        print(f"  To delete: {len(to_delete)} file(s)")
        for f in to_delete:
            print(f"    - {f}")
    print("-" * 40)
    print()

    if not to_copy and not to_update and not to_delete:
        print("Everything is in sync!")
        sys.exit(0)

    # Calculate space needed for new/updated files
    space_needed = sum(source_mp3s[f].stat().st_size for f in to_copy + to_update)
    if space_needed > free_space:
        print(f"WARNING: May not have enough space!")
        print(f"  Need: {format_size(space_needed)}")
        print(f"  Available: {format_size(free_space)}")
        print()

    # Prompt for confirmation
    response = input("Proceed with sync? [y/N]: ").strip().lower()
    if response != 'y':
        print("Sync cancelled.")
        sys.exit(0)

    print()

    # Perform sync
    total_copied = 0
    total_skipped = 0
    total_removed = 0
    all_errors = []

    if to_copy or to_update:
        print("Copying files...")
        print("-" * 40)
        copied, skipped, errors = sync_files(source_mp3s, device_path)
        total_copied = copied
        total_skipped = skipped
        all_errors.extend(errors)
        print("-" * 40)
        print()

    if to_delete:
        print("Removing orphaned files...")
        print("-" * 40)
        removed, errors = remove_orphans(source_mp3s, device_mp3s)
        total_removed = removed
        all_errors.extend(errors)
        print("-" * 40)
        print()

    # Summary
    print("Sync complete!")
    print(f"  Copied:  {total_copied}")
    print(f"  Skipped: {total_skipped}")
    print(f"  Removed: {total_removed}")
    if all_errors:
        print(f"  Errors:  {len(all_errors)}")
        for path, err in all_errors:
            print(f"    - {path}: {err}")

    print()
    print("Remember to safely eject the device before unplugging!")


if __name__ == '__main__':
    main()
