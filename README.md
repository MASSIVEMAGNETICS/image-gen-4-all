# image-gen-4-all
free image gen

## Documentation

- [HART-Morphosis docs](docs/index.md)
- [Enterprise-grade review & roadmap](docs/enterprise_roadmap.md)

## Export Parser

This repository includes a tool to parse export files and extract files from `instruct/dir/` directories.

### Usage

Parse an export file (ZIP, TAR, or TAR.GZ) to extract files from `instruct/dir/` paths:

```bash
python parse_export.py <export_file> [options]
```

### Options

- `-o, --output`: Output directory for extracted files (default: `./parsed_output`)
- `-m, --manifest`: Path to save a JSON manifest of parsed files
- `--no-extract`: List files without extracting them

### Examples

```bash
# Parse a ZIP file and extract to default location
python parse_export.py export.zip

# Parse a TAR.GZ file and extract to custom directory
python parse_export.py export.tar.gz -o /path/to/output

# Parse and save a manifest file without extracting
python parse_export.py export.zip --no-extract -m manifest.json
```

### Requirements

- Python 3.6 or higher
- No external dependencies (uses Python standard library)
