import os
from pathlib import Path
from PIL import Image
import piexif
import pillow_heif
from collections import defaultdict
from tqdm import tqdm  # For progress bar
import hashlib
import shutil
from datetime import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import ffmpeg
from typing import Optional

# Import our new specialized classes
from heic_converter import HeicConverter
from media_scanner import MediaFileScanner

class ImageConverter:
    SUPPORTED_TYPES = [
        '.jpg', '.jpeg', '.png', '.heic', '.tiff',  # Images
        '.mov', '.mp4', '.mts',  # Videos
        '.gif'  # Animated images
    ]
    EXCLUDED_PATHS = ['.dtrash']  # Add this line

    def __init__(self, src_root: str, dest_root: str):
        try:
            self.src_root = Path(r'W:\Organized')
            if not self.src_root.exists():
                raise FileNotFoundError(f"Source folder does not exist: {self.src_root}")
            print(f"Source folder is set to: {self.src_root}")
        except Exception as e:
            print(f"Error setting source folder: {e}")
            raise
        try:
            self.dest_root = Path(r'W:\Convert to Jpeg')
            if not self.dest_root.exists():
                print(f"Destination folder does not exist: {self.dest_root}")
            else:
                print(f"Destination folder is set to: {self.dest_root}")
        except Exception as e:
            print(f"Error setting destination folder: {e}")
            raise
        
        # Create reports directory
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    # --- Directory and File Listing ---
    def validate_directories(self):
        """Ensure source exists and destination is ready."""
        if not self.src_root.exists():
            raise FileNotFoundError(f"Source directory {self.src_root} does not exist.")
        self.dest_root.mkdir(parents=True, exist_ok=True)

    def list_supported_files(self):
        """Return a list of all supported files in the source directory."""
        return [p for p in self.src_root.rglob('*') 
                if p.is_file() 
                and p.suffix.lower() in self.SUPPORTED_TYPES
                and not self.is_excluded_path(p)]

    # --- Reporting ---
    def report_file_types_by_year(self, show_files=10, save_report=True):
        """
        Prints a report of the count of all file types by year.
        Args:
            show_files (int): Number of unknown files to show in console output
            save_report (bool): Whether to save full report to a file
        """
        counts = defaultdict(lambda: defaultdict(int))
        unknown_files = []
        
        for file_path in self.src_root.rglob('*'):
            if file_path.is_file() and not self.is_excluded_path(file_path):
                # Try folder structure first
                parts = file_path.relative_to(self.src_root).parts
                year = None
                
                if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                    year = parts[0]
                else:
                    # Try EXIF data
                    try:
                        if file_path.suffix.lower() in self.SUPPORTED_TYPES:
                            img = Image.open(file_path)
                            exif = img._getexif()
                            if exif:
                                date_str = exif.get(36867) or exif.get(306)
                                if date_str:
                                    year = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").strftime("%Y")
                    except:
                        pass
                        
                if not year:
                    year = 'Unknown'
                    unknown_files.append(str(file_path))
                    
                ext = file_path.suffix.lower()
                counts[year][ext] += 1

        print("\nFile type counts by year:")
        for year in sorted(counts):
            print(f"\nYear: {year}")
            for ext, count in counts[year].items():
                print(f"  {ext}: {count}")
                
        if unknown_files:
            # Count unknown files by type
            unknown_by_type = defaultdict(int)
            for f in unknown_files:
                ext = Path(f).suffix.lower()
                unknown_by_type[ext] += 1
                
            print("\nUnknown files by type:")
            for ext, count in sorted(unknown_by_type.items()):
                print(f"  {ext}: {count}")
                
            print(f"\nShowing first {show_files} of {len(unknown_files)} unknown files:")
            for f in unknown_files[:show_files]:
                print(f"  {f}")
            if len(unknown_files) > show_files:
                print(f"  ... and {len(unknown_files) - show_files} more files")
                
            if save_report:
                report_file = self.reports_dir / "unknown_files_report.txt"
                with open(report_file, 'w') as f:
                    f.write("Files with unknown years:\n")
                    for file in unknown_files:
                        f.write(f"{file}\n")
                print(f"\nFull list saved to: {report_file}")

    def report_duplicates(self):
        """Detect and report duplicate images by hash."""
        seen = {}
        duplicates = defaultdict(list)
        for file_path in self.list_supported_files():
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash in seen:
                    duplicates[file_hash].append(file_path)
                else:
                    seen[file_hash] = file_path
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")
        if duplicates:
            print("Duplicate files found:")
            for file_hash, files in duplicates.items():
                print(f"Hash: {file_hash}")
                print(f"  Original: {seen[file_hash]}")
                for dup in files:
                    print(f"  Duplicate: {dup}")
        else:
            print("No duplicate files found.")

    # --- Conversion Helpers ---
    def convert_single_file(self, src_path: Path, dest_path: Path, exif_log=None):
        """Convert a single file to JPEG and log EXIF preservation."""
        try:
            img = Image.open(src_path)
            exif_bytes = img.info.get('exif', None)
            exif_status = "no_exif"
            if exif_bytes is None and src_path.suffix.lower() == '.heic':
                heif_file = pillow_heif.read_heif(str(src_path))
                exif_bytes = heif_file.metadata.get('exif', None)
            img = img.convert('RGB')
            if exif_bytes:
                try:
                    img.save(dest_path, 'JPEG', exif=exif_bytes, quality=95)
                    exif_status = "preserved"
                except Exception as e:
                    img.save(dest_path, 'JPEG', quality=95)
                    exif_status = f"failed_to_save_exif: {e}"
            else:
                img.save(dest_path, 'JPEG', quality=95)
                exif_status = "no_exif"
            print(f"Converted: {src_path} -> {dest_path} (EXIF: {exif_status})")
            if exif_log is not None:
                exif_log.append(f"{src_path} -> {dest_path} | EXIF: {exif_status}")
        except Exception as e:
            print(f"Failed to convert {src_path}: {e}")
            if exif_log is not None:
                exif_log.append(f"{src_path} -> {dest_path} | FAILED: {e}")

    def convert_to_jpeg(self, src_path: Path, dest_path: Path):
        """Convert a single file to JPEG (without EXIF logging)."""
        try:
            img = Image.open(src_path)
            exif_bytes = img.info.get('exif', None)
            if exif_bytes is None and src_path.suffix.lower() == '.heic':
                heif_file = pillow_heif.read_heif(str(src_path))
                exif_bytes = heif_file.metadata.get('exif', None)
            img = img.convert('RGB')
            if exif_bytes:
                img.save(dest_path, 'JPEG', exif=exif_bytes, quality=95)
            else:
                img.save(dest_path, 'JPEG', quality=95)
            print(f"Converted: {src_path} -> {dest_path}")
        except Exception as e:
            print(f"Failed to convert {src_path}: {e}")

    # --- Conversion Processes ---
    def dry_run(self):
        """Show what would be converted without actually converting."""
        files = self.list_supported_files()
        print("Dry run: The following files would be converted:")
        for src_path in files:
            rel_path = src_path.relative_to(self.src_root)
            dest_path = self.dest_root / rel_path.with_suffix('.jpg')
            print(f"{src_path} -> {dest_path}")

    def convert_all_with_progress(self):
        """Convert all supported files with a progress bar and log EXIF results."""
        files = self.list_supported_files()
        exif_log = []
        for src_path in tqdm(files, desc="Converting images"):
            rel_path = src_path.relative_to(self.src_root)
            dest_path = self.dest_root / rel_path.with_suffix('.jpg')
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            self.convert_single_file(src_path, dest_path, exif_log=exif_log)
        # After conversion, write the log:
        report_file = self.reports_dir / "exif_conversion_report.txt"
        with open(report_file, "w") as f:
            for line in exif_log:
                f.write(line + "\n")

    def convert_all(self):
        """Convert all supported files without progress bar or EXIF logging."""
        for src_path in self.src_root.rglob('*'):
            if (src_path.is_file() 
                and src_path.suffix.lower() in self.SUPPORTED_TYPES
                and not self.is_excluded_path(src_path)):
                rel_path = src_path.relative_to(self.src_root)
                dest_path = self.dest_root / rel_path.with_suffix('.jpg')
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self.convert_to_jpeg(src_path, dest_path)

    def convert_specific_month(self, year: str, month: str):
        """
        Converts images only in the specified year and month (YYYY and mm).
        """
        target_folder = self.src_root / year / month
        if not target_folder.exists():
            print(f"No folder found for {year}/{month}")
            return

        for src_path in target_folder.rglob('*'):
            if src_path.is_file() and src_path.suffix.lower() in self.SUPPORTED_TYPES:
                rel_path = src_path.relative_to(self.src_root)
                dest_path = self.dest_root / rel_path.with_suffix('.jpg')
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self.convert_to_jpeg(src_path, dest_path)

    def process_single_file(self, file_path: str):
        """Convert a single file by absolute or relative path."""
        src_path = Path(file_path)
        if not src_path.exists() or not src_path.is_file():
            print(f"File not found: {file_path}")
            return
        if src_path.suffix.lower() not in self.SUPPORTED_TYPES:
            print(f"Unsupported file type: {src_path.suffix}")
            return
        rel_path = src_path.relative_to(self.src_root) if self.src_root in src_path.parents else src_path.name
        dest_path = self.dest_root / Path(rel_path).with_suffix('.jpg')
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        self.convert_single_file(src_path, dest_path)

    def process_year_month(self, year: str, month: str):
        """Convert all images in a specific year/month folder."""
        self.convert_specific_month(year, month)

    # --- Logging ---
    def log_conversion_results(self, log_file, results):
        """Write conversion results to a log file."""
        report_path = self.reports_dir / log_file
        with open(report_path, 'w') as f:
            for line in results:
                f.write(line + '\n')

    def move_images_to_date_folders(self):
        """
        Move images not in YYYY/mm folders into folders by their taken date (EXIF DateTimeOriginal).
        """
        for file_path in self.src_root.rglob('*'):
            if (not file_path.is_file() 
                or file_path.suffix.lower() not in self.SUPPORTED_TYPES
                or self.is_excluded_path(file_path)):
                continue
            # Check if already in YYYY/mm
            parts = file_path.relative_to(self.src_root).parts
            if len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 4 and parts[1].isdigit() and len(parts[1]) == 2:
                continue  # Already in correct folder

            # Try to get date taken
            try:
                img = Image.open(file_path)
                exif = img._getexif()
                date_str = None
                if exif:
                    date_str = exif.get(36867) or exif.get(306)  # 36867: DateTimeOriginal, 306: DateTime
                if not date_str:
                    print(f"Skipping (no date): {file_path}")
                    continue
                date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                year = str(date_obj.year)
                month = f"{date_obj.month:02d}"
                target_folder = self.src_root / year / month
                target_folder.mkdir(parents=True, exist_ok=True)
                target_path = target_folder / file_path.name
                if target_path.exists():
                    print(f"Target exists, skipping: {target_path}")
                    continue
                shutil.move(str(file_path), str(target_path))
                print(f"Moved: {file_path} -> {target_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    def is_excluded_path(self, path: Path) -> bool:
        """Check if the path contains any excluded directory names."""
        return any(excluded in path.parts for excluded in self.EXCLUDED_PATHS)

    def get_file_date(self, file_path: Path) -> Optional[datetime]:
        """Get creation date from file metadata."""
        ext = file_path.suffix.lower()
        
        # Handle images
        if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.gif']:
            try:
                img = Image.open(file_path)
                exif = img._getexif()
                if exif:
                    date_str = exif.get(36867) or exif.get(306)  # 36867: DateTimeOriginal, 306: DateTime
                    if date_str:
                        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                print(f"Error reading image EXIF: {e}")
        
        # Handle HEIC
        elif ext == '.heic':
            try:
                heif_file = pillow_heif.read_heif(str(file_path))
                exif = heif_file.metadata.get('exif')
                if exif:
                    return datetime.strptime(exif.get('DateTimeOriginal'), "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                print(f"Error reading HEIC metadata: {e}")
        
        # Handle video files
        elif ext in ['.mov', '.mp4', '.mts']:
            try:
                # Try ffmpeg first
                probe = ffmpeg.probe(str(file_path))
                if 'format' in probe and 'tags' in probe['format']:
                    tags = probe['format']['tags']
                    if 'creation_time' in tags:
                        return datetime.strptime(tags['creation_time'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
            except Exception as e:
                print(f"Error reading video metadata with ffmpeg: {e}")
                
                # Fallback to hachoir
                try:
                    parser = createParser(str(file_path))
                    if parser:
                        metadata = extractMetadata(parser)
                        if metadata and metadata.has('creation_date'):
                            return metadata.get('creation_date')
                except Exception as e:
                    print(f"Error reading video metadata with hachoir: {e}")
    
        # If all methods fail, use file modification time
        return datetime.fromtimestamp(file_path.stat().st_mtime)

    def find_non_media_files(self) -> dict:
        """
        Find files that are not images or videos and can likely be deleted.
        Returns a dictionary of file extensions and their counts.
        """
        KNOWN_MEDIA_TYPES = {
            # Images
            '.jpg', '.jpeg', '.png', '.heic', '.tiff', '.gif', '.raw', '.arw', '.cr2', '.nef',
            # Videos
            '.mov', '.mp4', '.mts', '.avi', '.wmv', '.m4v', '.3gp',
            # Common sidecar files to keep
            '.thm', '.xmp'
        }
        
        deletable_files = defaultdict(list)
        
        for file_path in self.src_root.rglob('*'):
            if not file_path.is_file() or self.is_excluded_path(file_path):
                continue
                
            ext = file_path.suffix.lower()
            if ext not in KNOWN_MEDIA_TYPES:
                deletable_files[ext].append(str(file_path))
        
        # Print report
        if deletable_files:
            print("\nPotentially deletable non-media files found:")
            for ext, files in sorted(deletable_files.items()):
                print(f"\n{ext}: {len(files)} files")
                # Show first 5 examples
                for f in files[:5]:
                    print(f"  {f}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more {ext} files")
        else:
            print("No non-media files found")
        
        return deletable_files

    # --- New Methods Using Specialized Classes ---
    
    def scan_all_media_files(self) -> dict:
        """
        Use MediaFileScanner to analyze all media files for conversion readiness.
        This provides a comprehensive overview before any conversion.
        """
        print("Scanning all media files for conversion readiness...")
        scanner = MediaFileScanner(str(self.src_root))
        return scanner.scan_for_conversion_readiness()
    
    def scan_heic_files_detailed(self) -> dict:
        """
        Use HeicConverter to perform detailed HEIC file analysis.
        This checks EXIF data and creation dates.
        """
        print("Performing detailed HEIC file analysis...")
        heic_converter = HeicConverter(str(self.src_root), str(self.dest_root))
        return heic_converter.scan_heic_files()
    
    def convert_heic_files_only(self, dry_run: bool = False) -> dict:
        """
        Convert only HEIC files using the specialized HeicConverter.
        
        Args:
            dry_run: If True, only shows what would be converted
        """
        print("Converting HEIC files with EXIF validation...")
        heic_converter = HeicConverter(str(self.src_root), str(self.dest_root))
        return heic_converter.convert_all_heic(dry_run=dry_run)
    
    def analyze_directory_organization(self) -> dict:
        """
        Analyze how files are organized in the source directory.
        """
        print("Analyzing directory organization...")
        scanner = MediaFileScanner(str(self.src_root))
        return scanner.analyze_directory_structure()
    
    def comprehensive_scan_and_convert_plan(self):
        """
        Perform a comprehensive scan and create a detailed conversion plan.
        This method ties together all the scanning capabilities.
        """
        print("=" * 70)
        print("COMPREHENSIVE MEDIA ANALYSIS AND CONVERSION PLANNING")
        print("=" * 70)
        
        # 1. Overall media file scan
        print("\n1. Scanning all media files...")
        media_scan = self.scan_all_media_files()
        
        # 2. Directory organization analysis
        print("\n2. Analyzing directory organization...")
        org_analysis = self.analyze_directory_organization()
        print(f"Directory organization: {org_analysis['organization_percentage']:.1f}% organized by date")
        
        # 3. Detailed HEIC analysis if HEIC files found
        if media_scan['summary']['heic_count'] > 0:
            print(f"\n3. Detailed HEIC analysis ({media_scan['summary']['heic_count']} files found)...")
            heic_scan = self.scan_heic_files_detailed()
        else:
            print("\n3. No HEIC files found, skipping detailed HEIC analysis.")
            heic_scan = None
        
        # 4. Generate recommendations
        print("\n4. Generating conversion recommendations...")
        recommendations = self._generate_conversion_recommendations(media_scan, org_analysis, heic_scan)
        
        return {
            'media_scan': media_scan,
            'organization_analysis': org_analysis,
            'heic_scan': heic_scan,
            'recommendations': recommendations
        }
    
    def _generate_conversion_recommendations(self, media_scan, org_analysis, heic_scan):
        """Generate conversion recommendations based on scan results."""
        recommendations = []
        
        # Recommendation for images needing conversion
        needs_conversion = media_scan['summary']['needs_conversion_count']
        if needs_conversion > 0:
            recommendations.append(f"Convert {needs_conversion} non-JPEG images to JPEG format")
        
        # Recommendation for HEIC files
        heic_count = media_scan['summary']['heic_count']
        if heic_count > 0:
            if heic_scan:
                convertible_heic = len(heic_scan['convertible'])
                missing_date_heic = len(heic_scan['missing_date'])
                if convertible_heic > 0:
                    recommendations.append(f"Convert {convertible_heic} HEIC files (with creation dates) using specialized HEIC converter")
                if missing_date_heic > 0:
                    recommendations.append(f"Review {missing_date_heic} HEIC files missing creation dates - may need manual date assignment")
            else:
                recommendations.append(f"Perform detailed HEIC analysis on {heic_count} HEIC files before conversion")
        
        # Recommendation for organization
        if not org_analysis['organized_by_date'] and org_analysis['organization_percentage'] < 50:
            recommendations.append("Consider organizing files by date (YYYY/MM) before conversion for better management")
        
        # Recommendation for file management
        unorganized_count = len(org_analysis['unorganized_files'])
        if unorganized_count > 0:
            recommendations.append(f"Organize {unorganized_count} files that are not in date-based folders")
        
        # Print recommendations
        print("\nRECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        return recommendations
