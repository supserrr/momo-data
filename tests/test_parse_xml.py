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
        """Test parsing a simple MoMo SMS transaction."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="1" backup_set="test" backup_date="1737023646162" type="full">
            <sms protocol="0" address="M-Money" date="1715351458724" type="1" subject="null" 
                 body="You have received 50000 RWF from John Doe (+256700123456) on your mobile money account at 2024-05-10 16:30:51. Your new balance: 50000 RWF. Financial Transaction Id: TXN123456." 
                 toa="null" sc_toa="null" service_center="+250788110381" read="1" status="-1" 
                 locked="0" date_sent="1715351451000" sub_id="6" readable_date="10 May 2024 4:30:58 PM" 
                 contact_name="(Unknown)" />
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction['amount'], 50000.0)
        self.assertEqual(transaction['phone'], '+256700123456')
        self.assertEqual(transaction['type'], 'DEPOSIT')
        self.assertEqual(transaction['status'], 'SUCCESS')
        self.assertEqual(transaction['reference'], 'TXN123456')
    
    def test_parse_multiple_transactions(self):
        """Test parsing multiple MoMo SMS transactions."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="2" backup_set="test" backup_date="1737023646162" type="full">
            <sms protocol="0" address="M-Money" date="1715351458724" type="1" subject="null" 
                 body="TxId: 123456. Your payment of 25,000 RWF to Jane Smith 12845 has been completed at 2024-05-10 16:31:39. Your new balance: 25,000 RWF." 
                 toa="null" sc_toa="null" service_center="+250788110381" read="1" status="-1" 
                 locked="0" date_sent="1715351451000" sub_id="6" readable_date="10 May 2024 4:30:58 PM" 
                 contact_name="(Unknown)" />
            <sms protocol="0" address="M-Money" date="1715351506754" type="1" subject="null" 
                 body="*165*S*75000 RWF transferred to Alex Doe (250700123457) from 36521838 at 2024-05-10 16:32:00. Fee was: 100 RWF. New balance: 75000 RWF." 
                 toa="null" sc_toa="null" service_center="+250788110381" read="1" status="-1" 
                 locked="0" date_sent="1715351500000" sub_id="6" readable_date="10 May 2024 4:32:00 PM" 
                 contact_name="(Unknown)" />
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 2)
        
        # Check first transaction
        self.assertEqual(transactions[0]['amount'], 25000.0)
        self.assertEqual(transactions[0]['type'], 'PAYMENT')
        
        # Check second transaction
        self.assertEqual(transactions[1]['amount'], 75000.0)
        self.assertEqual(transactions[1]['type'], 'TRANSFER')
    
    def test_parse_unstructured_data(self):
        """Test parsing unstructured MoMo SMS data."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="1" backup_set="test" backup_date="1737023646162" type="full">
            <sms protocol="0" address="M-Money" date="1715351458724" type="1" subject="null" 
                 body="*113*R*A bank deposit of 100000 RWF has been added to your mobile money account at 2024-05-10 16:30:51. Your NEW BALANCE :100000 RWF." 
                 toa="null" sc_toa="null" service_center="+250788110381" read="1" status="-1" 
                 locked="0" date_sent="1715351451000" sub_id="6" readable_date="10 May 2024 4:30:58 PM" 
                 contact_name="(Unknown)" />
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        # Should extract data from unstructured text
        self.assertGreater(len(transactions), 0)
        transaction = transactions[0]
        self.assertEqual(transaction['amount'], 100000.0)
        self.assertEqual(transaction['type'], 'DEPOSIT')
    
    def test_parse_empty_file(self):
        """Test parsing empty XML file."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="0" backup_set="test" backup_date="1737023646162" type="full">
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        
        self.assertEqual(len(transactions), 0)
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML file."""
        xml_content = "This is not valid XML"
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        
        with self.assertRaises(Exception):
            parser.parse()
    
    def test_parse_malformed_xml(self):
        """Test parsing malformed XML file."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="1" backup_set="test" backup_date="1737023646162" type="full">
            <sms protocol="0" address="M-Money" date="1715351458724" type="1" subject="null" 
                 body="Incomplete SMS without proper closing
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        
        with self.assertRaises(Exception):
            parser.parse()
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file."""
        parser = XMLParser(Path("nonexistent.xml"))
        
        with self.assertRaises(FileNotFoundError):
            parser.parse()
    
    def test_amount_parsing(self):
        """Test amount parsing with various formats."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid amounts
        self.assertEqual(parser._extract_amount("50000 RWF"), 50000.0)
        self.assertEqual(parser._extract_amount("payment of 25,000 RWF"), 25000.0)
        self.assertEqual(parser._extract_amount("received 1000 UGX"), 1000.0)
        
        # Test invalid amounts
        self.assertIsNone(parser._extract_amount("no amount here"))
        self.assertIsNone(parser._extract_amount(""))
    
    def test_phone_parsing(self):
        """Test phone number parsing."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid phones
        self.assertEqual(parser._extract_phone("+256700123456"), "+256700123456")
        self.assertEqual(parser._extract_phone("256700123456"), "+256700123456")
        self.assertEqual(parser._extract_phone("0700123456"), "+250700123456")
        
        # Test invalid phones
        self.assertIsNone(parser._extract_phone("no phone here"))
        self.assertIsNone(parser._extract_phone(""))
    
    def test_date_parsing(self):
        """Test date parsing."""
        parser = XMLParser(self.temp_xml)
        
        # Test valid dates
        date1 = parser._parse_date("1715351458724", "10 May 2024 4:30:58 PM")
        self.assertIsNotNone(date1)
        
        date2 = parser._parse_date("", "2025-01-15 10:30:00")
        self.assertIsNotNone(date2)
        
        # Test invalid dates
        self.assertIsNone(parser._parse_date("", ""))
        self.assertIsNone(parser._parse_date("invalid", "invalid"))
    
    def test_get_parsing_summary(self):
        """Test getting parsing summary."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
        <smses count="1" backup_set="test" backup_date="1737023646162" type="full">
            <sms protocol="0" address="M-Money" date="1715351458724" type="1" subject="null" 
                 body="You have received 50000 RWF from John Doe (+256700123456) on your mobile money account at 2024-05-10 16:30:51. Your new balance: 50000 RWF. Financial Transaction Id: TXN123456." 
                 toa="null" sc_toa="null" service_center="+250788110381" read="1" status="-1" 
                 locked="0" date_sent="1715351451000" sub_id="6" readable_date="10 May 2024 4:30:58 PM" 
                 contact_name="(Unknown)" />
        </smses>"""
        
        self.create_test_xml(xml_content)
        parser = XMLParser(self.temp_xml)
        transactions = parser.parse()
        summary = parser.get_parsing_summary()
        
        self.assertIn('total_parsed', summary)
        self.assertIn('parsing_errors', summary)
        self.assertIn('error_rate', summary)
        self.assertIn('parsed_at', summary)
        self.assertEqual(summary['total_parsed'], 1)
        self.assertEqual(summary['parsing_errors'], 0)

if __name__ == '__main__':
    unittest.main()