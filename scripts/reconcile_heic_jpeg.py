#!/usr/bin/env python3
"""
HEIC/JPEG Reconciliation Script

This script compares HEIC files with their converted JPEG counterparts to:
1. Show which HEIC files have been successfully converted
2. Identify HEIC files that still need conversion
3. Find orphaned JPEG files (no corresponding HEIC)
4. Generate detailed reconciliation reports
"""

import os
from pathlib import Path
from datetime import datetime


def analyze_conversion_status(src_dir: str, dest_dir: str) -> dict:
    """
    Analyze the conversion status between HEIC and JPEG files.
    
    Args:
        src_dir: Source directory containing HEIC files
        dest_dir: Destination directory containing JPEG files
    
    Returns:
        Dictionary with analysis results
    """
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # Find all HEIC files
    heic_files = set()
    for pattern in ['*.heic', '*.HEIC']:
        heic_files.update(src_path.rglob(pattern))
    
    # Find all JPEG files in destination
    jpeg_files = set()
    for pattern in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        jpeg_files.update(dest_path.rglob(pattern))
    
    # Analysis results
    results = {
        'converted_pairs': [],      # HEIC files with corresponding JPEG
        'unconverted_heic': [],     # HEIC files without JPEG
        'orphaned_jpeg': [],        # JPEG files without HEIC
        'summary': {}
    }
    
    # Track which JPEG files have corresponding HEIC
    matched_jpegs = set()
    
    # Check each HEIC file for corresponding JPEG
    for heic_file in heic_files:
        # Calculate expected JPEG path
        rel_path = heic_file.relative_to(src_path)
        expected_jpeg = dest_path / rel_path.with_suffix('.jpg')
        
        if expected_jpeg.exists():
            # Found converted pair
            heic_stat = heic_file.stat()
            jpeg_stat = expected_jpeg.stat()
            
            results['converted_pairs'].append({
                'heic_path': heic_file,
                'jpeg_path': expected_jpeg,
                'heic_size': heic_stat.st_size,
                'jpeg_size': jpeg_stat.st_size,
                'heic_modified': datetime.fromtimestamp(heic_stat.st_mtime),
                'jpeg_modified': datetime.fromtimestamp(jpeg_stat.st_mtime),
                'size_reduction': round((1 - jpeg_stat.st_size / heic_stat.st_size) * 100, 1)
            })
            matched_jpegs.add(expected_jpeg)
        else:
            # HEIC file without corresponding JPEG
            results['unconverted_heic'].append({
                'path': heic_file,
                'size': heic_file.stat().st_size,
                'modified': datetime.fromtimestamp(heic_file.stat().st_mtime)
            })
    
    # Find orphaned JPEG files
    for jpeg_file in jpeg_files:
        if jpeg_file not in matched_jpegs:
            results['orphaned_jpeg'].append({
                'path': jpeg_file,
                'size': jpeg_file.stat().st_size,
                'modified': datetime.fromtimestamp(jpeg_file.stat().st_mtime)
            })
    
    # Calculate summary statistics
    total_heic = len(heic_files)
    converted_count = len(results['converted_pairs'])
    unconverted_count = len(results['unconverted_heic'])
    orphaned_count = len(results['orphaned_jpeg'])
    
    total_heic_size = sum(item['heic_size'] for item in results['converted_pairs']) + \
                     sum(item['size'] for item in results['unconverted_heic'])
    total_jpeg_size = sum(item['jpeg_size'] for item in results['converted_pairs'])
    
    results['summary'] = {
        'total_heic_files': total_heic,
        'converted_files': converted_count,
        'unconverted_files': unconverted_count,
        'orphaned_jpeg_files': orphaned_count,
        'conversion_rate': round((converted_count / total_heic * 100), 1) if total_heic > 0 else 0,
        'total_heic_size_mb': round(total_heic_size / (1024 * 1024), 2),
        'total_jpeg_size_mb': round(total_jpeg_size / (1024 * 1024), 2),
        'space_saved_mb': round((total_heic_size - total_jpeg_size) / (1024 * 1024), 2),
        'average_size_reduction': round(
            sum(item['size_reduction'] for item in results['converted_pairs']) / converted_count, 1
        ) if converted_count > 0 else 0
    }
    
    return results


def save_reconciliation_report(results: dict, reports_dir: str, src_dir: str, dest_dir: str):
    """Save detailed reconciliation report."""
    reports_path = Path(reports_dir)
    reports_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_path / f"heic_jpeg_reconciliation_{timestamp}.txt"
    
    summary = results['summary']
    
    with open(report_file, 'w') as f:
        f.write("HEIC/JPEG RECONCILIATION REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source Directory: {src_dir}\n")
        f.write(f"Destination Directory: {dest_dir}\n\n")
        
        # Summary Statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total HEIC Files: {summary['total_heic_files']}\n")
        f.write(f"Successfully Converted: {summary['converted_files']}\n")
        f.write(f"Not Yet Converted: {summary['unconverted_files']}\n")
        f.write(f"Orphaned JPEG Files: {summary['orphaned_jpeg_files']}\n")
        f.write(f"Conversion Rate: {summary['conversion_rate']}%\n\n")
        
        f.write(f"Storage Analysis:\n")
        f.write(f"  Total HEIC Size: {summary['total_heic_size_mb']} MB\n")
        f.write(f"  Total JPEG Size: {summary['total_jpeg_size_mb']} MB\n")
        f.write(f"  Space Saved: {summary['space_saved_mb']} MB\n")
        f.write(f"  Average Size Reduction: {summary['average_size_reduction']}%\n\n")
        
        # Converted Pairs
        if results['converted_pairs']:
            f.write(f"SUCCESSFULLY CONVERTED ({len(results['converted_pairs'])} files)\n")
            f.write("-" * 50 + "\n")
            for pair in results['converted_pairs']:
                f.write(f"HEIC: {pair['heic_path']}\n")
                f.write(f"JPEG: {pair['jpeg_path']}\n")
                f.write(f"Size: {pair['heic_size']:,} → {pair['jpeg_size']:,} bytes ({pair['size_reduction']}% reduction)\n")
                f.write(f"Modified: HEIC {pair['heic_modified']} → JPEG {pair['jpeg_modified']}\n")
                f.write("-" * 30 + "\n")
        
        # Unconverted HEIC files
        if results['unconverted_heic']:
            f.write(f"\nNOT YET CONVERTED ({len(results['unconverted_heic'])} files)\n")
            f.write("-" * 50 + "\n")
            for heic in results['unconverted_heic']:
                f.write(f"File: {heic['path']}\n")
                f.write(f"Size: {heic['size']:,} bytes\n")
                f.write(f"Modified: {heic['modified']}\n")
                f.write("-" * 30 + "\n")
        
        # Orphaned JPEG files
        if results['orphaned_jpeg']:
            f.write(f"\nORPHANED JPEG FILES ({len(results['orphaned_jpeg'])} files)\n")
            f.write("-" * 50 + "\n")
            f.write("These JPEG files don't have corresponding HEIC files:\n\n")
            for jpeg in results['orphaned_jpeg']:
                f.write(f"File: {jpeg['path']}\n")
                f.write(f"Size: {jpeg['size']:,} bytes\n")
                f.write(f"Modified: {jpeg['modified']}\n")
                f.write("-" * 30 + "\n")
    
    print(f"Detailed reconciliation report saved to: {report_file}")


def main():
    """Main reconciliation workflow."""
    
    # Define your directories - UPDATE THESE PATHS
    src_directory = r'W:\Organized'           # Where your HEIC files are
    dest_directory = r'W:\Convert to Jpeg'   # Where your JPEG files are
    
    # Reports directory
    reports_directory = str(Path(__file__).parent.parent / "reports")
    
    print("=" * 60)
    print("HEIC/JPEG RECONCILIATION TOOL")
    print("=" * 60)
    print(f"Source: {src_directory}")
    print(f"Destination: {dest_directory}")
    
    try:
        # Analyze conversion status
        print("\nAnalyzing HEIC/JPEG conversion status...")
        results = analyze_conversion_status(src_directory, dest_directory)
        
        # Display summary
        summary = results['summary']
        print(f"\n📊 SUMMARY REPORT")
        print(f"{'=' * 40}")
        print(f"Total HEIC Files: {summary['total_heic_files']}")
        print(f"Successfully Converted: {summary['converted_files']}")
        print(f"Not Yet Converted: {summary['unconverted_files']}")
        print(f"Orphaned JPEG Files: {summary['orphaned_jpeg_files']}")
        print(f"Conversion Rate: {summary['conversion_rate']}%")
        
        print(f"\n💾 STORAGE ANALYSIS")
        print(f"{'=' * 40}")
        print(f"Total HEIC Size: {summary['total_heic_size_mb']} MB")
        print(f"Total JPEG Size: {summary['total_jpeg_size_mb']} MB")
        print(f"Space Saved: {summary['space_saved_mb']} MB")
        print(f"Average Size Reduction: {summary['average_size_reduction']}%")
        
        # Show details for different categories
        if results['converted_pairs']:
            print(f"\n✅ CONVERTED FILES ({len(results['converted_pairs'])} files)")
            print("Recent conversions:")
            for pair in sorted(results['converted_pairs'], 
                             key=lambda x: x['jpeg_modified'], reverse=True)[:5]:
                print(f"  • {pair['heic_path'].name} → {pair['jpeg_path'].name} "
                      f"({pair['size_reduction']}% size reduction)")
            if len(results['converted_pairs']) > 5:
                print(f"  ... and {len(results['converted_pairs']) - 5} more")
        
        if results['unconverted_heic']:
            print(f"\n⏳ NOT YET CONVERTED ({len(results['unconverted_heic'])} files)")
            print("Files that still need conversion:")
            for heic in results['unconverted_heic'][:5]:
                size_mb = round(heic['size'] / (1024 * 1024), 1)
                print(f"  • {heic['path'].name} ({size_mb} MB)")
            if len(results['unconverted_heic']) > 5:
                print(f"  ... and {len(results['unconverted_heic']) - 5} more")
        
        if results['orphaned_jpeg']:
            print(f"\n🔍 ORPHANED JPEG FILES ({len(results['orphaned_jpeg'])} files)")
            print("JPEG files without corresponding HEIC files:")
            for jpeg in results['orphaned_jpeg'][:5]:
                print(f"  • {jpeg['path'].name}")
            if len(results['orphaned_jpeg']) > 5:
                print(f"  ... and {len(results['orphaned_jpeg']) - 5} more")
        
        # Save detailed report
        save_reconciliation_report(results, reports_directory, src_directory, dest_directory)
        print(f"\n📄 A detailed report has been saved to the reports folder.")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print(f"{'=' * 40}")
        if results['unconverted_heic']:
            print(f"• Run HEIC conversion script to convert {len(results['unconverted_heic'])} remaining files")
        if results['converted_pairs']:
            print(f"• Consider archiving {len(results['converted_pairs'])} converted HEIC files")
        if results['orphaned_jpeg']:
            print(f"• Review {len(results['orphaned_jpeg'])} orphaned JPEG files")
        
        if summary['conversion_rate'] == 100:
            print("🎉 All HEIC files have been successfully converted!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
