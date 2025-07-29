# Scripts Directory

This directory contains ready-to-use scripts for different media file operations. Each script is designed for a specific workflow and can be run independently.

## Available Scripts

### 1. `comprehensive_analysis.py`
**Purpose**: Complete analysis of your media collection
**What it does**:
- Scans all media files for conversion readiness
- Analyzes HEIC files for EXIF validation
- Checks directory organization
- Generates conversion recommendations
- Creates detailed reports

**When to use**: Run this first to understand your media collection before any conversion.

**Usage**:
```bash
python scripts/comprehensive_analysis.py
```

### 2. `media_scanning.py`
**Purpose**: Detailed scanning and analysis without conversion
**What it does**:
- Scans all media files by type
- Analyzes directory organization patterns
- Performs quick duplicate detection
- Generates detailed reports

**When to use**: When you want detailed analysis without any conversion.

**Usage**:
```bash
python scripts/media_scanning.py
```

### 3. `heic_conversion.py`
**Purpose**: Specialized HEIC file conversion with EXIF validation
**What it does**:
- Scans HEIC files for EXIF creation dates
- Only converts files with valid creation dates
- Preserves EXIF data during conversion
- Logs files that cannot be converted

**When to use**: After media scanning shows you have HEIC files to convert.

**Usage**:
```bash
python scripts/heic_conversion.py
```

### 4. `general_conversion.py`
**Purpose**: Convert non-HEIC image formats to JPEG
**What it does**:
- Converts PNG, TIFF, and other image formats to JPEG
- Offers option to convert all files or specific month
- Shows dry run before actual conversion
- Preserves EXIF data when possible

**When to use**: After HEIC conversion, for remaining image formats.

**Usage**:
```bash
python scripts/general_conversion.py
```

### 5. `organize_by_date.py`
**Purpose**: Organize media files into date-based folders
**What it does**:
- Moves files into YYYY/MM folder structure
- Uses EXIF creation dates when available
- Skips files already organized
- Reports files that cannot be dated

**When to use**: Before conversion if your files aren't organized by date.

**Usage**:
```bash
python scripts/organize_by_date.py
```

### 6. `reconcile_heic_jpeg.py`
**Purpose**: Reconcile HEIC files with their converted JPEG counterparts
**What it does**:
- Compares HEIC files with corresponding JPEG files
- Shows which files have been successfully converted
- Identifies unconverted HEIC files
- Finds orphaned JPEG files without HEIC originals
- Calculates storage savings and conversion statistics

**When to use**: After HEIC conversion to verify results and track progress.

**Usage**:
```bash
python scripts/reconcile_heic_jpeg.py
```

### 7. `archive_converted_heic.py`
**Purpose**: Archive HEIC files that have been converted to JPEG
**What it does**:
- Finds HEIC files with corresponding JPEG files
- Moves converted HEIC files to an archive directory
- Maintains folder structure in archive
- Generates archive operation reports

**When to use**: After successful HEIC conversion to clean up original files.

**Usage**:
```bash
python scripts/archive_converted_heic.py
```

## Recommended Workflow

### Standard Conversion Workflow:
1. **Start with Analysis**:
   ```bash
   python scripts/comprehensive_analysis.py
   ```

2. **Organize Files (if needed)**:
   ```bash
   python scripts/organize_by_date.py
   ```

3. **Convert HEIC Files**:
   ```bash
   python scripts/heic_conversion.py
   ```

4. **Verify HEIC Conversion**:
   ```bash
   python scripts/reconcile_heic_jpeg.py
   ```

5. **Archive Converted HEIC Files**:
   ```bash
   python scripts/archive_converted_heic.py
   ```

6. **Convert Other Images**:
   ```bash
   python scripts/general_conversion.py
   ```

7. **Final Verification Scan**:
   ```bash
   python scripts/media_scanning.py
   ```

### Post-Conversion Management:
- Use `reconcile_heic_jpeg.py` anytime to check conversion status
- Use `archive_converted_heic.py` to clean up original HEIC files
- Re-run `comprehensive_analysis.py` after major changes

## Configuration

Before running any script, update the directory paths at the top of each script:

```python
src_directory = r'W:\Organized'        # Your source folder
dest_directory = r'W:\Convert to Jpeg' # Your destination folder
```

## Reports

All scripts generate timestamped reports in the `reports/` folder:

### Conversion Reports:
- `media_scan_summary_YYYYMMDD_HHMMSS.txt` - Overall media analysis
- `heic_convertible_YYYYMMDD_HHMMSS.txt` - HEIC files ready for conversion
- `heic_missing_date_YYYYMMDD_HHMMSS.txt` - HEIC files without creation dates
- `heic_conversion_report_YYYYMMDD_HHMMSS.txt` - Detailed conversion results
- `files_needing_conversion_YYYYMMDD_HHMMSS.txt` - Non-JPEG files to convert

### Post-Conversion Reports:
- `heic_jpeg_reconciliation_YYYYMMDD_HHMMSS.txt` - Conversion verification report
- `heic_archive_simple_YYYYMMDD_HHMMSS.txt` - Archive operation results

### Configuration Files:
- `conversion_tracking.json` - Tracks converted files and archive status

## Safety Features

- **Dry Run Support**: Most scripts show what would happen before making changes
- **User Confirmation**: Scripts ask for confirmation before making changes
- **EXIF Validation**: HEIC files are only converted if they have creation dates
- **Error Logging**: All errors are logged for review
- **Detailed Reporting**: Comprehensive logs of all operations

## Error Handling

If you encounter import errors, ensure:
1. You're running scripts from the project root directory
2. All required packages are installed (`pip install -r requirements.txt`)
3. The `src/` directory contains all the Python modules

## Getting Help

Each script includes help text and will guide you through the process. Most scripts also offer multiple options for different use cases.
