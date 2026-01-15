#!/usr/bin/env python3
"""
Export Parser for instruct/dir/ files

This script parses export files (zip, tar.gz, etc.) and extracts files
from the instruct/dir/ directory structure.
"""

import os
import sys
import argparse
import zipfile
import tarfile
import json
from pathlib import Path
from typing import List, Dict, Any


class ExportParser:
    """Parser for export files containing instruct/dir/ files."""
    
    def __init__(self, export_path: str, output_dir: str = None):
        """
        Initialize the export parser.
        
        Args:
            export_path: Path to the export file (zip, tar.gz, etc.)
            output_dir: Directory to extract instruct/dir/ files to
        """
        self.export_path = export_path
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'parsed_output')
        self.instruct_files = []
        
    def is_instruct_dir_file(self, file_path: str) -> bool:
        """
        Check if a file is in the instruct/dir/ directory.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the file is in instruct/dir/, False otherwise
        """
        normalized_path = file_path.replace('\\', '/')
        return 'instruct/dir/' in normalized_path
    
    def parse_zip(self) -> List[Dict[str, Any]]:
        """
        Parse a ZIP export file.
        
        Returns:
            List of dictionaries containing file information
        """
        results = []
        
        try:
            with zipfile.ZipFile(self.export_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if self.is_instruct_dir_file(file_info.filename):
                        file_data = {
                            'filename': file_info.filename,
                            'size': file_info.file_size,
                            'compressed_size': file_info.compress_size,
                            'date_time': file_info.date_time
                        }
                        results.append(file_data)
                        
                        # Extract the file
                        if self.output_dir is not None:
                            zip_ref.extract(file_info.filename, self.output_dir)
                            
        except zipfile.BadZipFile:
            print(f"Error: {self.export_path} is not a valid ZIP file")
            sys.exit(1)
            
        return results
    
    def parse_tar(self) -> List[Dict[str, Any]]:
        """
        Parse a TAR/TAR.GZ export file.
        
        Returns:
            List of dictionaries containing file information
        """
        results = []
        
        try:
            with tarfile.open(self.export_path, 'r:*') as tar_ref:
                for member in tar_ref.getmembers():
                    if member.isfile() and self.is_instruct_dir_file(member.name):
                        file_data = {
                            'filename': member.name,
                            'size': member.size,
                            'mode': oct(member.mode),
                            'mtime': member.mtime
                        }
                        results.append(file_data)
                        
                        # Extract the file
                        if self.output_dir is not None:
                            tar_ref.extract(member, self.output_dir)
                            
        except tarfile.TarError as e:
            print(f"Error: {self.export_path} is not a valid TAR file: {e}")
            sys.exit(1)
            
        return results
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the export file and extract instruct/dir/ files.
        
        Returns:
            List of dictionaries containing file information
        """
        if not os.path.exists(self.export_path):
            print(f"Error: Export file '{self.export_path}' not found")
            sys.exit(1)
            
        # Create output directory if needed
        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)
            
        # Determine file type and parse accordingly
        if zipfile.is_zipfile(self.export_path):
            print(f"Parsing ZIP file: {self.export_path}")
            results = self.parse_zip()
        elif tarfile.is_tarfile(self.export_path):
            print(f"Parsing TAR file: {self.export_path}")
            results = self.parse_tar()
        else:
            print(f"Error: Unsupported file format for {self.export_path}")
            print("Supported formats: ZIP, TAR, TAR.GZ")
            sys.exit(1)
            
        self.instruct_files = results
        return results
    
    def print_results(self):
        """Print parsed results in a readable format."""
        if not self.instruct_files:
            print("\nNo files found in instruct/dir/ directory")
            return
            
        print(f"\nFound {len(self.instruct_files)} file(s) in instruct/dir/:")
        print("-" * 80)
        
        for file_data in self.instruct_files:
            print(f"\nFile: {file_data['filename']}")
            print(f"  Size: {file_data.get('size', 'N/A')} bytes")
            if 'compressed_size' in file_data:
                print(f"  Compressed Size: {file_data['compressed_size']} bytes")
            if 'date_time' in file_data:
                dt = file_data['date_time']
                print(f"  Date: {dt[0]}-{dt[1]:02d}-{dt[2]:02d} {dt[3]:02d}:{dt[4]:02d}:{dt[5]:02d}")
                
        if self.output_dir:
            print(f"\nFiles extracted to: {self.output_dir}")
    
    def save_manifest(self, manifest_path: str = None):
        """
        Save a JSON manifest of parsed files.
        
        Args:
            manifest_path: Path to save the manifest (default: manifest.json in output_dir)
        """
        if not manifest_path:
            manifest_path = os.path.join(self.output_dir, 'manifest.json')
            
        manifest = {
            'export_file': self.export_path,
            'total_files': len(self.instruct_files),
            'files': self.instruct_files
        }
        
        manifest_dir = os.path.dirname(manifest_path)
        if manifest_dir:
            os.makedirs(manifest_dir, exist_ok=True)
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"Manifest saved to: {manifest_path}")


def main():
    """Main entry point for the export parser CLI."""
    parser = argparse.ArgumentParser(
        description='Parse export files and extract instruct/dir/ files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a ZIP file and extract to default location
  python parse_export.py export.zip
  
  # Parse a TAR.GZ file and extract to custom directory
  python parse_export.py export.tar.gz -o /path/to/output
  
  # Parse and save a manifest file
  python parse_export.py export.zip -m manifest.json
        """
    )
    
    parser.add_argument(
        'export_file',
        help='Path to the export file (ZIP, TAR, TAR.GZ)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for extracted files (default: ./parsed_output)',
        default=None
    )
    
    parser.add_argument(
        '-m', '--manifest',
        help='Path to save a JSON manifest of parsed files',
        default=None
    )
    
    parser.add_argument(
        '--no-extract',
        action='store_true',
        help='List files without extracting them'
    )
    
    args = parser.parse_args()
    
    # Create parser instance
    output_dir = None if args.no_extract else args.output
    export_parser = ExportParser(args.export_file, output_dir)
    
    # Parse the export file
    export_parser.parse()
    
    # Print results
    export_parser.print_results()
    
    # Save manifest if requested
    if args.manifest:
        export_parser.save_manifest(args.manifest)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
