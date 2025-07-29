#!/usr/bin/env python3
"""
Simple HEIC Archive Script

This script moves converted HEIC files to an archive directory.
It identifies HEIC files that have corresponding JPEG files and archives them.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def find_converted_heic_files(src_dir: str, dest_dir: str) -> list:
    """
    Find HEIC files that have corresponding JPEG files in the destination.
    
    Args:
        src_dir: Source directory containing HEIC files
        dest_dir: Destination directory containing converted JPEG files
    
    Returns:
        List of tuples: (heic_path, jpeg_path)
    """
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    converted_pairs = []
    
    # Find all HEIC files
    heic_files = list(src_path.rglob('*.heic'))
    heic_files.extend(list(src_path.rglob('*.HEIC')))
    
    for heic_file in heic_files:
        # Calculate expected JPEG path
        rel_path = heic_file.relative_to(src_path)
        expected_jpeg = dest_path / rel_path.with_suffix('.jpg')
        
        if expected_jpeg.exists():
            converted_pairs.append((heic_file, expected_jpeg))
    
    return converted_pairs


def archive_heic_files(converted_pairs: list, archive_dir: str, dry_run: bool = False) -> dict:
    """
    Move converted HEIC files to archive directory.
    
    Args:
        converted_pairs: List of (heic_path, jpeg_path) tuples
        archive_dir: Directory to archive HEIC files to
        dry_run: If True, only show what would be archived
    
    Returns:
        Dictionary with archive results
    """
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    results = {
        'archived': [],
        'errors': []
    }
    
    if dry_run:
        print(f"\nDry Run: Would archive {len(converted_pairs)} HEIC files to {archive_dir}:")
        for heic_file, jpeg_file in converted_pairs:
            print(f"  {heic_file}")
        return results
    
    print(f"\nArchiving {len(converted_pairs)} HEIC files...")
    
    for heic_file, jpeg_file in converted_pairs:
        try:
            # Create archive subdirectory structure
            src_root = heic_file.parents[len(heic_file.parents) - 2]  # Get original source root
            rel_path = heic_file.relative_to(src_root)
            archive_dest = archive_path / rel_path
            
            # Create destination directory
            archive_dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the HEIC file
            shutil.move(str(heic_file), str(archive_dest))
            
            results['archived'].append({
                'original': str(heic_file),
                'archive': str(archive_dest),
                'jpeg': str(jpeg_file)
            })
            
            print(f"Archived: {heic_file.name}")
            
        except Exception as e:
            results['errors'].append({
                'file': str(heic_file),
                'error': str(e)
            })
            print(f"Error archiving {heic_file.name}: {e}")
    
    return results


def save_archive_report(results: dict, reports_dir: str):
    """Save archive operation report."""
    reports_path = Path(reports_dir)
    reports_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_path / f"heic_archive_simple_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write("HEIC Archive Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Successfully Archived ({len(results['archived'])}):\n")
        f.write("-" * 30 + "\n")
        for item in results['archived']:
            f.write(f"Original: {item['original']}\n")
            f.write(f"Archive: {item['archive']}\n")
            f.write(f"JPEG: {item['jpeg']}\n")
            f.write("-" * 30 + "\n")
        
        if results['errors']:
            f.write(f"\nArchive Errors ({len(results['errors'])}):\n")
            f.write("-" * 30 + "\n")
            for error in results['errors']:
                f.write(f"File: {error['file']}\n")
                f.write(f"Error: {error['error']}\n")
                f.write("-" * 30 + "\n")
    
    print(f"Archive report saved to: {report_file}")


def main():
    """Main archiving workflow."""
    
    # Define your directories - UPDATE THESE PATHS
    src_directory = r'W:\Organized'           # Where your HEIC files are
    dest_directory = r'W:\Convert to Jpeg'   # Where your JPEG files are
    archive_directory = r'W:\HEIC_Archive'   # Where to archive HEIC files
    
    # Reports directory
    reports_directory = str(Path(__file__).parent.parent / "reports")
    
    print("=" * 60)
    print("SIMPLE HEIC ARCHIVE TOOL")
    print("=" * 60)
    print(f"Source: {src_directory}")
    print(f"Destination: {dest_directory}")
    print(f"Archive: {archive_directory}")
    
    try:
        # Step 1: Find converted pairs
        print("\n1. Finding HEIC files with corresponding JPEG files...")
        converted_pairs = find_converted_heic_files(src_directory, dest_directory)
        
        if not converted_pairs:
            print("No converted HEIC files found to archive.")
            return 0
        
        print(f"Found {len(converted_pairs)} HEIC files that have been converted to JPEG")
        
        # Step 2: Show what would be archived (dry run)
        print("\n2. Dry run - showing what would be archived...")
        archive_heic_files(converted_pairs, archive_directory, dry_run=True)
        
        # Step 3: Confirm archiving
        response = input(f"\nDo you want to archive {len(converted_pairs)} HEIC files? (y/N): ")
        if response.lower() == 'y':
            print("\n3. Archiving HEIC files...")
            results = archive_heic_files(converted_pairs, archive_directory, dry_run=False)
            
            # Save report
            save_archive_report(results, reports_directory)
            
            print(f"\nArchiving completed!")
            print(f"  Successfully archived: {len(results['archived'])}")
            print(f"  Errors: {len(results['errors'])}")
            
            if results['errors']:
                print("\nSome files had errors - check the archive report for details.")
        else:
            print("Archiving cancelled.")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
