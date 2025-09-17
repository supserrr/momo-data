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
            # This parser is specifically designed for SMS backup XML files
            transactions = []
            
            # Look for SMS elements that contain mobile money transactions
            for sms_elem in root.findall('.//sms'):
                transaction = self._extract_sms_transaction(sms_elem)
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
    
    def _extract_sms_transaction(self, sms_elem) -> Optional[Dict[str, Any]]:
        """Extract transaction data from SMS element."""
        try:
            # Get SMS attributes
            body = sms_elem.get('body', '')
            date = sms_elem.get('date', '')
            readable_date = sms_elem.get('readable_date', '')
            address = sms_elem.get('address', '')
            
            # Only process SMS from M-Money (mobile money service)
            if 'M-Money' not in address and 'mobile' not in body.lower():
                return None
            
            # Parse the SMS body for transaction information
            transaction = self._parse_sms_body(body)
            
            if not transaction:
                return None
            
            # Add SMS metadata
            transaction['raw_data'] = body
            transaction['xml_tag'] = 'sms'
            transaction['xml_attributes'] = dict(sms_elem.attrib)
            transaction['original_data'] = body
            
            # Parse date from SMS attributes
            if date:
                try:
                    # Convert Unix timestamp to ISO format
                    timestamp = int(date) / 1000  # Convert from milliseconds
                    parsed_date = datetime.fromtimestamp(timestamp)
                    transaction['date'] = parsed_date.isoformat()
                except (ValueError, OSError):
                    transaction['date'] = readable_date
            
            # Validate transaction
            if self._validate_transaction(transaction):
                return transaction
            else:
                logger.warning(f"Invalid SMS transaction: {transaction}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting SMS transaction: {e}")
            return None

    def _parse_sms_body(self, body: str) -> Optional[Dict[str, Any]]:
        """Parse SMS body to extract transaction information."""
        if not body:
            return None
        
        import re
        
        transaction = {}
        
        # Amount patterns (RWF currency) - try multiple patterns
        amount_patterns = [
            # Patterns for *165*S* format (transfers)
            r'\*165\*S\*(\d{1,3}(?:,\d{3})*)\s*RWF',  # *165*S*4000 RWF
            r'\*165\*S\*(\d+)\s*RWF',  # *165*S*4000 RWF (no commas)
            
            # Patterns for *113*R* format (deposits)
            r'\*113\*R\*.*?deposit of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # *113*R*A bank deposit of 20000 RWF
            r'\*113\*R\*.*?deposit of\s+(\d+)\s*RWF',  # *113*R*A bank deposit of 20000 RWF (no commas)
            
            # Patterns for *162* format (payments)
            r'\*162\*.*?payment of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # *162*TxId:...*S*Your payment of 3000 RWF
            r'\*162\*.*?payment of\s+(\d+)\s*RWF',  # *162*TxId:...*S*Your payment of 3000 RWF (no commas)
            
            # Patterns for *164* format (data bundles)
            r'\*164\*.*?transaction of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # *164*S*Y'ello,A transaction of 10000 RWF
            r'\*164\*.*?transaction of\s+(\d+)\s*RWF',  # *164*S*Y'ello,A transaction of 10000 RWF (no commas)
            
            # General patterns - more comprehensive
            r'received\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # received 2000 RWF
            r'payment of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # payment of 1,000 RWF
            r'transferred\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # transferred 1000 RWF
            r'deposit of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # deposit of 40000 RWF
            r'withdrawn\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # withdrawn 20000 RWF
            r'You have received\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # You have received 2000 RWF
            r'You have transferred\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # You have transferred 10000 RWF
            r'Your payment of\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # Your payment of 8000 RWF
            r'with\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # with 3000 RWF (for reversals)
            r'amount\s+(\d{1,3}(?:,\d{3})*)\s*RWF',  # amount 5000 RWF
            r'DEPOSIT\s+RWF\s+(\d{1,3}(?:,\d{3})*)',  # DEPOSIT RWF 25000
            r'(\d{1,3}(?:,\d{3})*)\s*RWF',  # 1,000 RWF (general)
            r'(\d+)\s*RWF',  # 1000 RWF (general, no commas)
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, body)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    transaction['amount'] = amount
                    break
                except ValueError:
                    continue
        
        # Phone number patterns
        phone_patterns = [
            r'(\+?250\d{9})',  # +250XXXXXXXXX
            r'(\+?256\d{9})',  # +256XXXXXXXXX
            r'(\d{9})',        # XXXXXXXXX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, body)
            if match:
                phone = match.group(1)
                # Normalize phone number
                if phone.startswith('250'):
                    phone = '+' + phone
                elif phone.startswith('256'):
                    phone = '+' + phone
                elif len(phone) == 9:
                    phone = '+250' + phone
                transaction['phone'] = phone
                break
        
        # Transaction type detection
        if 'received' in body.lower() and 'from' in body.lower():
            transaction['type'] = 'DEPOSIT'
            transaction['status'] = 'SUCCESS'
        elif 'payment of' in body.lower() and 'to' in body.lower():
            if 'airtime' in body.lower():
                transaction['type'] = 'AIRTIME'
            else:
                transaction['type'] = 'PAYMENT'
            transaction['status'] = 'SUCCESS'
        elif 'transferred to' in body.lower():
            transaction['type'] = 'TRANSFER'
            transaction['status'] = 'SUCCESS'
        elif 'bank deposit' in body.lower():
            transaction['type'] = 'DEPOSIT'
            transaction['status'] = 'SUCCESS'
        elif 'withdrawal' in body.lower() or 'withdraw' in body.lower():
            transaction['type'] = 'WITHDRAWAL'
            transaction['status'] = 'SUCCESS'
        else:
            transaction['type'] = 'UNKNOWN'
            transaction['status'] = 'SUCCESS'
        
        # Extract fee
        fee_match = re.search(r'Fee was[:\s]*(\d+)\s*RWF', body)
        if fee_match:
            transaction['fee'] = float(fee_match.group(1))
        
        # Extract balance
        balance_match = re.search(r'balance[:\s]*(\d{1,3}(?:,\d{3})*)\s*RWF', body, re.IGNORECASE)
        if balance_match:
            transaction['balance'] = float(balance_match.group(1).replace(',', ''))
        
        # Extract transaction ID
        txid_match = re.search(r'TxId[:\s]*(\d+)', body)
        if txid_match:
            transaction['reference'] = txid_match.group(1)
        
        # Check for failed transactions
        if any(word in body.lower() for word in ['failed', 'error', 'unsuccessful', 'declined']):
            transaction['status'] = 'FAILED'
        
        return transaction

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
