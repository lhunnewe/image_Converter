# Image Converter

A comprehensive media file conversion tool with specialized components for different file types and conversion needs. This tool provides both simple image format conversion and advanced HEIC file processing with EXIF validation.

## Project Structure

```
image_Converter/
├── src/                          # Source code modules
│   ├── main.py                   # Main ImageConverter class
│   ├── heic_converter.py         # Specialized HEIC file handling
│   └── media_scanner.py          # Media file scanning utilities
├── scripts/                      # Ready-to-use workflow scripts
│   ├── comprehensive_analysis.py # Complete media analysis
│   ├── media_scanning.py         # File scanning and analysis
│   ├── heic_conversion.py        # HEIC file conversion
│   ├── general_conversion.py     # General image conversion
│   ├── organize_by_date.py       # File organization by date
│   ├── reconcile_heic_jpeg.py    # Conversion verification
│   ├── archive_converted_heic.py # Archive management
│   └── README.md                 # Scripts documentation
├── workflows/                    # Step-by-step workflow guides
│   ├── post_conversion_workflow.txt # Complete workflow guide
│   ├── quick_reference.txt       # Fast track reference
│   └── README.md                 # Workflow documentation
├── reports/                      # Generated log files and reports
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Features

- **Convert images to and from popular formats** (JPEG, PNG, BMP, GIF, TIFF, HEIC, etc.)
- **Batch conversion support** with progress tracking
- **Resize images during conversion** (optional)
- **Command-line interface** via workflow scripts
- **HEIC File Conversion with EXIF Validation** - Verifies creation date exists before conversion
- **Comprehensive Media File Scanning** - Analyzes all media files for conversion readiness
- **Structured Workflow Scripts** - Ready-to-use scripts for different conversion needs
- **Detailed Reporting System** - All operations generate timestamped reports
- **Safety Features** - Dry run capabilities and user confirmation required

## Quick Start

### 1. Setup Environment
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd image_Converter

# Create and activate virtual environment
python -m venv venv

# Windows activation:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Update Directory Paths
Edit the scripts in the `scripts/` folder to update your source and destination paths:
```python
src_directory = r'W:\Organized'        # Your source folder
dest_directory = r'W:\Convert to Jpeg' # Your destination folder
```

### 3. Choose Your Workflow
For complete step-by-step guidance, see the `workflows/` directory:
- **First-time users**: `workflows/post_conversion_workflow.txt` (complete guide)
- **Quick reference**: `workflows/quick_reference.txt` (command summary)

### 4. Start with Analysis
```bash
python scripts/comprehensive_analysis.py
```

### 5. Follow the Workflow
Based on the analysis, follow the complete workflow in the workflows directory.

## Key Features

### ✅ HEIC File Conversion with EXIF Validation
- Verifies creation date exists before conversion
- Only converts files with valid EXIF data
- Detailed logging of conversion attempts
- Safe conversion with EXIF preservation

### ✅ Comprehensive Media File Scanning
- Analyzes all media files for conversion readiness
- Categorizes files by type and conversion needs
- Checks directory organization patterns
- Generates detailed conversion reports

### ✅ Structured Workflow Scripts
- `comprehensive_analysis.py` - Complete media analysis
- `media_scanning.py` - Detailed scanning without conversion
- `heic_conversion.py` - HEIC-specific conversion with validation
- `general_conversion.py` - Convert other image formats
- `organize_by_date.py` - Organize files by creation date

### ✅ Detailed Reporting System
All operations generate timestamped reports in the `reports/` folder:
- Media scan summaries
- HEIC conversion readiness reports
- Conversion success/failure logs
- File organization results

### ✅ Safety Features
- Dry run capabilities show what would happen before making changes
- User confirmation required before actual conversion
- EXIF validation prevents conversion of problematic files
- Comprehensive error logging and reporting

## Workflow Scripts

### Recommended Usage Order

1. **Comprehensive Analysis** (`comprehensive_analysis.py`)
   - Analyzes your entire media collection
   - Provides conversion recommendations
   - Generates detailed reports

2. **File Organization** (`organize_by_date.py`) - *Optional*
   - Organizes files into YYYY/MM folders
   - Uses EXIF creation dates
   - Only needed if files aren't already organized

3. **HEIC Conversion** (`heic_conversion.py`)
   - Converts HEIC files with EXIF validation
   - Only processes files with creation dates
   - Preserves EXIF data during conversion

4. **General Conversion** (`general_conversion.py`)
   - Converts remaining image formats (PNG, TIFF, etc.)
   - Offers bulk or selective conversion
   - Preserves EXIF data when possible

5. **Verification Scan** (`media_scanning.py`)
   - Re-scans to verify conversion results
   - Updates analysis after conversion

## Report Files Generated

### HEIC Reports
- `heic_convertible_YYYYMMDD_HHMMSS.txt` - Files ready for conversion
- `heic_missing_date_YYYYMMDD_HHMMSS.txt` - Files without creation dates
- `heic_errors_YYYYMMDD_HHMMSS.txt` - Files with processing errors
- `heic_conversion_report_YYYYMMDD_HHMMSS.txt` - Detailed conversion results

### Media Scan Reports
- `media_scan_summary_YYYYMMDD_HHMMSS.txt` - Overall scan summary
- `files_needing_conversion_YYYYMMDD_HHMMSS.txt` - Non-JPEG files to convert
- `heic_files_found_YYYYMMDD_HHMMSS.txt` - HEIC files requiring special processing

### Post-Conversion Reports
- `heic_jpeg_reconciliation_YYYYMMDD_HHMMSS.txt` - Conversion verification
- `heic_archive_simple_YYYYMMDD_HHMMSS.txt` - Archive operation results

## Complete Workflows

The `workflows/` directory contains comprehensive step-by-step guides:

### 📋 Complete Workflow Guide (`workflows/post_conversion_workflow.txt`)
Detailed step-by-step workflow covering:
- Initial analysis and preparation
- HEIC conversion process
- Post-conversion verification and management
- Archive management
- Troubleshooting and recovery procedures

### ⚡ Quick Reference (`workflows/quick_reference.txt`)
Fast-track reference for experienced users:
- 6-step core workflow
- Command quick reference
- Common issues and fixes
- Emergency recovery procedures

**Recommended**: Start with the complete workflow guide for your first conversion project.

## Advanced Usage

### Using the Source Modules Directly

```python
# Import from src directory
from src.heic_converter import HeicConverter
from src.media_scanner import MediaFileScanner
from src.main import ImageConverter

# HEIC-only conversion
heic_converter = HeicConverter('source_folder', 'destination_folder')
scan_results = heic_converter.scan_heic_files()
conversion_results = heic_converter.convert_all_heic(dry_run=False)

# Media scanning
scanner = MediaFileScanner('source_folder')
scan_results = scanner.scan_for_conversion_readiness()

# General conversion
converter = ImageConverter('source_folder', 'destination_folder')
converter.convert_all_with_progress()
```

## Migration from Previous Version

The new structure maintains backward compatibility:
- All existing `ImageConverter` methods still work
- New specialized classes provide enhanced functionality
- Reports are now organized in dedicated folder
- Scripts provide user-friendly interfaces

## Installation Requirements

```bash
pip install pillow pillow-heif piexif tqdm ffmpeg-python hachoir
```

## Configuration

1. **Update Directory Paths**: Edit paths in script files
2. **Verify Dependencies**: Ensure all packages are installed
3. **Test with Dry Run**: Always test with dry run before actual conversion
4. **Review Reports**: Check generated reports before proceeding

## Troubleshooting

- **Import Errors**: Ensure scripts are run from project root directory
- **Path Errors**: Verify source and destination paths exist
- **Permission Errors**: Check file/folder permissions
- **HEIC Issues**: Ensure pillow-heif is properly installed

## Support

- Check the `scripts/README.md` for detailed script documentation
- Review generated reports for operation details
- Use dry run mode to preview operations before execution
