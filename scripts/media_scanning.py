#!/usr/bin/env python3
"""
Media File Scanning Script

This script performs comprehensive scanning of media files to understand
what's in your collection and what needs conversion.
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from media_scanner import MediaFileScanner


def main():
    """Scan media files and generate detailed reports."""
    
    # Define your source directory
    # Update this path to match your actual directory
    src_directory = r'W:\Organized'
    
    print("=" * 60)
    print("COMPREHENSIVE MEDIA FILE SCANNING")
    print("=" * 60)
    
    try:
        # Create media scanner
        scanner = MediaFileScanner(src_directory)
        
        # Step 1: Scan for conversion readiness
        print("\n1. Scanning all media files for conversion readiness...")
        scan_results = scanner.scan_for_conversion_readiness()
        
        # Step 2: Analyze directory organization
        print("\n2. Analyzing directory organization...")
        org_analysis = scanner.analyze_directory_structure()
        
        print(f"\nDirectory Organization Analysis:")
        print(f"  Organization level: {org_analysis['organization_percentage']:.1f}% of files are in date-organized folders")
        print(f"  Year folders found: {len(org_analysis['year_folders'])} years")
        print(f"  Unorganized files: {len(org_analysis['unorganized_files'])} files")
        
        # Step 3: Quick duplicate check
        print("\n3. Performing quick duplicate scan...")
        duplicate_check = scanner.quick_duplicate_scan()
        
        print(f"\nDuplicate Analysis:")
        print(f"  Potential duplicate groups: {duplicate_check['potential_duplicate_groups']}")
        print(f"  Total potential duplicates: {duplicate_check['total_potential_duplicates']}")
        
        # Summary
        summary = scan_results['summary']
        print(f"\n{'='*60}")
        print("SCANNING COMPLETED!")
        print(f"{'='*60}")
        print(f"Total media files: {summary['total_files']}")
        print(f"Files needing conversion: {summary['needs_conversion_count']}")
        print(f"HEIC files: {summary['heic_count']}")
        print(f"Already JPEG: {summary['already_jpeg_count']}")
        print(f"Video files: {summary['videos_count']}")
        print(f"Files with errors: {summary['error_count']}")
        print(f"{'='*60}")
        print("\nDetailed reports saved to 'reports' folder.")
        print("\nNext steps:")
        print("- Review the generated reports")
        print("- Use heic_conversion.py for HEIC files")
        print("- Use general_conversion.py for other image types")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please update the source directory path in this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
