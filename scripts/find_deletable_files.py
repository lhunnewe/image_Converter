import sys
from pathlib import Path

# Add parent directory to Python path to import main.py
sys.path.append(str(Path(__file__).parent.parent))

from main import ImageConverter
import argparse

def main():
    parser = argparse.ArgumentParser(description='Find non-media files that can potentially be deleted')
    parser.add_argument('--save', action='store_true', help='Save results to deletable_files_report.txt')
    args = parser.parse_args()

    # Create converter instance
    converter = ImageConverter('Organized', 'Organized_jpeg')
    
    # Find non-media files
    deletable_files = converter.find_non_media_files()
    
    # Save to file if requested
    if args.save and deletable_files:
        report_path = Path(__file__).parent.parent / 'deletable_files_report.txt'
        with open(report_path, 'w') as f:
            f.write("Potentially deletable non-media files:\n\n")
            for ext, files in sorted(deletable_files.items()):
                f.write(f"\n{ext}: {len(files)} files\n")
                for file in files:
                    f.write(f"  {file}\n")
        print(f"\nFull report saved to: {report_path}")

if __name__ == '__main__':
    main()