import os
from pathlib import Path
from PIL import Image
import piexif
import pillow_heif
from collections import defaultdict

class ImageConverter:
    SUPPORTED_TYPES = ['.jpg', '.jpeg', '.png', '.heic', '.tiff']

    def __init__(self, src_root: str, dest_root: str):
        self.src_root = Path(src_root)
        self.dest_root = Path(dest_root)

    def convert_all(self):
        for src_path in self.src_root.rglob('*'):
            if src_path.is_file() and src_path.suffix.lower() in self.SUPPORTED_TYPES:
                rel_path = src_path.relative_to(self.src_root)
                dest_path = self.dest_root / rel_path.with_suffix('.jpg')
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                self.convert_to_jpeg(src_path, dest_path)

    def convert_to_jpeg(self, src_path: Path, dest_path: Path):
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

# Example usage:
# converter = ImageConverter('Organized', 'Organized_jpeg')
# converter.report_file_types_by_year()