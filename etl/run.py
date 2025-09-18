#!/usr/bin/env python3
"""
Enhanced ETL Pipeline for MTN MobileMoney SMS Data Processing
Uses the new enhanced parser with detailed message type categorization
"""

import argparse
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.config import XML_INPUT_FILE, ETL_LOG_FILE, LOG_LEVEL
from etl.parser import EnhancedMTNParser, ParsedTransaction
from etl.loader import MySQLDatabaseLoader
from etl.file_tracker import FileTracker

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
    logger.info(f"Enhanced ETL process started - Log level: {level}")
    return logger

def parse_xml_with_enhanced_parser(xml_file: Path) -> List[ParsedTransaction]:
    """Parse XML file using the enhanced parser."""
    import xml.etree.ElementTree as ET
    
    logger = logging.getLogger(__name__)
    parser = EnhancedMTNParser()
    transactions = []
    
    try:
        # Parse XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extract SMS elements
        sms_elements = root.findall('.//sms')
        logger.info(f"Found {len(sms_elements)} SMS elements")
        
        # Process each SMS
        for i, sms in enumerate(sms_elements):
            try:
                body = sms.get('body', '')
                date = sms.get('date', '')
                readable_date = sms.get('readable_date', '')
                
                # Skip if not a MoMo SMS
                if not _is_momo_sms(body, sms.get('address', '')):
                    continue
                
                # Parse timestamp
                timestamp = None
                if date:
                    try:
                        timestamp_int = int(date)
                        dt = datetime.fromtimestamp(timestamp_int / 1000)
                        timestamp = dt.isoformat()
                    except:
                        pass
                elif readable_date:
                    timestamp = readable_date
                
                # Parse message with enhanced parser
                transaction = parser.parse_message(body, timestamp)
                if transaction:
                    transactions.append(transaction)
                    
            except Exception as e:
                logger.error(f"Error processing SMS {i}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(transactions)} transactions")
        return transactions
        
    except Exception as e:
        logger.error(f"Error parsing XML file: {e}")
        raise

def _is_momo_sms(body: str, address: str) -> bool:
    """Check if SMS is a MoMo transaction."""
    # Check address
    momo_addresses = ['M-Money', 'MTN', 'MoMo', 'Mobile Money']
    if any(addr.lower() in address.lower() for addr in momo_addresses):
        return True
    
    # Check body content
    momo_keywords = [
        'RWF', 'UGX', 'deposit', 'withdraw', 'transfer', 'payment',
        'balance', 'mobile money', 'momo', 'transaction', 'TxId',
        'received', 'sent', 'completed', 'fee', 'new balance'
    ]
    
    body_lower = body.lower()
    return any(keyword.lower() in body_lower for keyword in momo_keywords)

def convert_to_database_format(transactions: List[ParsedTransaction]) -> List[Dict[str, Any]]:
    """Convert ParsedTransaction objects to database format."""
    db_transactions = []
    
    for transaction in transactions:
        db_transaction = {
            'amount': transaction.amount,
            'phone': transaction.recipient_phone or transaction.sender_phone,
            'date': transaction.date,
            'reference': transaction.transaction_id or transaction.financial_transaction_id or transaction.external_transaction_id,
            'type': transaction.transaction_type,
            'transaction_type': transaction.transaction_type,
            'direction': transaction.direction,
            'status': transaction.status,  # Use the status from parsed transaction
            'category': transaction.category,
            'category_confidence': transaction.confidence,
            'confidence': transaction.confidence,
            'recipient_name': transaction.recipient_name,
            'sender_name': transaction.sender_name,
            'sender_phone': transaction.sender_phone,
            'recipient_phone': transaction.recipient_phone,
            'momo_code': transaction.momo_code,
            'sender_momo_id': transaction.sender_momo_id,
            'agent_momo_number': transaction.agent_momo_number,
            'business_name': transaction.business_name,
            'fee': transaction.fee,
            'new_balance': transaction.new_balance,
            'financial_transaction_id': transaction.financial_transaction_id,
            'external_transaction_id': transaction.external_transaction_id,
            'personal_id': transaction.sender_momo_id or transaction.momo_code,
            'original_data': transaction.original_message,
            'original_message': transaction.original_message,
            'raw_data': transaction.original_message,
            'xml_tag': 'sms',
            'xml_attributes': {
                'transaction_type': transaction.transaction_type,
                'category': transaction.category,
                'direction': transaction.direction,
                'fee': transaction.fee,
                'new_balance': transaction.new_balance,
                'business_name': transaction.business_name,
                'agent_momo_number': transaction.agent_momo_number,
                'financial_transaction_id': transaction.financial_transaction_id,
                'external_transaction_id': transaction.external_transaction_id,
                'transaction_id': transaction.transaction_id
            },
            'parsed_at': datetime.now().isoformat(),
            'cleaned_at': datetime.now().isoformat(),
            'categorized_at': datetime.now().isoformat()
        }
        
        db_transactions.append(db_transaction)
    
    return db_transactions

def run_enhanced_etl_pipeline(xml_file: Path, export_json: bool = True) -> dict:
    """
    Run the enhanced ETL pipeline with detailed message type parsing.
    
    Args:
        xml_file: Path to XML input file
        export_json: Whether to export dashboard JSON
        
    Returns:
        Summary of ETL process
    """
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    
    # Initialize file tracker
    file_tracker = FileTracker()
    
    try:
        logger.info("=" * 60)
        logger.info("Starting Enhanced MTN MobileMoney ETL Pipeline")
        logger.info("=" * 60)
        
        # Check if file should be processed
        if not file_tracker.should_process_file(xml_file):
            logger.info(f"File {xml_file.name} has already been processed and hasn't changed. Skipping...")
            return {'status': 'skipped', 'message': 'File already processed and unchanged'}
        
        logger.info(f"Processing file: {xml_file.name}")
        
        # Step 1: Parse XML with enhanced parser
        logger.info("Step 1: Parsing XML with enhanced message type detection...")
        parsed_transactions = parse_xml_with_enhanced_parser(xml_file)
        
        if not parsed_transactions:
            logger.warning("No transactions found in XML file")
            return {'status': 'warning', 'message': 'No transactions found'}
        
        # Analyze transaction types
        type_stats = {}
        category_stats = {}
        for transaction in parsed_transactions:
            type_stats[transaction.transaction_type] = type_stats.get(transaction.transaction_type, 0) + 1
            category_stats[transaction.category] = category_stats.get(transaction.category, 0) + 1
        
        logger.info(f"Transaction Types: {type_stats}")
        logger.info(f"Transaction Categories: {category_stats}")
        
        # Step 2: Convert to database format
        logger.info("Step 2: Converting to database format...")
        db_transactions = convert_to_database_format(parsed_transactions)
        logger.info(f"Converted {len(db_transactions)} transactions to database format")
        
        # Step 3: Load to database
        logger.info("Step 3: Loading to MySQL database...")
        with MySQLDatabaseLoader() as db_loader:
            loading_summary = db_loader.load_transactions(db_transactions)
            logger.info(f"Loaded {loading_summary['successfully_loaded']} transactions to database")
            
            # Step 4: Export dashboard JSON
            if export_json:
                logger.info("Step 4: Exporting dashboard data...")
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
            'parsing_stats': {
                'total_parsed': len(parsed_transactions),
                'transaction_types': type_stats,
                'transaction_categories': category_stats
            },
            'loading': loading_summary,
            'database_stats': db_stats,
            'total_processed': len(parsed_transactions),
            'final_loaded': loading_summary['successfully_loaded']
        }
        
        # Mark file as processed
        file_tracker.mark_file_processed(
            xml_file, 
            loading_summary['successfully_loaded'], 
            'SUCCESS'
        )
        
        logger.info("=" * 60)
        logger.info("Enhanced ETL Pipeline Completed Successfully")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total processed: {final_summary['total_processed']}")
        logger.info(f"Final loaded: {final_summary['final_loaded']}")
        logger.info("=" * 60)
        
        return final_summary
        
    except Exception as e:
        logger.error(f"Enhanced ETL pipeline failed: {e}")
        
        # Mark file as failed
        file_tracker.mark_file_processed(
            xml_file, 
            0, 
            'FAILED', 
            str(e)
        )
        
        return {
            'status': 'error',
            'message': str(e),
            'duration_seconds': (datetime.now() - start_time).total_seconds(),
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat()
        }

def main():
    """Main entry point for enhanced ETL script."""
    parser = argparse.ArgumentParser(description='Enhanced MTN MobileMoney Data ETL Pipeline')
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
        help='Parse data without loading to database'
    )
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='Analyze message types and show statistics'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level)
    
    # Validate input file
    if not args.xml.exists():
        logger.error(f"XML file not found: {args.xml}")
        sys.exit(1)
    
    try:
        if args.dry_run or args.analyze:
            logger.info("Running in analysis mode...")
            # Parse and analyze without loading to database
            parsed_transactions = parse_xml_with_enhanced_parser(args.xml)
            
            if not parsed_transactions:
                logger.warning("No transactions found")
                sys.exit(0)
            
            # Analyze transaction types
            type_stats = {}
            category_stats = {}
            direction_stats = {}
            
            for transaction in parsed_transactions:
                type_stats[transaction.transaction_type] = type_stats.get(transaction.transaction_type, 0) + 1
                category_stats[transaction.category] = category_stats.get(transaction.category, 0) + 1
                direction_stats[transaction.direction] = direction_stats.get(transaction.direction, 0) + 1
            
            logger.info(f"Analysis Results:")
            logger.info(f"  Total transactions: {len(parsed_transactions)}")
            logger.info(f"  Transaction types: {type_stats}")
            logger.info(f"  Categories: {category_stats}")
            logger.info(f"  Directions: {direction_stats}")
            
            if args.analyze:
                # Show sample transactions
                logger.info("\nSample transactions:")
                for i, transaction in enumerate(parsed_transactions[:5]):
                    logger.info(f"  {i+1}. {transaction.transaction_type} - {transaction.category} - {transaction.amount} RWF")
                    logger.info(f"     Direction: {transaction.direction}")
                    if transaction.recipient_name:
                        logger.info(f"     Recipient: {transaction.recipient_name}")
                    if transaction.business_name:
                        logger.info(f"     Business: {transaction.business_name}")
                    logger.info(f"     Confidence: {transaction.confidence}")
                    logger.info("")
        else:
            # Run full enhanced ETL pipeline
            summary = run_enhanced_etl_pipeline(args.xml, export_json=not args.no_export)
            
            if summary['status'] == 'success':
                logger.info("Enhanced ETL pipeline completed successfully")
                sys.exit(0)
            elif summary['status'] == 'skipped':
                logger.info(f"ETL pipeline skipped: {summary.get('message', 'File already processed')}")
                sys.exit(0)
            else:
                logger.error(f"Enhanced ETL pipeline failed: {summary.get('message', 'Unknown error')}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("ETL process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
