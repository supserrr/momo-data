#!/usr/bin/env python3
"""
Test script to verify the MoMo data processing setup.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test ETL imports
        from etl.config import DATABASE_FILE, XML_INPUT_FILE
        from etl.parse_xml import XMLParser
        from etl.clean_normalize import DataCleaner
        from etl.categorize import TransactionCategorizer
        from etl.load_db import DatabaseLoader
        print("✓ ETL modules imported successfully")
        
        # Test API imports
        from api.db import DatabaseManager
        from api.schemas import Transaction, DashboardData
        print("✓ API modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_directories():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "data/raw",
        "data/processed", 
        "logs",
        "logs/dead_letter",
        "etl",
        "api",
        "scripts",
        "tests",
        "web",
        "web/assets"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} - Missing")
            all_exist = False
    
    return all_exist

def test_files():
    """Test that all required files exist."""
    print("\nTesting required files...")
    
    required_files = [
        "README.md",
        "requirements.txt",
        "env.example",
        ".gitignore",
        "index.html",
        "web/styles.css",
        "web/chart_handler.js",
        "etl/__init__.py",
        "etl/config.py",
        "etl/parse_xml.py",
        "etl/clean_normalize.py",
        "etl/categorize.py",
        "etl/load_db.py",
        "etl/run.py",
        "api/__init__.py",
        "api/app.py",
        "api/db.py",
        "api/schemas.py",
        "scripts/run_etl.sh",
        "scripts/export_json.sh",
        "scripts/serve_frontend.sh",
        "tests/test_parse_xml.py",
        "tests/test_clean_normalize.py",
        "tests/test_categorize.py",
        "data/raw/sample_momo.xml"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_sample_data():
    """Test that sample data can be parsed."""
    print("\nTesting sample data parsing...")
    
    try:
        from etl.parse_xml import XMLParser
        
        sample_file = Path("data/raw/sample_momo.xml")
        if not sample_file.exists():
            print("✗ Sample XML file not found")
            return False
        
        parser = XMLParser(sample_file)
        transactions = parser.parse()
        
        if len(transactions) > 0:
            print(f"✓ Successfully parsed {len(transactions)} transactions from sample data")
            return True
        else:
            print("✗ No transactions found in sample data")
            return False
            
    except Exception as e:
        print(f"✗ Error parsing sample data: {e}")
        return False

def test_etl_pipeline():
    """Test the ETL pipeline with sample data."""
    print("\nTesting ETL pipeline...")
    
    try:
        from etl.parse_xml import XMLParser
        from etl.clean_normalize import DataCleaner
        from etl.categorize import TransactionCategorizer
        
        # Parse sample data
        sample_file = Path("data/raw/sample_momo.xml")
        parser = XMLParser(sample_file)
        raw_transactions = parser.parse()
        
        # Clean data
        cleaner = DataCleaner()
        cleaned_transactions = cleaner.clean_transactions(raw_transactions)
        
        # Categorize data
        categorizer = TransactionCategorizer()
        categorized_transactions = categorizer.categorize_transactions(cleaned_transactions)
        
        print(f"✓ ETL pipeline completed successfully")
        print(f"  - Raw transactions: {len(raw_transactions)}")
        print(f"  - Cleaned transactions: {len(cleaned_transactions)}")
        print(f"  - Categorized transactions: {len(categorized_transactions)}")
        
        return True
        
    except Exception as e:
        print(f"✗ ETL pipeline error: {e}")
        return False

def main():
    """Run all tests."""
    print("MoMo Data Processing Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_directories,
        test_files,
        test_sample_data,
        test_etl_pipeline
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests passed!")
        print("\nSetup is complete and ready for development.")
        print("\nNext steps:")
        print("1. Update team information in README.md")
        print("2. Create system architecture diagram")
        print("3. Set up Scrum board")
        print("4. Run: ./scripts/run_etl.sh -x data/raw/sample_momo.xml")
        print("5. Run: ./scripts/serve_frontend.sh")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} tests failed")
        print("\nPlease fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
