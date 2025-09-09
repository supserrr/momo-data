"""
Unit tests for XML parsing module.
"""

import unittest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.parse_xml import XMLParser

class TestXMLParser(unittest.TestCase):
    """Test cases for XMLParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_xml = Path(self.temp_dir) / "test_momo.xml"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_xml(self, xml_content):
        """Create a temporary XML file with given content."""
        with open(self.temp_xml, 'w') as f:
            f.write(xml_content)
        return self.temp_xml
    
    def test_parse_simple_transaction(self):
        """Test parsing a simple transaction XML."""
        xml_content = """
        <transactions>
            <transaction>
                <amount>50000</amount>
                <phone>+256700123456</phone>
                <date>2025-01-15 10:30:00</date>
                <reference>TXN123456</reference>
                <type>DEPOSIT</type>
                <status>SUCCESS</status>
            </transaction>
        </transactions>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        
        self.assertEqual(transaction['amount'], 50000.0)
        self.assertEqual(transaction['phone'], '+256700123456')
        self.assertEqual(transaction['reference'], 'TXN123456')
        self.assertEqual(transaction['type'], 'DEPOSIT')
        self.assertEqual(transaction['status'], 'SUCCESS')
    
    def test_parse_multiple_transactions(self):
        """Test parsing multiple transactions."""
        xml_content = """
        <transactions>
            <transaction>
                <amount>25000</amount>
                <phone>+256700123456</phone>
                <date>2025-01-15</date>
            </transaction>
            <transaction>
                <amount>75000</amount>
                <phone>+256700123457</phone>
                <date>2025-01-15</date>
            </transaction>
        </transactions>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['amount'], 25000.0)
        self.assertEqual(transactions[1]['amount'], 75000.0)
    
    def test_parse_unstructured_data(self):
        """Test parsing unstructured transaction data."""
        xml_content = """
        <data>
            <record>Amount: 100000 Phone: +256700123456 Date: 2025-01-15</record>
            <record>Amount: 50000 Phone: +256700123457 Date: 2025-01-15</record>
        </data>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        # Should extract data from unstructured text
        self.assertGreater(len(transactions), 0)
        
        # Check if amounts and phones were extracted
        for transaction in transactions:
            if 'amount' in transaction:
                self.assertIsInstance(transaction['amount'], (int, float))
            if 'phone' in transaction:
                self.assertIsInstance(transaction['phone'], str)
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML."""
        xml_content = """
        <transactions>
            <transaction>
                <amount>invalid</amount>
                <phone></phone>
            </transaction>
        </transactions>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        # Should handle invalid data gracefully
        self.assertIsInstance(transactions, list)
    
    def test_parse_empty_file(self):
        """Test parsing empty XML file."""
        xml_content = "<transactions></transactions>"
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 0)
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.xml"
        parser = XMLParser(nonexistent_file)
        
        with self.assertRaises(FileNotFoundError):
            parser.parse()
    
    def test_parse_malformed_xml(self):
        """Test parsing malformed XML."""
        xml_content = """
        <transactions>
            <transaction>
                <amount>50000</amount>
                <phone>+256700123456</phone>
            </transaction>
            <unclosed_tag>
        </transactions>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        
        with self.assertRaises(ET.ParseError):
            parser.parse()
    
    def test_get_parsing_summary(self):
        """Test getting parsing summary."""
        xml_content = """
        <transactions>
            <transaction>
                <amount>50000</amount>
                <phone>+256700123456</phone>
                <date>2025-01-15</date>
            </transaction>
        </transactions>
        """
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        summary = parser.get_parsing_summary()
        
        self.assertIn('total_parsed', summary)
        self.assertIn('valid_transactions', summary)
        self.assertIn('invalid_transactions', summary)
        self.assertIn('xml_file', summary)
        self.assertIn('parsed_at', summary)
        
        self.assertEqual(summary['total_parsed'], len(transactions))
    
    def test_amount_parsing(self):
        """Test amount parsing with various formats."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid amounts
        self.assertEqual(parser._parse_amount("50000"), 50000.0)
        self.assertEqual(parser._parse_amount("50,000"), 50000.0)
        self.assertEqual(parser._parse_amount("UGX 50000"), 50000.0)
        self.assertEqual(parser._parse_amount("$50000"), 50000.0)
        
        # Test invalid amounts
        self.assertIsNone(parser._parse_amount("invalid"))
        self.assertIsNone(parser._parse_amount(""))
        self.assertIsNone(parser._parse_amount(None))
    
    def test_phone_parsing(self):
        """Test phone number parsing."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid phones
        self.assertEqual(parser._parse_phone("+256700123456"), "+256700123456")
        self.assertEqual(parser._parse_phone("256700123456"), "256700123456")
        self.assertEqual(parser._parse_phone("0700123456"), "0700123456")
        
        # Test invalid phones
        self.assertIsNone(parser._parse_phone("123"))
        self.assertIsNone(parser._parse_phone(""))
        self.assertIsNone(parser._parse_phone(None))
    
    def test_date_parsing(self):
        """Test date parsing."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid dates
        date1 = parser._parse_date("2025-01-15 10:30:00")
        self.assertIsNotNone(date1)
        
        date2 = parser._parse_date("2025-01-15")
        self.assertIsNotNone(date2)
        
        # Test invalid dates
        self.assertIsNone(parser._parse_date(""))
        self.assertIsNone(parser._parse_date(None))

if __name__ == '__main__':
    unittest.main()
