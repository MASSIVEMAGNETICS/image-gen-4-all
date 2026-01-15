# Example Usage

This directory contains examples of using the export parser.

## Basic Usage Example

```python
from parse_export import ExportParser

# Create parser instance
parser = ExportParser('path/to/export.zip', output_dir='./output')

# Parse and extract files
results = parser.parse()

# Print results
parser.print_results()

# Save manifest
parser.save_manifest('manifest.json')
```

## Command Line Examples

### Parse a ZIP file
```bash
python parse_export.py export.zip
```

### Parse with custom output directory
```bash
python parse_export.py export.tar.gz -o /custom/path
```

### List files without extracting
```bash
python parse_export.py export.zip --no-extract
```

### Generate manifest
```bash
python parse_export.py export.zip -m manifest.json
```

## Expected Export Structure

The parser looks for files in the `instruct/dir/` path within the export. Example structure:

```
export.zip
├── instruct/
│   └── dir/
│       ├── instruction1.txt
│       ├── instruction2.json
│       └── config.yaml
├── other_files/
│   └── data.txt
└── readme.txt
```

Only files under `instruct/dir/` will be extracted and processed.
