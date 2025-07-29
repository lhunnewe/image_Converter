import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import hashlib

class MediaFileScanner:
    """
    A utility class for scanning and analyzing media files before conversion.
    Provides detailed reporting on what can and cannot be converted.
    """
    
    SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.heic', '.tiff', '.gif']
    SUPPORTED_VIDEO_TYPES = ['.mov', '.mp4', '.mts']
    ALL_SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES + SUPPORTED_VIDEO_TYPES
    
    def __init__(self, src_root: str):
        self.src_root = Path(src_root)
        self.excluded_paths = ['.dtrash']
        
        if not self.src_root.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.src_root}")
        
        # Create reports directory
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def is_excluded_path(self, path: Path) -> bool:
        """Check if the path contains any excluded directory names."""
        return any(excluded in path.parts for excluded in self.excluded_paths)
    
    def get_all_media_files(self) -> List[Path]:
        """Get all supported media files from the source directory."""
        media_files = []
        for file_path in self.src_root.rglob('*'):
            if (file_path.is_file() 
                and file_path.suffix.lower() in self.ALL_SUPPORTED_TYPES
                and not self.is_excluded_path(file_path)):
                media_files.append(file_path)
        return media_files
    
    def get_file_metadata_basic(self, file_path: Path) -> Dict:
        """
        Get basic metadata for a file without heavy processing.
        This is a lightweight scan for initial assessment.
        """
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.src_root)),
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified_date': datetime.fromtimestamp(stat.st_mtime),
                'file_type': file_path.suffix.lower(),
                'is_image': file_path.suffix.lower() in self.SUPPORTED_IMAGE_TYPES,
                'is_video': file_path.suffix.lower() in self.SUPPORTED_VIDEO_TYPES,
                'already_jpeg': file_path.suffix.lower() in ['.jpg', '.jpeg']
            }
        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e)
            }
    
    def scan_for_conversion_readiness(self, save_report: bool = True) -> Dict:
        """
        Scan all media files and categorize them by conversion readiness.
        This is a quick scan that doesn't read EXIF data.
        """
        media_files = self.get_all_media_files()
        
        scan_results = {
            'needs_conversion': [],  # Non-JPEG images that need conversion
            'already_jpeg': [],      # Already in JPEG format
            'videos': [],            # Video files (may need different handling)
            'heic_files': [],        # HEIC files (need special handling)
            'errors': [],            # Files that couldn't be processed
            'summary': {}
        }
        
        print(f"Scanning {len(media_files)} media files for conversion readiness...")
        
        for file_path in media_files:
            metadata = self.get_file_metadata_basic(file_path)
            
            if 'error' in metadata:
                scan_results['errors'].append(metadata)
                continue
            
            # Categorize files
            if metadata['file_type'] == '.heic':
                scan_results['heic_files'].append(metadata)
            elif metadata['already_jpeg']:
                scan_results['already_jpeg'].append(metadata)
            elif metadata['is_image']:
                scan_results['needs_conversion'].append(metadata)
            elif metadata['is_video']:
                scan_results['videos'].append(metadata)
        
        # Calculate summary statistics
        scan_results['summary'] = self._calculate_summary_stats(scan_results)
        
        # Print summary
        self._print_scan_summary(scan_results)
        
        if save_report:
            self._save_scan_readiness_report(scan_results)
        
        return scan_results
    
    def _calculate_summary_stats(self, scan_results: Dict) -> Dict:
        """Calculate summary statistics from scan results."""
        total_files = (len(scan_results['needs_conversion']) + 
                      len(scan_results['already_jpeg']) + 
                      len(scan_results['videos']) + 
                      len(scan_results['heic_files']))
        
        # Calculate total sizes
        def get_total_size(file_list):
            return sum(f.get('size_mb', 0) for f in file_list if 'size_mb' in f)
        
        # File type counts
        file_type_counts = defaultdict(int)
        for category in ['needs_conversion', 'already_jpeg', 'videos', 'heic_files']:
            for file_info in scan_results[category]:
                file_type = file_info.get('file_type', 'unknown')
                file_type_counts[file_type] += 1
        
        return {
            'total_files': total_files,
            'needs_conversion_count': len(scan_results['needs_conversion']),
            'already_jpeg_count': len(scan_results['already_jpeg']),
            'videos_count': len(scan_results['videos']),
            'heic_count': len(scan_results['heic_files']),
            'error_count': len(scan_results['errors']),
            'total_size_mb': get_total_size(scan_results['needs_conversion'] + 
                                          scan_results['already_jpeg'] + 
                                          scan_results['videos'] + 
                                          scan_results['heic_files']),
            'needs_conversion_size_mb': get_total_size(scan_results['needs_conversion']),
            'heic_size_mb': get_total_size(scan_results['heic_files']),
            'file_type_counts': dict(file_type_counts)
        }
    
    def _print_scan_summary(self, scan_results: Dict):
        """Print a summary of the scan results."""
        summary = scan_results['summary']
        
        print(f"\n" + "=" * 60)
        print("MEDIA FILE CONVERSION READINESS SCAN RESULTS")
        print("=" * 60)
        
        print(f"Total media files found: {summary['total_files']}")
        print(f"Total size: {summary['total_size_mb']:.1f} MB")
        print()
        
        print("Conversion Categories:")
        print(f"  📸 Images needing conversion: {summary['needs_conversion_count']} files ({summary['needs_conversion_size_mb']:.1f} MB)")
        print(f"  ✅ Already JPEG: {summary['already_jpeg_count']} files")
        print(f"  🎥 Video files: {summary['videos_count']} files")
        print(f"  📱 HEIC files: {summary['heic_count']} files ({summary['heic_size_mb']:.1f} MB)")
        print(f"  ❌ Errors: {summary['error_count']} files")
        print()
        
        print("File types found:")
        for file_type, count in sorted(summary['file_type_counts'].items()):
            print(f"  {file_type}: {count} files")
        
        print("=" * 60)
    
    def _save_scan_readiness_report(self, scan_results: Dict):
        """Save detailed scan results to report files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main summary report
        summary_file = self.reports_dir / f"media_scan_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("MEDIA FILE CONVERSION READINESS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source Directory: {self.src_root}\n\n")
            
            summary = scan_results['summary']
            f.write("SUMMARY:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total media files: {summary['total_files']}\n")
            f.write(f"Total size: {summary['total_size_mb']:.1f} MB\n\n")
            
            f.write("CONVERSION CATEGORIES:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Images needing conversion: {summary['needs_conversion_count']} files\n")
            f.write(f"Already JPEG: {summary['already_jpeg_count']} files\n")
            f.write(f"Video files: {summary['videos_count']} files\n")
            f.write(f"HEIC files: {summary['heic_count']} files\n")
            f.write(f"Errors: {summary['error_count']} files\n\n")
            
            f.write("FILE TYPES:\n")
            f.write("-" * 30 + "\n")
            for file_type, count in sorted(summary['file_type_counts'].items()):
                f.write(f"{file_type}: {count} files\n")
        
        print(f"Summary report saved to: {summary_file}")
        
        # Detailed files needing conversion
        if scan_results['needs_conversion']:
            conversion_file = self.reports_dir / f"files_needing_conversion_{timestamp}.txt"
            with open(conversion_file, 'w') as f:
                f.write("FILES THAT NEED CONVERSION TO JPEG\n")
                f.write("=" * 50 + "\n\n")
                
                for file_info in scan_results['needs_conversion']:
                    f.write(f"File: {file_info['path']}\n")
                    f.write(f"Type: {file_info['file_type']}\n")
                    f.write(f"Size: {file_info['size_mb']} MB\n")
                    f.write(f"Modified: {file_info['modified_date']}\n")
                    f.write("-" * 30 + "\n")
            
            print(f"Conversion list saved to: {conversion_file}")
        
        # HEIC files report (they need special handling)
        if scan_results['heic_files']:
            heic_file = self.reports_dir / f"heic_files_found_{timestamp}.txt"
            with open(heic_file, 'w') as f:
                f.write("HEIC FILES REQUIRING SPECIAL PROCESSING\n")
                f.write("=" * 50 + "\n")
                f.write("These files need EXIF validation before conversion.\n\n")
                
                for file_info in scan_results['heic_files']:
                    f.write(f"File: {file_info['path']}\n")
                    f.write(f"Size: {file_info['size_mb']} MB\n")
                    f.write(f"Modified: {file_info['modified_date']}\n")
                    f.write("-" * 30 + "\n")
            
            print(f"HEIC files report saved to: {heic_file}")
    
    def analyze_directory_structure(self) -> Dict:
        """
        Analyze the directory structure to understand organization patterns.
        This helps determine if files are organized by date.
        """
        structure_analysis = {
            'year_folders': [],
            'organized_by_date': False,
            'unorganized_files': [],
            'total_depth_levels': set(),
            'folder_patterns': defaultdict(int)
        }
        
        media_files = self.get_all_media_files()
        
        for file_path in media_files:
            rel_path = file_path.relative_to(self.src_root)
            parts = rel_path.parts
            
            # Track depth
            structure_analysis['total_depth_levels'].add(len(parts))
            
            # Check if organized in YYYY/MM pattern
            if len(parts) >= 2:
                first_part = parts[0]
                second_part = parts[1]
                
                if (first_part.isdigit() and len(first_part) == 4 and 
                    second_part.isdigit() and len(second_part) == 2):
                    if first_part not in structure_analysis['year_folders']:
                        structure_analysis['year_folders'].append(first_part)
                    structure_analysis['folder_patterns'][f"{first_part}/{second_part}"] += 1
                else:
                    structure_analysis['unorganized_files'].append(str(file_path))
            else:
                structure_analysis['unorganized_files'].append(str(file_path))
        
        # Determine if mostly organized by date
        total_files = len(media_files)
        organized_files = total_files - len(structure_analysis['unorganized_files'])
        structure_analysis['organized_by_date'] = (organized_files / total_files) > 0.8 if total_files > 0 else False
        structure_analysis['organization_percentage'] = (organized_files / total_files * 100) if total_files > 0 else 0
        
        return structure_analysis
    
    def quick_duplicate_scan(self) -> Dict:
        """
        Perform a quick duplicate scan based on file size and name.
        For a more thorough scan, use hash-based detection.
        """
        media_files = self.get_all_media_files()
        potential_duplicates = defaultdict(list)
        
        # Group by size and basename
        for file_path in media_files:
            try:
                size = file_path.stat().st_size
                name = file_path.name
                key = f"{size}_{name}"
                potential_duplicates[key].append(file_path)
            except Exception:
                continue
        
        # Filter to actual duplicates
        duplicates = {k: v for k, v in potential_duplicates.items() if len(v) > 1}
        
        return {
            'potential_duplicate_groups': len(duplicates),
            'total_potential_duplicates': sum(len(files) for files in duplicates.values()),
            'duplicate_details': duplicates
        }


# Convenience functions
def quick_media_scan(src_dir: str) -> Dict:
    """Quick scan of media files for conversion readiness."""
    scanner = MediaFileScanner(src_dir)
    return scanner.scan_for_conversion_readiness()

def analyze_media_organization(src_dir: str) -> Dict:
    """Analyze how media files are organized in the directory."""
    scanner = MediaFileScanner(src_dir)
    return scanner.analyze_directory_structure()
