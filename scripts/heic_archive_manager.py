#!/usr/bin/env python3
"""
HEIC Archive Manager

This script handles post-conversion tasks:
1. Reconciles HEIC files with their converted JPEG counterparts
2. Moves converted HEIC files to an archive directory
3. Tracks conversion history to prevent re-conversion
4. Provides rollback capabilities
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
import json

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from heic_converter import HeicConverter


class HeicArchiveManager:
    """Manages archiving and reconciliation of converted HEIC files."""
    
    def __init__(self, src_dir: str, dest_dir: str, archive_dir: str):
        self.src_dir = Path(src_dir)
        self.dest_dir = Path(dest_dir)
        self.archive_dir = Path(archive_dir)
        
        # Create archive directory if it doesn't exist
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Reports directory
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Conversion tracking file
        self.tracking_file = self.reports_dir / "conversion_tracking.json"
        self.load_tracking_data()
    
    def load_tracking_data(self):
        """Load the conversion tracking data."""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                self.tracking_data = json.load(f)
        else:
            self.tracking_data = {
                'converted_files': {},  # heic_path: {jpeg_path, archive_path, date}
                'archive_history': []
            }
    
    def save_tracking_data(self):
        """Save the conversion tracking data."""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
    
    def find_converted_pairs(self) -> List[Dict]:
        """
        Find HEIC files that have corresponding JPEG files.
        Returns list of dictionaries with file pair information.
        """
        converted_pairs = []
        
        # Find all HEIC files in source
        heic_files = list(self.src_dir.rglob('*.heic'))
        heic_files.extend(list(self.src_dir.rglob('*.HEIC')))
        
        for heic_path in heic_files:
            # Calculate expected JPEG path
            rel_path = heic_path.relative_to(self.src_dir)
            expected_jpeg = self.dest_dir / rel_path.with_suffix('.jpg')
            
            if expected_jpeg.exists():
                # Check if already tracked
                heic_str = str(heic_path)
                already_archived = heic_str in self.tracking_data['converted_files']
                
                pair_info = {
                    'heic_path': heic_path,
                    'jpeg_path': expected_jpeg,
                    'already_archived': already_archived,
                    'heic_size': heic_path.stat().st_size,
                    'jpeg_size': expected_jpeg.stat().st_size,
                    'conversion_verified': True
                }
                
                if already_archived:
                    pair_info['archive_info'] = self.tracking_data['converted_files'][heic_str]
                
                converted_pairs.append(pair_info)
        
        return converted_pairs
    
    def reconcile_conversions(self, save_report: bool = True) -> Dict:
        """
        Reconcile HEIC files with their JPEG counterparts.
        Returns summary of reconciliation results.
        """
        print("Scanning for converted HEIC/JPEG pairs...")
        
        converted_pairs = self.find_converted_pairs()
        
        summary = {
            'total_heic_files': len(list(self.src_dir.rglob('*.heic'))) + len(list(self.src_dir.rglob('*.HEIC'))),
            'converted_pairs': len(converted_pairs),
            'already_archived': len([p for p in converted_pairs if p['already_archived']]),
            'ready_for_archive': len([p for p in converted_pairs if not p['already_archived']]),
            'pairs': converted_pairs
        }
        
        if save_report:
            self._save_reconciliation_report(summary)
        
        return summary
    
    def archive_converted_heic_files(self, dry_run: bool = False) -> Dict:
        """
        Move converted HEIC files to archive directory.
        
        Args:
            dry_run: If True, only show what would be archived
        
        Returns:
            Archive operation results
        """
        reconcile_results = self.reconcile_conversions(save_report=False)
        ready_for_archive = [p for p in reconcile_results['pairs'] if not p['already_archived']]
        
        if not ready_for_archive:
            print("No HEIC files ready for archiving.")
            return {'archived': [], 'skipped': [], 'errors': []}
        
        if dry_run:
            print(f"\nDry Run: Would archive {len(ready_for_archive)} HEIC files:")
            for pair in ready_for_archive:
                rel_path = pair['heic_path'].relative_to(self.src_dir)
                archive_path = self.archive_dir / rel_path
                print(f"  {pair['heic_path']} -> {archive_path}")
            return {'archived': [], 'skipped': ready_for_archive, 'errors': []}
        
        # Actual archiving
        results = {'archived': [], 'skipped': [], 'errors': []}
        
        print(f"\nArchiving {len(ready_for_archive)} converted HEIC files...")
        
        for pair in ready_for_archive:
            try:
                heic_path = pair['heic_path']
                rel_path = heic_path.relative_to(self.src_dir)
                archive_path = self.archive_dir / rel_path
                
                # Create archive directory structure
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the HEIC file
                shutil.move(str(heic_path), str(archive_path))
                
                # Update tracking data
                self.tracking_data['converted_files'][str(heic_path)] = {
                    'jpeg_path': str(pair['jpeg_path']),
                    'archive_path': str(archive_path),
                    'archived_date': datetime.now().isoformat(),
                    'original_size': pair['heic_size'],
                    'jpeg_size': pair['jpeg_size']
                }
                
                self.tracking_data['archive_history'].append({
                    'heic_path': str(heic_path),
                    'archive_path': str(archive_path),
                    'archived_date': datetime.now().isoformat()
                })
                
                results['archived'].append({
                    'heic_path': str(heic_path),
                    'archive_path': str(archive_path),
                    'jpeg_path': str(pair['jpeg_path'])
                })
                
                print(f"Archived: {heic_path} -> {archive_path}")
                
            except Exception as e:
                error_info = {
                    'heic_path': str(pair['heic_path']),
                    'error': str(e)
                }
                results['errors'].append(error_info)
                print(f"Error archiving {pair['heic_path']}: {e}")
        
        # Save tracking data
        self.save_tracking_data()
        
        # Save archive report
        self._save_archive_report(results)
        
        print(f"\nArchiving completed:")
        print(f"  Successfully archived: {len(results['archived'])}")
        print(f"  Errors: {len(results['errors'])}")
        
        return results
    
    def restore_from_archive(self, heic_filename: str) -> bool:
        """
        Restore a specific HEIC file from archive back to original location.
        
        Args:
            heic_filename: Name of the HEIC file to restore
        
        Returns:
            True if successful, False otherwise
        """
        # Find the file in tracking data
        for original_path, archive_info in self.tracking_data['converted_files'].items():
            if Path(original_path).name.lower() == heic_filename.lower():
                archive_path = Path(archive_info['archive_path'])
                
                if archive_path.exists():
                    try:
                        # Move back to original location
                        original_path_obj = Path(original_path)
                        original_path_obj.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(archive_path), str(original_path_obj))
                        
                        # Remove from tracking
                        del self.tracking_data['converted_files'][original_path]
                        self.save_tracking_data()
                        
                        print(f"Restored: {archive_path} -> {original_path_obj}")
                        return True
                    except Exception as e:
                        print(f"Error restoring {heic_filename}: {e}")
                        return False
                else:
                    print(f"Archive file not found: {archive_path}")
                    return False
        
        print(f"No archive record found for: {heic_filename}")
        return False
    
    def _save_reconciliation_report(self, summary: Dict):
        """Save reconciliation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"heic_reconciliation_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("HEIC/JPEG Reconciliation Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Total HEIC files found: {summary['total_heic_files']}\n")
            f.write(f"Converted pairs found: {summary['converted_pairs']}\n")
            f.write(f"Already archived: {summary['already_archived']}\n")
            f.write(f"Ready for archiving: {summary['ready_for_archive']}\n\n")
            
            f.write("Converted Pairs:\n")
            f.write("-" * 30 + "\n")
            for pair in summary['pairs']:
                f.write(f"HEIC: {pair['heic_path']}\n")
                f.write(f"JPEG: {pair['jpeg_path']}\n")
                f.write(f"Already Archived: {pair['already_archived']}\n")
                f.write(f"HEIC Size: {pair['heic_size']:,} bytes\n")
                f.write(f"JPEG Size: {pair['jpeg_size']:,} bytes\n")
                if pair['already_archived']:
                    f.write(f"Archive Info: {pair['archive_info']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Reconciliation report saved to: {report_file}")
    
    def _save_archive_report(self, results: Dict):
        """Save archive operation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"heic_archive_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("HEIC Archive Operation Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Successfully Archived ({len(results['archived'])}):\n")
            f.write("-" * 30 + "\n")
            for item in results['archived']:
                f.write(f"Original: {item['heic_path']}\n")
                f.write(f"Archive: {item['archive_path']}\n")
                f.write(f"JPEG: {item['jpeg_path']}\n")
                f.write("-" * 30 + "\n")
            
            if results['errors']:
                f.write(f"\nArchive Errors ({len(results['errors'])}):\n")
                f.write("-" * 30 + "\n")
                for error in results['errors']:
                    f.write(f"File: {error['heic_path']}\n")
                    f.write(f"Error: {error['error']}\n")
                    f.write("-" * 30 + "\n")
        
        print(f"Archive report saved to: {report_file}")


def main():
    """Main archive management workflow."""
    
    # Define your directories
    # Update these paths to match your actual directories
    src_directory = r'W:\Organized'
    dest_directory = r'W:\Convert to Jpeg'
    archive_directory = r'W:\HEIC_Archive'  # New archive location
    
    print("=" * 60)
    print("HEIC ARCHIVE MANAGER")
    print("=" * 60)
    
    try:
        # Create archive manager
        manager = HeicArchiveManager(src_directory, dest_directory, archive_directory)
        
        # Step 1: Reconcile conversions
        print("\n1. Reconciling HEIC files with JPEG conversions...")
        reconcile_results = manager.reconcile_conversions()
        
        print(f"\nReconciliation Summary:")
        print(f"  Total HEIC files: {reconcile_results['total_heic_files']}")
        print(f"  Converted pairs: {reconcile_results['converted_pairs']}")
        print(f"  Already archived: {reconcile_results['already_archived']}")
        print(f"  Ready for archive: {reconcile_results['ready_for_archive']}")
        
        if reconcile_results['ready_for_archive'] == 0:
            print("\nNo files ready for archiving.")
            return
        
        # Step 2: Show what would be archived (dry run)
        print(f"\n2. Dry run - showing what would be archived...")
        manager.archive_converted_heic_files(dry_run=True)
        
        # Step 3: Confirm archiving
        response = input(f"\nDo you want to archive {reconcile_results['ready_for_archive']} HEIC files? (y/N): ")
        if response.lower() == 'y':
            print("\n3. Archiving converted HEIC files...")
            archive_results = manager.archive_converted_heic_files(dry_run=False)
            print("\nArchiving completed successfully!")
        else:
            print("Archiving cancelled.")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
