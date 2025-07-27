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

class ImageConverter:
    SUPPORTED_TYPES = ['.jpg', '.jpeg', '.png', '.heic', '.tiff']

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

    # --- Directory and File Listing ---
    def validate_directories(self):
        """Ensure source exists and destination is ready."""
        if not self.src_root.exists():
            raise FileNotFoundError(f"Source directory {self.src_root} does not exist.")
        self.dest_root.mkdir(parents=True, exist_ok=True)

    def list_supported_files(self):
        """Return a list of all supported files in the source directory."""
        return [p for p in self.src_root.rglob('*') if p.is_file() and p.suffix.lower() in self.SUPPORTED_TYPES]

    # --- Reporting ---
    def report_file_types_by_year(self):
        """
        Prints a report of the count of all file types by year based on folder structure.
        Assumes structure: root/YYYY/mm/images
        """
        counts = defaultdict(lambda: defaultdict(int))
        for file_path in self.src_root.rglob('*'):
            if file_path.is_file():
                parts = file_path.relative_to(self.src_root).parts
                if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                    year = parts[0]
                else:
                    year = 'Unknown'
                ext = file_path.suffix.lower()
                counts[year][ext] += 1

        print("File type counts by year:")
        for year in sorted(counts):
            print(f"Year: {year}")
            for ext, count in counts[year].items():
                print(f"  {ext}: {count}")
            print()

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
        with open("exif_conversion_report.txt", "w") as f:
            for line in exif_log:
                f.write(line + "\n")

    def convert_all(self):
        """Convert all supported files without progress bar or EXIF logging."""
        for src_path in self.src_root.rglob('*'):
            if src_path.is_file() and src_path.suffix.lower() in self.SUPPORTED_TYPES:
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
        with open(log_file, 'w') as f:
            for line in results:
                f.write(line + '\n')

    def move_images_to_date_folders(self):
        """
        Move images not in YYYY/mm folders into folders by their taken date (EXIF DateTimeOriginal).
        """
        for file_path in self.src_root.rglob('*'):
            if not file_path.is_file() or file_path.suffix.lower() not in self.SUPPORTED_TYPES:
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

# Example usage:
converter = ImageConverter('Organized', 'Organized_jpeg')
converter.report_file_types_by_year()