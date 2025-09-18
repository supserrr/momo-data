#!/usr/bin/env python3
"""
Script to add new files to the data/raw directory and process them.
"""

import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from etl.run import run_enhanced_etl_pipeline
from etl.file_tracker import FileTracker

def add_and_process_file(source_file: Path, target_name: str = None):
    """
    Add a new file to the data/raw directory and process it.
    
    Args:
        source_file: Path to the source file to copy
        target_name: Optional new name for the file (defaults to source file name)
    """
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        return False
    
    # Set target name
    if target_name is None:
        target_name = source_file.name
    
    # Create target path
    target_path = Path("data/raw") / target_name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    print(f"📁 Copying {source_file} to {target_path}")
    shutil.copy2(source_file, target_path)
    
    # Process the file
    print(f"🔄 Processing {target_name}...")
    result = run_enhanced_etl_pipeline(target_path)
    
    if result['status'] == 'success':
        print(f"✅ Successfully processed {target_name}")
        print(f"   Records loaded: {result['final_loaded']}")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
    elif result['status'] == 'skipped':
        print(f"⏭️  Skipped {target_name} (already processed)")
    else:
        print(f"❌ Failed to process {target_name}: {result.get('message', 'Unknown error')}")
    
    return result['status'] == 'success'

def main():
    """Main function for adding and processing files."""
    if len(sys.argv) < 2:
        print("Usage: python add_new_file.py <source_file> [target_name]")
        print("Example: python add_new_file.py /path/to/new_data.xml new_transactions.xml")
        sys.exit(1)
    
    source_file = Path(sys.argv[1])
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = add_and_process_file(source_file, target_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
