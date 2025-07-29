#!/usr/bin/env python3
"""
General Image Conversion Script

This script handles conversion of general image formats (PNG, TIFF, etc.) to JPEG.
Use this for non-HEIC images after running media scanning.
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import ImageConverter


def main():
    """Convert general image files to JPEG."""
    
    # Define your source and destination directories
    # Update these paths to match your actual directories
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'
    
    print("=" * 60)
    print("GENERAL IMAGE CONVERSION TO JPEG")
    print("=" * 60)
    
    try:
        # Initialize the converter
        converter = ImageConverter(src_directory, dest_directory)
        
        # Step 1: Show what would be converted (dry run)
        print("\n1. Dry run - showing what files would be converted...")
        converter.dry_run()
        
        # Step 2: Ask user if they want to proceed
        print(f"\n{'='*60}")
        response = input("Proceed with actual conversion? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n2. Converting all supported files...")
            converter.convert_all_with_progress()
            
            print(f"\n{'='*60}")
            print("CONVERSION COMPLETED!")
            print(f"{'='*60}")
            print("Check the 'reports' folder for detailed conversion logs.")
        else:
            print("\nConversion cancelled. Use this script again when ready to convert.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please update the source and destination directory paths in this script.")
    except Exception as e:
        print(f"An error occurred: {e}")


def convert_specific_month():
    """Convert images from a specific year and month."""
    
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'
    
    try:
        converter = ImageConverter(src_directory, dest_directory)
        
        print("\n" + "=" * 60)
        print("CONVERT SPECIFIC MONTH")
        print("=" * 60)
        
        year = input("Enter year (YYYY): ").strip()
        month = input("Enter month (MM): ").strip()
        
        if len(year) != 4 or not year.isdigit():
            print("Invalid year format. Please use YYYY format.")
            return
            
        if len(month) != 2 or not month.isdigit() or int(month) < 1 or int(month) > 12:
            print("Invalid month format. Please use MM format (01-12).")
            return
        
        print(f"\nConverting images from {year}/{month}...")
        converter.convert_specific_month(year, month)
        print("Conversion completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Convert all supported files")
    print("2. Convert specific month")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        convert_specific_month()
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")
