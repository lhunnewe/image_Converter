#!/usr/bin/env python3
"""
File Organization Script

This script helps organize media files into date-based folders (YYYY/MM)
based on their EXIF creation dates.
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import ImageConverter


def main():
    """Organize media files into date-based folders."""
    
    # Define your source directory
    # Update this path to match your actual directory
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'  # Required for ImageConverter initialization
    
    print("=" * 60)
    print("MEDIA FILE ORGANIZATION BY DATE")
    print("=" * 60)
    
    try:
        # Initialize the converter
        converter = ImageConverter(src_directory, dest_directory)
        
        print("\nThis script will move media files into YYYY/MM folders based on their EXIF creation dates.")
        print("Files already in date-organized folders will be skipped.")
        print("Files without creation dates will be skipped and reported.")
        
        print(f"\nSource directory: {src_directory}")
        
        response = input("\nProceed with organizing files? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\nOrganizing files by date...")
            converter.move_images_to_date_folders()
            
            print(f"\n{'='*60}")
            print("ORGANIZATION COMPLETED!")
            print(f"{'='*60}")
            print("Files have been moved into YYYY/MM folders based on their creation dates.")
            print("Check the console output above for any files that couldn't be processed.")
        else:
            print("\nOrganization cancelled.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please update the source directory path in this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


def analyze_organization():
    """Analyze current organization without moving files."""
    
    src_directory = r'W:\Organized'
    
    try:
        # Use MediaFileScanner directly for analysis
        sys.path.append(str(Path(__file__).parent.parent / "src"))
        from media_scanner import MediaFileScanner
        
        scanner = MediaFileScanner(src_directory)
        org_analysis = scanner.analyze_directory_structure()
        
        print("\n" + "=" * 60)
        print("CURRENT ORGANIZATION ANALYSIS")
        print("=" * 60)
        
        print(f"Organization level: {org_analysis['organization_percentage']:.1f}%")
        print(f"Files in date-organized folders: {org_analysis['organized_by_date']}")
        print(f"Year folders found: {org_analysis['year_folders']}")
        print(f"Unorganized files: {len(org_analysis['unorganized_files'])}")
        
        if org_analysis['folder_patterns']:
            print("\nExisting date folder patterns:")
            for pattern, count in sorted(org_analysis['folder_patterns'].items()):
                print(f"  {pattern}: {count} files")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Organize files by date (move files)")
    print("2. Analyze current organization (no changes)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        analyze_organization()
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")
