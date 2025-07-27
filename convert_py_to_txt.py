#!/usr/bin/env python3
"""
Python to Text File Converter

This script converts all .py files to .txt files in the current directory
and all subdirectories, preserving the original content.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('convert_py_to_txt.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PyToTxtConverter:
    def __init__(self, root_dir="."):
        """Initialize the converter."""
        self.root_dir = Path(root_dir).resolve()
        self.converted_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def find_py_files(self):
        """Find all .py files in the directory tree."""
        py_files = []
        try:
            for py_file in self.root_dir.rglob("*.py"):
                # Skip __pycache__ directories
                if "__pycache__" in str(py_file):
                    continue
                py_files.append(py_file)
            return py_files
        except Exception as e:
            logger.error(f"Error finding .py files: {e}")
            return []
    
    def convert_file(self, py_file_path):
        """Convert a single .py file to .txt."""
        try:
            # Create the corresponding .txt file path
            txt_file_path = py_file_path.with_suffix('.txt')
            
            # Check if .txt file already exists
            if txt_file_path.exists():
                logger.warning(f"Text file already exists: {txt_file_path}")
                return False
            
            # Copy the .py file to .txt
            shutil.copy2(py_file_path, txt_file_path)
            logger.info(f"Converted: {py_file_path} -> {txt_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting {py_file_path}: {e}")
            return False
    
    def run(self, dry_run=False, force=False):
        """Main execution method."""
        logger.info(f"Starting conversion from: {self.root_dir}")
        
        if dry_run:
            logger.info("DRY RUN MODE - No files will be converted")
        
        py_files = self.find_py_files()
        
        if not py_files:
            logger.warning("No .py files found in the directory tree")
            return True
        
        logger.info(f"Found {len(py_files)} .py files to convert:")
        for py_file in py_files:
            logger.info(f"  - {py_file}")
        
        if dry_run:
            logger.info("DRY RUN: Would convert the above files")
            return True
        
        # Ask for confirmation unless force is used
        if not force:
            confirm = input(f"⚠️  Convert {len(py_files)} .py files to .txt? (type 'yes' to confirm): ")
            if confirm.lower() != 'yes':
                logger.info("Conversion cancelled by user")
                return False
        
        # Convert files
        for py_file in py_files:
            if self.convert_file(py_file):
                self.converted_count += 1
            else:
                self.error_count += 1
        
        logger.info(f"Conversion complete!")
        logger.info(f"  - Converted: {self.converted_count}")
        logger.info(f"  - Errors: {self.error_count}")
        
        return self.error_count == 0


def main():
    """Main function to run the converter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert .py files to .txt files")
    parser.add_argument("--dir", default=".", help="Root directory to search (default: current)")
    parser.add_argument("--parent-dir", help="Parent directory path to search in")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be converted without doing it")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    try:
        # Use parent directory if specified, otherwise use --dir
        target_dir = args.parent_dir if args.parent_dir else args.dir
        converter = PyToTxtConverter(target_dir)
        
        if args.dry_run:
            success = converter.run(dry_run=True)
        else:
            success = converter.run(dry_run=False, force=args.force)
        
        if success:
            print("✅ File conversion completed successfully!")
            sys.exit(0)
        else:
            print("❌ File conversion failed. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 