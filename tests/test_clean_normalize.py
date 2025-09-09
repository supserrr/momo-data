"""
Unit tests for data cleaning and normalization module.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.clean_normalize import DataCleaner

class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = DataCleaner()
    
    def test_clean_amount_valid(self):
        """Test cleaning valid amounts."""
        # Test various valid amount formats
        self.assertEqual(self.cleaner.clean_amount(50000), 50000.0)
        self.assertEqual(self.cleaner.clean_amount("50000"), 50000.0)
        self.assertEqual(self.cleaner.clean_amount("50,000"), 50000.0)
        self.assertEqual(self.cleaner.clean_amount("UGX 50000"), 50000.0)
        self.assertEqual(self.cleaner.clean_amount("$50000"), 50000.0)
        self.assertEqual(self.cleaner.clean_amount("50000.50"), 50000.5)
    
    def test_clean_amount_invalid(self):
        """Test cleaning invalid amounts."""
        # Test invalid amounts
        self.assertIsNone(self.cleaner.clean_amount("invalid"))
        self.assertIsNone(self.cleaner.clean_amount(""))
        self.assertIsNone(self.cleaner.clean_amount(None))
        self.assertIsNone(self.cleaner.clean_amount(-100))
        self.assertIsNone(self.cleaner.clean_amount(0))
        self.assertIsNone(self.cleaner.clean_amount(10000001))  # Too large
    
    def test_clean_phone_valid(self):
        """Test cleaning valid phone numbers."""
        # Test various valid phone formats
        self.assertEqual(self.cleaner.clean_phone("+256700123456"), "+256700123456")
        self.assertEqual(self.cleaner.clean_phone("256700123456"), "+256700123456")
        self.assertEqual(self.cleaner.clean_phone("0700123456"), "+2560700123456")
        self.assertEqual(self.cleaner.clean_phone("+256-700-123-456"), "+256700123456")
        self.assertEqual(self.cleaner.clean_phone("(256) 700 123 456"), "256700123456")
    
    def test_clean_phone_invalid(self):
        """Test cleaning invalid phone numbers."""
        # Test invalid phones
        self.assertIsNone(self.cleaner.clean_phone("123"))
        self.assertIsNone(self.cleaner.clean_phone(""))
        self.assertIsNone(self.cleaner.clean_phone(None))
        self.assertIsNone(self.cleaner.clean_phone("abc"))
    
    def test_clean_date_valid(self):
        """Test cleaning valid dates."""
        # Test various valid date formats
        date1 = self.cleaner.clean_date("2025-01-15 10:30:00")
        self.assertIsNotNone(date1)
        
        date2 = self.cleaner.clean_date("2025-01-15")
        self.assertIsNotNone(date2)
        
        date3 = self.cleaner.clean_date("15/01/2025")
        self.assertIsNotNone(date3)
    
    def test_clean_date_invalid(self):
        """Test cleaning invalid dates."""
        # Test invalid dates
        self.assertIsNone(self.cleaner.clean_date(""))
        self.assertIsNone(self.cleaner.clean_date(None))
    
    def test_clean_reference(self):
        """Test cleaning reference numbers."""
        # Test valid references
        self.assertEqual(self.cleaner.clean_reference("TXN123456"), "TXN123456")
        self.assertEqual(self.cleaner.clean_reference("  TXN123456  "), "TXN123456")
        self.assertEqual(self.cleaner.clean_reference("TXN  123  456"), "TXN 123 456")
        
        # Test invalid references
        self.assertIsNone(self.cleaner.clean_reference(""))
        self.assertIsNone(self.cleaner.clean_reference(None))
        self.assertIsNone(self.cleaner.clean_reference("   "))
    
    def test_clean_type(self):
        """Test cleaning transaction types."""
        # Test type mapping
        self.assertEqual(self.cleaner.clean_type("DEP"), "DEPOSIT")
        self.assertEqual(self.cleaner.clean_type("WIT"), "WITHDRAWAL")
        self.assertEqual(self.cleaner.clean_type("TRF"), "TRANSFER")
        self.assertEqual(self.cleaner.clean_type("PAY"), "PAYMENT")
        self.assertEqual(self.cleaner.clean_type("BAL"), "QUERY")
        self.assertEqual(self.cleaner.clean_type("UNK"), "UNKNOWN")
        
        # Test case insensitive
        self.assertEqual(self.cleaner.clean_type("deposit"), "DEPOSIT")
        self.assertEqual(self.cleaner.clean_type("Withdrawal"), "WITHDRAWAL")
        
        # Test unknown types
        self.assertEqual(self.cleaner.clean_type("CUSTOM"), "CUSTOM")
        self.assertEqual(self.cleaner.clean_type(None), "UNKNOWN")
    
    def test_clean_status(self):
        """Test cleaning transaction status."""
        # Test status mapping
        self.assertEqual(self.cleaner.clean_status("SUCC"), "SUCCESS")
        self.assertEqual(self.cleaner.clean_status("FAIL"), "FAILED")
        self.assertEqual(self.cleaner.clean_status("PEND"), "PENDING")
        self.assertEqual(self.cleaner.clean_status("PROC"), "PROCESSING")
        self.assertEqual(self.cleaner.clean_status("COMP"), "COMPLETED")
        self.assertEqual(self.cleaner.clean_status("CANC"), "CANCELLED")
        self.assertEqual(self.cleaner.clean_status("REJ"), "REJECTED")
        self.assertEqual(self.cleaner.clean_status("TIMEOUT"), "FAILED")
        self.assertEqual(self.cleaner.clean_status("ERROR"), "FAILED")
        
        # Test case insensitive
        self.assertEqual(self.cleaner.clean_status("success"), "SUCCESS")
        self.assertEqual(self.cleaner.clean_status("Failed"), "FAILED")
        
        # Test unknown status
        self.assertEqual(self.cleaner.clean_status("CUSTOM"), "CUSTOM")
        self.assertEqual(self.cleaner.clean_status(None), "UNKNOWN")
    
    def test_clean_transaction_valid(self):
        """Test cleaning a valid transaction."""
        raw_transaction = {
            'amount': '50000',
            'phone': '+256700123456',
            'date': '2025-01-15 10:30:00',
            'reference': 'TXN123456',
            'type': 'DEP',
            'status': 'SUCC',
            'raw_data': 'Sample raw data'
        }
        
        cleaned = self.cleaner.clean_transaction(raw_transaction)
        
        self.assertIsNotNone(cleaned)
        self.assertEqual(cleaned['amount'], 50000.0)
        self.assertEqual(cleaned['phone'], '+256700123456')
        self.assertEqual(cleaned['type'], 'DEPOSIT')
        self.assertEqual(cleaned['status'], 'SUCCESS')
        self.assertEqual(cleaned['reference'], 'TXN123456')
        self.assertIn('cleaned_at', cleaned)
        self.assertEqual(cleaned['original_data'], 'Sample raw data')
    
    def test_clean_transaction_invalid(self):
        """Test cleaning an invalid transaction."""
        raw_transaction = {
            'amount': 'invalid',
            'phone': '123',
            'date': '2025-01-15',
            'reference': 'TXN123456',
            'type': 'DEP',
            'status': 'SUCC'
        }
        
        cleaned = self.cleaner.clean_transaction(raw_transaction)
        
        # Should return None due to invalid amount and phone
        self.assertIsNone(cleaned)
    
    def test_clean_transactions_list(self):
        """Test cleaning a list of transactions."""
        raw_transactions = [
            {
                'amount': '50000',
                'phone': '+256700123456',
                'date': '2025-01-15',
                'reference': 'TXN123456',
                'type': 'DEP',
                'status': 'SUCC'
            },
            {
                'amount': '25000',
                'phone': '+256700123457',
                'date': '2025-01-15',
                'reference': 'TXN123457',
                'type': 'WIT',
                'status': 'SUCC'
            },
            {
                'amount': 'invalid',
                'phone': '123',
                'date': '2025-01-15',
                'reference': 'TXN123458',
                'type': 'DEP',
                'status': 'SUCC'
            }
        ]
        
        cleaned_transactions = self.cleaner.clean_transactions(raw_transactions)
        
        # Should have 2 valid transactions (third is invalid)
        self.assertEqual(len(cleaned_transactions), 2)
        self.assertEqual(cleaned_transactions[0]['amount'], 50000.0)
        self.assertEqual(cleaned_transactions[1]['amount'], 25000.0)
    
    def test_get_cleaning_summary(self):
        """Test getting cleaning summary."""
        # Clean some transactions first
        raw_transactions = [
            {'amount': '50000', 'phone': '+256700123456', 'date': '2025-01-15'},
            {'amount': 'invalid', 'phone': '123', 'date': '2025-01-15'}
        ]
        
        self.cleaner.clean_transactions(raw_transactions)
        summary = self.cleaner.get_cleaning_summary()
        
        self.assertIn('total_processed', summary)
        self.assertIn('successfully_cleaned', summary)
        self.assertIn('cleaning_errors', summary)
        self.assertIn('error_rate', summary)
        self.assertIn('errors', summary)
        self.assertIn('cleaned_at', summary)
        
        self.assertEqual(summary['total_processed'], 2)
        self.assertEqual(summary['successfully_cleaned'], 1)
        self.assertEqual(summary['cleaning_errors'], 1)
        self.assertEqual(summary['error_rate'], 0.5)

if __name__ == '__main__':
    unittest.main()
