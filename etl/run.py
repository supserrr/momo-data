#!/usr/bin/env python3
"""
ETL Pipeline for MoMo SMS Data Processing
Team 11 - Enterprise Web Development
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.config import XML_INPUT_FILE, ETL_LOG_FILE, LOG_LEVEL
from etl.parse_xml import XMLParser
from etl.clean_normalize import DataCleaner
from etl.categorize import TransactionCategorizer
from etl.load_db import DatabaseLoader

def setup_logging(log_file: Path = ETL_LOG_FILE, level: str = LOG_LEVEL):
    """Setup logging configuration."""
    # Create logs directory
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"ETL process started - Log level: {level}")
    return logger

def run_etl_pipeline(xml_file: Path, export_json: bool = True) -> dict:
    """
    Run the complete ETL pipeline.
    This function orchestrates the entire data processing workflow.
    
    Args:
        xml_file: Path to XML input file
        export_json: Whether to export dashboard JSON
        
    Returns:
        Summary of ETL process
    """
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    
    try:
        logger.info("=" * 50)
        logger.info("Starting MoMo ETL Pipeline")
        logger.info("=" * 50)
        
        # Step 1: Parse XML
        logger.info("Step 1: Parsing XML data...")
        parser = XMLParser(xml_file)
        raw_transactions = parser.parse()
        parse_summary = parser.get_parsing_summary()
        logger.info(f"Parsed {parse_summary['total_parsed']} transactions")
        
        if not raw_transactions:
            logger.warning("No transactions found in XML file")
            return {'status': 'warning', 'message': 'No transactions found'}
        
        # Step 2: Clean and normalize
        logger.info("Step 2: Cleaning and normalizing data...")
        cleaner = DataCleaner()
        cleaned_transactions = cleaner.clean_transactions(raw_transactions)
        cleaning_summary = cleaner.get_cleaning_summary()
        logger.info(f"Cleaned {cleaning_summary['successfully_cleaned']} transactions")
        
        if not cleaned_transactions:
            logger.error("No valid transactions after cleaning")
            return {'status': 'error', 'message': 'No valid transactions after cleaning'}
        
        # Step 3: Categorize
        logger.info("Step 3: Categorizing transactions...")
        categorizer = TransactionCategorizer()
        categorized_transactions = categorizer.categorize_transactions(cleaned_transactions)
        categorization_summary = categorizer.get_categorization_summary()
        logger.info(f"Categorized {categorization_summary['categorized']} transactions")
        
        # Step 4: Load to database
        logger.info("Step 4: Loading to database...")
        with DatabaseLoader() as db_loader:
            loading_summary = db_loader.load_transactions(categorized_transactions)
            logger.info(f"Loaded {loading_summary['successfully_loaded']} transactions to database")
            
            # Step 5: Export dashboard JSON
            if export_json:
                logger.info("Step 5: Exporting dashboard data...")
                dashboard_data = db_loader.export_dashboard_json()
                logger.info("Dashboard data exported successfully")
            
            # Get final database stats
            db_stats = db_loader.get_database_stats()
        
        # Compile final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        final_summary = {
            'status': 'success',
            'duration_seconds': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'steps': {
                'parsing': parse_summary,
                'cleaning': cleaning_summary,
                'categorization': categorization_summary,
                'loading': loading_summary
            },
            'database_stats': db_stats,
            'total_processed': len(raw_transactions),
            'final_loaded': loading_summary['successfully_loaded']
        }
        
        logger.info("=" * 50)
        logger.info("ETL Pipeline Completed Successfully")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total processed: {final_summary['total_processed']}")
        logger.info(f"Final loaded: {final_summary['final_loaded']}")
        logger.info("=" * 50)
        
        return final_summary
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'duration_seconds': (datetime.now() - start_time).total_seconds(),
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat()
        }

def main():
    """Main entry point for ETL script."""
    parser = argparse.ArgumentParser(description='MoMo Data ETL Pipeline')
    parser.add_argument(
        '--xml', 
        type=Path, 
        default=XML_INPUT_FILE,
        help='Path to XML input file'
    )
    parser.add_argument(
        '--no-export', 
        action='store_true',
        help='Skip dashboard JSON export'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=LOG_LEVEL,
        help='Logging level'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Parse and clean data without loading to database'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level)
    
    # Validate input file
    if not args.xml.exists():
        logger.error(f"XML file not found: {args.xml}")
        sys.exit(1)
    
    try:
        if args.dry_run:
            logger.info("Running in dry-run mode...")
            # Just parse and clean, don't load to database
            parser = XMLParser(args.xml)
            raw_transactions = parser.parse()
            
            cleaner = DataCleaner()
            cleaned_transactions = cleaner.clean_transactions(raw_transactions)
            
            categorizer = TransactionCategorizer()
            categorized_transactions = categorizer.categorize_transactions(cleaned_transactions)
            
            logger.info(f"Dry run completed: {len(categorized_transactions)} transactions processed")
            logger.info("Sample transaction:")
            if categorized_transactions:
                sample = categorized_transactions[0]
                logger.info(f"  Amount: {sample.get('amount')}")
                logger.info(f"  Phone: {sample.get('phone')}")
                logger.info(f"  Category: {sample.get('category')}")
                logger.info(f"  Confidence: {sample.get('category_confidence')}")
        else:
            # Run full ETL pipeline
            summary = run_etl_pipeline(args.xml, export_json=not args.no_export)
            
            if summary['status'] == 'success':
                logger.info("ETL pipeline completed successfully")
                sys.exit(0)
            else:
                logger.error(f"ETL pipeline failed: {summary.get('message', 'Unknown error')}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("ETL process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
