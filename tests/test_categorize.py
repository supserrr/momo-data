"""
Unit tests for transaction categorization module.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.categorize import TransactionCategorizer

class TestTransactionCategorizer(unittest.TestCase):
    """Test cases for TransactionCategorizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.categorizer = TransactionCategorizer()
    
    def test_categorize_deposit_transaction(self):
        """Test categorizing a deposit transaction."""
        transaction = {
            'amount': 50000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'type': 'DEPOSIT',
            'status': 'SUCCESS',
            'reference': 'DEP123456',
            'original_data': 'Deposit of 50000 UGX to account'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(categorized['category'], 'DEPOSIT')
        self.assertGreater(categorized['category_confidence'], 0.0)
        self.assertIn('categorized_at', categorized)
    
    def test_categorize_withdrawal_transaction(self):
        """Test categorizing a withdrawal transaction."""
        transaction = {
            'amount': 25000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'type': 'WITHDRAWAL',
            'status': 'SUCCESS',
            'reference': 'WIT123456',
            'original_data': 'Withdrawal of 25000 UGX from account'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(categorized['category'], 'WITHDRAWAL')
        self.assertGreater(categorized['category_confidence'], 0.0)
    
    def test_categorize_transfer_transaction(self):
        """Test categorizing a transfer transaction."""
        transaction = {
            'amount': 100000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'type': 'TRANSFER',
            'status': 'SUCCESS',
            'reference': 'TRF123456',
            'original_data': 'Transfer of 100000 UGX to another account'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(categorized['category'], 'TRANSFER')
        self.assertGreater(categorized['category_confidence'], 0.0)
    
    def test_categorize_payment_transaction(self):
        """Test categorizing a payment transaction."""
        transaction = {
            'amount': 15000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'type': 'PAYMENT',
            'status': 'SUCCESS',
            'reference': 'PAY123456',
            'original_data': 'Payment of 15000 UGX for utility bill'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(categorized['category'], 'PAYMENT')
        self.assertGreater(categorized['category_confidence'], 0.0)
    
    def test_categorize_query_transaction(self):
        """Test categorizing a query transaction."""
        transaction = {
            'amount': 0,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'type': 'QUERY',
            'status': 'SUCCESS',
            'reference': 'QRY123456',
            'original_data': 'Balance inquiry for account'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(categorized['category'], 'QUERY')
        self.assertGreater(categorized['category_confidence'], 0.0)
    
    def test_categorize_by_amount_heuristics(self):
        """Test categorization based on amount heuristics."""
        # Small amount - likely query
        small_transaction = {
            'amount': 500,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'original_data': 'Balance check'
        }
        
        categorized = self.categorizer.categorize_transaction(small_transaction)
        self.assertIn(categorized['category'], ['QUERY', 'OTHER'])
        
        # Large amount - likely transfer
        large_transaction = {
            'amount': 500000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'original_data': 'Large transaction'
        }
        
        categorized = self.categorizer.categorize_transaction(large_transaction)
        self.assertIn(categorized['category'], ['TRANSFER', 'PAYMENT'])
    
    def test_categorize_by_phone_patterns(self):
        """Test categorization based on phone number patterns."""
        # Merchant number
        merchant_transaction = {
            'amount': 15000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'original_data': 'Payment to merchant'
        }
        
        categorized = self.categorizer.categorize_transaction(merchant_transaction)
        # Should be categorized as payment due to merchant phone pattern
        self.assertIsNotNone(categorized['category'])
    
    def test_categorize_unknown_transaction(self):
        """Test categorizing an unknown transaction."""
        transaction = {
            'amount': 50000,
            'phone': '+256700123456',
            'date': '2025-01-15',
            'original_data': 'Some random transaction data'
        }
        
        categorized = self.categorizer.categorize_transaction(transaction)
        
        # Should default to UNKNOWN or be categorized based on amount
        self.assertIsNotNone(categorized['category'])
        self.assertGreaterEqual(categorized['category_confidence'], 0.0)
    
    def test_categorize_transactions_list(self):
        """Test categorizing a list of transactions."""
        transactions = [
            {
                'amount': 50000,
                'phone': '+256700123456',
                'date': '2025-01-15',
                'type': 'DEPOSIT',
                'status': 'SUCCESS',
                'original_data': 'Deposit transaction'
            },
            {
                'amount': 25000,
                'phone': '+256700123457',
                'date': '2025-01-15',
                'type': 'WITHDRAWAL',
                'status': 'SUCCESS',
                'original_data': 'Withdrawal transaction'
            },
            {
                'amount': 100000,
                'phone': '+256700123458',
                'date': '2025-01-15',
                'type': 'TRANSFER',
                'status': 'SUCCESS',
                'original_data': 'Transfer transaction'
            }
        ]
        
        categorized_transactions = self.categorizer.categorize_transactions(transactions)
        
        self.assertEqual(len(categorized_transactions), 3)
        
        # Check that all transactions have categories
        for transaction in categorized_transactions:
            self.assertIn('category', transaction)
            self.assertIn('category_confidence', transaction)
            self.assertIn('categorized_at', transaction)
    
    def test_calculate_category_score(self):
        """Test category score calculation."""
        # Test exact match
        score = self.categorizer._calculate_category_score(
            "deposit transaction", 
            ['deposit', 'credit', 'topup']
        )
        self.assertGreater(score, 0.0)
        
        # Test partial match
        score = self.assertGreater(
            self.categorizer._calculate_category_score(
                "withdrawal from account", 
                ['withdraw', 'debit', 'cashout']
            ), 0.0
        )
        
        # Test no match
        score = self.categorizer._calculate_category_score(
            "random text", 
            ['deposit', 'withdraw']
        )
        self.assertEqual(score, 0.0)
    
    def test_categorize_by_amount(self):
        """Test amount-based categorization."""
        # Small amount
        category, confidence = self.categorizer._categorize_by_amount(500, "balance check")
        self.assertIsNotNone(category)
        self.assertGreaterEqual(confidence, 0.0)
        
        # Medium amount
        category, confidence = self.categorizer._categorize_by_amount(50000, "deposit")
        self.assertIsNotNone(category)
        self.assertGreaterEqual(confidence, 0.0)
        
        # Large amount
        category, confidence = self.categorizer._categorize_by_amount(500000, "payment")
        self.assertIsNotNone(category)
        self.assertGreaterEqual(confidence, 0.0)
    
    def test_categorize_by_phone(self):
        """Test phone-based categorization."""
        # Merchant number
        category, confidence = self.categorizer._categorize_by_phone(
            "+256700123456", "payment to merchant"
        )
        self.assertIsNotNone(category)
        self.assertGreaterEqual(confidence, 0.0)
        
        # Regular number
        category, confidence = self.categorizer._categorize_by_phone(
            "+256700123456", "regular transaction"
        )
        # May or may not be categorized based on phone pattern
        self.assertGreaterEqual(confidence, 0.0)
    
    def test_get_categorization_summary(self):
        """Test getting categorization summary."""
        # Categorize some transactions first
        transactions = [
            {
                'amount': 50000,
                'phone': '+256700123456',
                'date': '2025-01-15',
                'type': 'DEPOSIT',
                'original_data': 'Deposit transaction'
            },
            {
                'amount': 25000,
                'phone': '+256700123457',
                'date': '2025-01-15',
                'type': 'WITHDRAWAL',
                'original_data': 'Withdrawal transaction'
            }
        ]
        
        self.categorizer.categorize_transactions(transactions)
        summary = self.categorizer.get_categorization_summary()
        
        self.assertIn('total_transactions', summary)
        self.assertIn('categorized', summary)
        self.assertIn('uncategorized', summary)
        self.assertIn('categorization_rate', summary)
        self.assertIn('category_distribution', summary)
        self.assertIn('categorized_at', summary)
        
        self.assertEqual(summary['total_transactions'], 2)
        self.assertGreaterEqual(summary['categorized'], 0)
        self.assertGreaterEqual(summary['uncategorized'], 0)
    
    def test_get_category_rules(self):
        """Test getting category rules."""
        rules = self.categorizer.get_category_rules()
        
        self.assertIsInstance(rules, dict)
        self.assertIn('DEPOSIT', rules)
        self.assertIn('WITHDRAWAL', rules)
        self.assertIn('TRANSFER', rules)
        self.assertIn('PAYMENT', rules)
        self.assertIn('QUERY', rules)
        self.assertIn('OTHER', rules)
    
    def test_add_custom_rule(self):
        """Test adding custom categorization rule."""
        self.categorizer.add_custom_rule('CUSTOM', ['custom', 'special'])
        
        rules = self.categorizer.get_category_rules()
        self.assertIn('CUSTOM', rules)
        self.assertIn('custom', rules['CUSTOM'])
        self.assertIn('special', rules['CUSTOM'])
    
    def test_update_category_rule(self):
        """Test updating existing categorization rule."""
        self.categorizer.update_category_rule('DEPOSIT', ['new_deposit', 'credit'])
        
        rules = self.categorizer.get_category_rules()
        self.assertEqual(rules['DEPOSIT'], ['new_deposit', 'credit'])

if __name__ == '__main__':
    unittest.main()
