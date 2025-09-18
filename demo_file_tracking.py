#!/usr/bin/env python3
"""
File Tracking System - Test and Demonstration Script
Shows how the system prevents reprocessing of unchanged files and provides testing functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from etl.file_tracker import FileTracker

def test_file_tracking():
    """Test the file tracking system."""
    print("Testing File Tracking System")
    print("=" * 40)
    
    # Initialize file tracker
    tracker = FileTracker()
    
    # Test file
    test_file = Path("data/raw/modified_sms_v2.xml")
    
    print(f"Testing with file: {test_file}")
    print(f"File exists: {test_file.exists()}")
    
    if test_file.exists():
        # Check if file should be processed
        should_process = tracker.should_process_file(test_file)
        print(f"Should process file: {should_process}")
        
        # Get file stats
        stats = tracker.get_file_stats()
        print(f"\nFile Statistics:")
        print(f"  Total files processed: {stats['total_files']}")
        print(f"  Successfully processed: {stats['success_files']}")
        print(f"  Failed files: {stats['failed_files']}")
        print(f"  Total records processed: {stats['total_records']}")
        
        # Get processed files list
        processed_files = tracker.get_processed_files()
        print(f"\nProcessed Files ({len(processed_files)}):")
        for file_info in processed_files:
            print(f"  - {file_info['file_name']}")
            print(f"    Path: {file_info['file_path']}")
            print(f"    Processed: {file_info['processed_at']}")
            print(f"    Records: {file_info['records_processed']}")
            print(f"    Status: {file_info['processing_status']}")
            if file_info['error_message']:
                print(f"    Error: {file_info['error_message']}")
            print()

def demo_file_tracking():
    """Demonstrate the file tracking system."""
    print("File Tracking System Demonstration")
    print("=" * 50)
    
    # Initialize file tracker
    tracker = FileTracker()
    
    # Current file
    current_file = Path("data/raw/modified_sms_v2.xml")
    
    print(f"Testing with file: {current_file}")
    print(f"File exists: {current_file.exists()}")
    print()
    
    # Check file status
    print("File Status Check:")
    print(f"  Is processed: {tracker.is_file_processed(current_file)}")
    print(f"  Has changed: {tracker.is_file_changed(current_file)}")
    print(f"  Should process: {tracker.should_process_file(current_file)}")
    print()
    
    # Get file statistics
    stats = tracker.get_file_stats()
    print("File Processing Statistics:")
    print(f"  Total files processed: {stats['total_files']}")
    print(f"  Successfully processed: {stats['success_files']}")
    print(f"  Failed files: {stats['failed_files']}")
    print(f"  Total records processed: {stats['total_records']}")
    print()
    
    # Show processed files
    processed_files = tracker.get_processed_files()
    print("Processed Files:")
    for file_info in processed_files:
        print(f"  📁 {file_info['file_name']}")
        print(f"     Path: {file_info['file_path']}")
        print(f"     Processed: {file_info['processed_at']}")
        print(f"     Records: {file_info['records_processed']}")
        print(f"     Status: {file_info['processing_status']}")
        if file_info['error_message']:
            print(f"     Error: {file_info['error_message']}")
        print()
    
    print("System Behavior:")
    print("✅ Files are only processed if they are new or have been modified")
    print("✅ Duplicate transactions are automatically prevented")
    print("✅ File changes are detected by size and hash comparison")
    print("✅ Processing history is maintained for audit purposes")

def main():
    """Main function with command line options."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_file_tracking()
    else:
        demo_file_tracking()

if __name__ == "__main__":
    main()
