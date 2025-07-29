import os
from pathlib import Path
from PIL import Image
import pillow_heif
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import piexif

class HeicConverter:
    """
    A dedicated class for scanning and converting HEIC files.
    Handles EXIF validation and provides detailed logging.
    """
    
    def __init__(self, src_root: str, dest_root: str):
        self.src_root = Path(src_root)
        self.dest_root = Path(dest_root)
        self.excluded_paths = ['.dtrash']
        
        # Ensure source exists
        if not self.src_root.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.src_root}")
        
        # Create destination if it doesn't exist
        self.dest_root.mkdir(parents=True, exist_ok=True)
        
        # Create reports directory
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def is_excluded_path(self, path: Path) -> bool:
        """Check if the path contains any excluded directory names."""
        return any(excluded in path.parts for excluded in self.excluded_paths)
    
    def find_heic_files(self) -> List[Path]:
        """Find all HEIC files in the source directory."""
        heic_files = []
        for file_path in self.src_root.rglob('*'):
            if (file_path.is_file() 
                and file_path.suffix.lower() == '.heic'
                and not self.is_excluded_path(file_path)):
                heic_files.append(file_path)
        return heic_files
    
    def extract_heic_metadata(self, file_path: Path) -> Tuple[Optional[datetime], Dict]:
        """
        Extract EXIF metadata from a HEIC file.
        Returns (creation_date, metadata_dict)
        """
        try:
            heif_file = pillow_heif.read_heif(str(file_path))
            metadata = heif_file.metadata or {}
            
            # Try to extract creation date from various EXIF fields
            creation_date = None
            exif_data = metadata.get('exif')
            
            if exif_data:
                try:
                    # Parse EXIF data
                    exif_dict = piexif.load(exif_data)
                    
                    # Try DateTimeOriginal first (most reliable)
                    if piexif.ExifIFD.DateTimeOriginal in exif_dict.get('Exif', {}):
                        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                        creation_date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    # Fall back to DateTime
                    elif piexif.ImageIFD.DateTime in exif_dict.get('0th', {}):
                        date_str = exif_dict['0th'][piexif.ImageIFD.DateTime].decode('utf-8')
                        creation_date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except Exception as e:
                    print(f"Error parsing EXIF data for {file_path}: {e}")
            
            return creation_date, metadata
            
        except Exception as e:
            print(f"Error reading HEIC metadata for {file_path}: {e}")
            return None, {}
    
    def scan_heic_files(self, save_report: bool = True) -> Dict:
        """
        Scan all HEIC files and create a detailed report of what can be converted.
        Returns a dictionary with conversion status for each file.
        """
        heic_files = self.find_heic_files()
        scan_results = {
            'convertible': [],
            'missing_date': [],
            'errors': []
        }
        
        print(f"Scanning {len(heic_files)} HEIC files...")
        
        for file_path in tqdm(heic_files, desc="Scanning HEIC files"):
            try:
                creation_date, metadata = self.extract_heic_metadata(file_path)
                
                file_info = {
                    'path': str(file_path),
                    'relative_path': str(file_path.relative_to(self.src_root)),
                    'creation_date': creation_date.isoformat() if creation_date else None,
                    'has_exif': bool(metadata.get('exif'))
                }
                
                if creation_date:
                    scan_results['convertible'].append(file_info)
                else:
                    scan_results['missing_date'].append(file_info)
                    
            except Exception as e:
                error_info = {
                    'path': str(file_path),
                    'error': str(e)
                }
                scan_results['errors'].append(error_info)
        
        # Print summary
        print(f"\nScan Results:")
        print(f"  Convertible files (with creation date): {len(scan_results['convertible'])}")
        print(f"  Files missing creation date: {len(scan_results['missing_date'])}")
        print(f"  Files with errors: {len(scan_results['errors'])}")
        
        if save_report:
            self._save_scan_report(scan_results)
        
        return scan_results
    
    def _save_scan_report(self, scan_results: Dict):
        """Save the scan results to detailed log files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save convertible files report
        if scan_results['convertible']:
            convertible_file = self.reports_dir / f"heic_convertible_{timestamp}.txt"
            with open(convertible_file, 'w') as f:
                f.write("HEIC Files Ready for Conversion\n")
                f.write("=" * 50 + "\n\n")
                for file_info in scan_results['convertible']:
                    f.write(f"File: {file_info['path']}\n")
                    f.write(f"Creation Date: {file_info['creation_date']}\n")
                    f.write(f"Has EXIF: {file_info['has_exif']}\n")
                    f.write("-" * 30 + "\n")
            print(f"Convertible files report saved to: {convertible_file}")
        
        # Save missing date files report
        if scan_results['missing_date']:
            missing_date_file = self.reports_dir / f"heic_missing_date_{timestamp}.txt"
            with open(missing_date_file, 'w') as f:
                f.write("HEIC Files Missing Creation Date\n")
                f.write("=" * 50 + "\n\n")
                f.write("These files cannot be converted because they lack creation date information:\n\n")
                for file_info in scan_results['missing_date']:
                    f.write(f"File: {file_info['path']}\n")
                    f.write(f"Has EXIF: {file_info['has_exif']}\n")
                    f.write("-" * 30 + "\n")
            print(f"Missing date files report saved to: {missing_date_file}")
        
        # Save errors report
        if scan_results['errors']:
            errors_file = self.reports_dir / f"heic_errors_{timestamp}.txt"
            with open(errors_file, 'w') as f:
                f.write("HEIC Files with Processing Errors\n")
                f.write("=" * 50 + "\n\n")
                for error_info in scan_results['errors']:
                    f.write(f"File: {error_info['path']}\n")
                    f.write(f"Error: {error_info['error']}\n")
                    f.write("-" * 30 + "\n")
            print(f"Errors report saved to: {errors_file}")
    
    def convert_heic_file(self, src_path: Path, dest_path: Path) -> Dict:
        """
        Convert a single HEIC file to JPEG, preserving EXIF data.
        Returns conversion result dictionary.
        """
        result = {
            'src_path': str(src_path),
            'dest_path': str(dest_path),
            'success': False,
            'creation_date': None,
            'exif_preserved': False,
            'error': None
        }
        
        try:
            # First, validate that the file has a creation date
            creation_date, metadata = self.extract_heic_metadata(src_path)
            
            if not creation_date:
                result['error'] = "No creation date found in EXIF data"
                return result
            
            result['creation_date'] = creation_date.isoformat()
            
            # Convert the file
            heif_file = pillow_heif.read_heif(str(src_path))
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try to preserve EXIF data
            exif_bytes = metadata.get('exif')
            if exif_bytes:
                try:
                    image.save(dest_path, 'JPEG', exif=exif_bytes, quality=95)
                    result['exif_preserved'] = True
                except Exception as e:
                    # If EXIF preservation fails, save without it
                    image.save(dest_path, 'JPEG', quality=95)
                    result['exif_preserved'] = False
                    print(f"Warning: Could not preserve EXIF for {src_path}: {e}")
            else:
                image.save(dest_path, 'JPEG', quality=95)
                result['exif_preserved'] = False
            
            result['success'] = True
            print(f"Converted: {src_path} -> {dest_path} (EXIF: {'preserved' if result['exif_preserved'] else 'not preserved'})")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Failed to convert {src_path}: {e}")
        
        return result
    
    def convert_all_heic(self, dry_run: bool = False) -> Dict:
        """
        Convert all HEIC files that have creation dates.
        
        Args:
            dry_run: If True, only scan and report what would be converted
        
        Returns:
            Dictionary with conversion results
        """
        # First scan to identify convertible files
        scan_results = self.scan_heic_files(save_report=True)
        convertible_files = scan_results['convertible']
        
        if not convertible_files:
            print("No HEIC files with creation dates found for conversion.")
            return {'converted': [], 'skipped': [], 'errors': []}
        
        if dry_run:
            print(f"\nDry Run: Would convert {len(convertible_files)} HEIC files:")
            for file_info in convertible_files:
                src_path = Path(file_info['path'])
                rel_path = src_path.relative_to(self.src_root)
                dest_path = self.dest_root / rel_path.with_suffix('.jpg')
                print(f"  {src_path} -> {dest_path}")
            return {'converted': [], 'skipped': convertible_files, 'errors': []}
        
        # Actual conversion
        conversion_results = {
            'converted': [],
            'skipped': [],
            'errors': []
        }
        
        print(f"\nConverting {len(convertible_files)} HEIC files...")
        
        for file_info in tqdm(convertible_files, desc="Converting HEIC files"):
            src_path = Path(file_info['path'])
            rel_path = src_path.relative_to(self.src_root)
            dest_path = self.dest_root / rel_path.with_suffix('.jpg')
            
            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert the file
            result = self.convert_heic_file(src_path, dest_path)
            
            if result['success']:
                conversion_results['converted'].append(result)
            else:
                conversion_results['errors'].append(result)
        
        # Save conversion report
        self._save_conversion_report(conversion_results)
        
        print(f"\nConversion completed:")
        print(f"  Successfully converted: {len(conversion_results['converted'])}")
        print(f"  Errors: {len(conversion_results['errors'])}")
        
        return conversion_results
    
    def _save_conversion_report(self, conversion_results: Dict):
        """Save detailed conversion results to a log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"heic_conversion_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("HEIC Conversion Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Successfully converted files
            f.write(f"Successfully Converted ({len(conversion_results['converted'])}):\n")
            f.write("-" * 30 + "\n")
            for result in conversion_results['converted']:
                f.write(f"Source: {result['src_path']}\n")
                f.write(f"Destination: {result['dest_path']}\n")
                f.write(f"Creation Date: {result['creation_date']}\n")
                f.write(f"EXIF Preserved: {result['exif_preserved']}\n")
                f.write("-" * 30 + "\n")
            
            # Error files
            if conversion_results['errors']:
                f.write(f"\nConversion Errors ({len(conversion_results['errors'])}):\n")
                f.write("-" * 30 + "\n")
                for result in conversion_results['errors']:
                    f.write(f"Source: {result['src_path']}\n")
                    f.write(f"Error: {result['error']}\n")
                    f.write("-" * 30 + "\n")
        
        print(f"Conversion report saved to: {report_file}")


# Example usage functions
def scan_heic_files_only(src_dir: str):
    """Convenience function to scan HEIC files without converting."""
    converter = HeicConverter(src_dir, "temp_dest")
    return converter.scan_heic_files()

def convert_heic_with_validation(src_dir: str, dest_dir: str, dry_run: bool = False):
    """Convenience function to convert HEIC files with full validation."""
    converter = HeicConverter(src_dir, dest_dir)
    return converter.convert_all_heic(dry_run=dry_run)
