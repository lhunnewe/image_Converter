#!/usr/bin/env python3
"""
Comprehensive Media Analysis Script

This script performs a complete analysis of your media collection,
including scanning, HEIC validation, and generating conversion recommendations.
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import ImageConverter


def main():
    """Perform comprehensive media analysis and conversion planning."""
    
    # Define your source and destination directories
    # Update these paths to match your actual directories
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'
    
    print("=" * 70)
    print("COMPREHENSIVE MEDIA ANALYSIS AND CONVERSION PLANNING")
    print("=" * 70)
    
    try:
        # Initialize the main converter
        converter = ImageConverter(src_directory, dest_directory)
        
        # Perform comprehensive scan and generate conversion plan
        print("\nPerforming comprehensive analysis...")
        full_analysis = converter.comprehensive_scan_and_convert_plan()
        
        print(f"\n{'='*70}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*70}")
        print("\nCheck the 'reports' folder for detailed log files.")
        print("\nNext steps:")
        print("1. Review the generated reports")
        print("2. Use specific conversion scripts for actual conversion")
        print("3. Consider running heic_conversion.py for HEIC files")
        print("4. Use general_conversion.py for other image types")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please update the source and destination directory paths in this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
