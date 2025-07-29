#!/usr/bin/env python3
"""
HEIC File Conversion Script

This script specifically handles HEIC files with EXIF validation.
It scans for HEIC files, validates they have creation dates, and converts them safely.
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from heic_converter import HeicConverter


def main():
    """Convert HEIC files with EXIF validation."""
    
    # Define your source and destination directories
    # Update these paths to match your actual directories
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'
    
    print("=" * 60)
    print("HEIC FILE CONVERSION WITH EXIF VALIDATION")
    print("=" * 60)
    
    try:
        # Create HEIC converter
        heic_converter = HeicConverter(src_directory, dest_directory)
        
        # Step 1: Scan HEIC files for EXIF validation
        print("\n1. Scanning HEIC files for EXIF validation...")
        scan_results = heic_converter.scan_heic_files()
        
        convertible_count = len(scan_results['convertible'])
        missing_date_count = len(scan_results['missing_date'])
        error_count = len(scan_results['errors'])
        
        if convertible_count == 0:
            print("No HEIC files with creation dates found.")
            return
        
        # Step 2: Show what would be converted (dry run)
        print(f"\n2. Dry run - showing what {convertible_count} HEIC files would be converted...")
        heic_converter.convert_all_heic(dry_run=True)
        
        # Step 3: Ask user if they want to proceed
        print(f"\n{'='*60}")
        print("CONVERSION SUMMARY:")
        print(f"  ✅ Ready to convert: {convertible_count} files")
        print(f"  ❌ Missing creation date: {missing_date_count} files")
        print(f"  ⚠️  Processing errors: {error_count} files")
        print(f"{'='*60}")
        
        response = input("\nProceed with actual conversion? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n3. Converting HEIC files...")
            conversion_results = heic_converter.convert_all_heic(dry_run=False)
            
            print(f"\n{'='*60}")
            print("CONVERSION COMPLETED!")
            print(f"  Successfully converted: {len(conversion_results['converted'])} files")
            print(f"  Conversion errors: {len(conversion_results['errors'])} files")
            print(f"{'='*60}")
            print("\nCheck the 'reports' folder for detailed conversion logs.")
        else:
            print("\nConversion cancelled. Use this script again when ready to convert.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please update the source and destination directory paths in this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
