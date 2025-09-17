"""
XML Parser for MoMo SMS Data
Team 11 - Enterprise Web Development
"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class XMLParser:
    """Parser for MoMo XML transaction data."""
    
    def __init__(self, xml_file_path: Path):
        self.xml_file_path = xml_file_path
        self.transactions = []
        
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse XML file and extract transaction data.
        
        Returns:
            List of transaction dictionaries
        """
        try:
            if not self.xml_file_path.exists():
                raise FileNotFoundError(f"XML file not found: {self.xml_file_path}")
                
            logger.info(f"Parsing XML file: {self.xml_file_path}")
            
            # Parse XML file
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            
            # Extract transactions based on XML structure
            # This is a generic parser - adjust based on actual XML structure
            transactions = []
            
            # Look for common transaction elements
            for transaction_elem in root.findall('.//transaction'):
                transaction = self._extract_transaction(transaction_elem)
                if transaction:
                    transactions.append(transaction)
            
            # If no transactions found with 'transaction' tag, try other common tags
            if not transactions:
                for elem in root.findall('.//*'):
                    if self._is_transaction_element(elem):
                        transaction = self._extract_transaction(elem)
                        if transaction:
                            transactions.append(transaction)
            
            logger.info(f"Successfully parsed {len(transactions)} transactions")
            self.transactions = transactions
            return transactions
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing XML file: {e}")
            raise
    
    def _is_transaction_element(self, element) -> bool:
        """Check if element represents a transaction."""
        # Look for common transaction indicators
        transaction_indicators = ['amount', 'phone', 'date', 'time', 'reference', 'id']
        text_content = element.text or ''
        tag_name = element.tag.lower()
        
        return (
            any(indicator in tag_name for indicator in transaction_indicators) or
            any(indicator in text_content.lower() for indicator in transaction_indicators)
        )
    
    def _extract_transaction(self, element) -> Optional[Dict[str, Any]]:
        """Extract transaction data from XML element."""
        try:
            transaction = {}
            
            # Store raw data for debugging and analysis
            transaction['raw_data'] = self._get_element_text(element)
            transaction['xml_tag'] = element.tag
            transaction['xml_attributes'] = dict(element.attrib)
            
            # Try to extract structured data
            for child in element:
                tag_name = child.tag.lower()
                text_value = self._get_element_text(child)
                
                if text_value:
                    # Map common field names
                    if 'amount' in tag_name or 'value' in tag_name:
                        transaction['amount'] = self._parse_amount(text_value)
                    elif 'phone' in tag_name or 'mobile' in tag_name or 'msisdn' in tag_name:
                        transaction['phone'] = self._parse_phone(text_value)
                    elif 'date' in tag_name or 'time' in tag_name or 'timestamp' in tag_name:
                        transaction['date'] = self._parse_date(text_value)
                    elif 'reference' in tag_name or 'ref' in tag_name or 'id' in tag_name:
                        transaction['reference'] = text_value
                    elif 'type' in tag_name or 'category' in tag_name:
                        transaction['type'] = text_value
                    elif 'status' in tag_name or 'result' in tag_name:
                        transaction['status'] = text_value
                    else:
                        # Store other fields with original tag name
                        transaction[tag_name] = text_value
            
            # If no structured data found, try to parse from text content
            if len(transaction) <= 3:  # Only has raw_data, xml_tag, xml_attributes
                parsed_data = self._parse_unstructured_text(transaction['raw_data'])
                transaction.update(parsed_data)
            
            # Validate transaction has minimum required fields
            if self._validate_transaction(transaction):
                return transaction
            else:
                logger.warning(f"Invalid transaction data: {transaction}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting transaction from element: {e}")
            return None
    
    def _get_element_text(self, element) -> str:
        """Get text content from XML element."""
        if element.text:
            return element.text.strip()
        return ''
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount from string."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = amount_str.replace('UGX', '').replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_phone(self, phone_str: str) -> Optional[str]:
        """Parse and normalize phone number."""
        if not phone_str:
            return None
        
        # Remove common separators
        cleaned = phone_str.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Basic validation
        if len(cleaned) >= 10:
            return cleaned
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date from string."""
        if not date_str:
            return None
        
        # Try common date formats
        from dateutil import parser
        
        try:
            parsed_date = parser.parse(date_str)
            return parsed_date.isoformat()
        except:
            return date_str  # Return as-is if parsing fails
    
    def _parse_unstructured_text(self, text: str) -> Dict[str, Any]:
        """Parse unstructured text for transaction data."""
        parsed = {}
        
        if not text:
            return parsed
        
        # Simple regex patterns for common data
        import re
        
        # Amount patterns
        amount_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # 1,000.00
            r'(\d+(?:\.\d{2})?)',  # 1000.00
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    amount = float(matches[0].replace(',', ''))
                    if 100 <= amount <= 10000000:  # Reasonable amount range
                        parsed['amount'] = amount
                        break
                except ValueError:
                    continue
        
        # Phone patterns
        phone_patterns = [
            r'(\+?256\d{9})',  # +256XXXXXXXXX
            r'(0\d{9})',       # 0XXXXXXXXX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                parsed['phone'] = match.group(1)
                break
        
        # Date patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                parsed['date'] = match.group(1)
                break
        
        return parsed
    
    def _validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate transaction has minimum required fields."""
        required_fields = ['amount', 'phone']
        
        for field in required_fields:
            if field not in transaction or transaction[field] is None:
                return False
        
        # Validate amount range
        amount = transaction.get('amount')
        if not isinstance(amount, (int, float)) or amount <= 0:
            return False
        
        # Validate phone number
        phone = transaction.get('phone')
        if not isinstance(phone, str) or len(phone) < 10:
            return False
        
        return True
    
    def get_parsing_summary(self) -> Dict[str, Any]:
        """Get summary of parsing results."""
        return {
            'total_parsed': len(self.transactions),
            'valid_transactions': len([t for t in self.transactions if self._validate_transaction(t)]),
            'invalid_transactions': len([t for t in self.transactions if not self._validate_transaction(t)]),
            'xml_file': str(self.xml_file_path),
            'parsed_at': datetime.now().isoformat()
        }
