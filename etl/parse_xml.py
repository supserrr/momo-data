"""
XML Parser for MoMo SMS Data
Team 11 - Enterprise Web Development
"""

import xml.etree.ElementTree as ET
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from .config import XML_INPUT_FILE

logger = logging.getLogger(__name__)

class XMLParser:
    """Parses XML files with MoMo SMS transaction data."""
    
    def __init__(self, xml_file: Path = XML_INPUT_FILE):
        """Initialize XML parser with file path."""
        self.xml_file = Path(xml_file)
        self.parsed_count = 0
        self.error_count = 0
        self.errors = []
        self.transactions = []
    
    def parse(self) -> List[Dict[str, Any]]:
        """Parse XML file and extract transaction data."""
        if not self.xml_file.exists():
            logger.error(f"XML file not found: {self.xml_file}")
            raise FileNotFoundError(f"XML file not found: {self.xml_file}")
        
        try:
            logger.info(f"Parsing XML file: {self.xml_file}")
            
            # Parse XML file
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            
            # Extract SMS elements
            sms_elements = root.findall('.//sms')
            logger.info(f"Found {len(sms_elements)} SMS elements")
            
            # Process each SMS
            for i, sms in enumerate(sms_elements):
                try:
                    transaction = self._parse_sms_element(sms, i)
                    if transaction:
                        self.transactions.append(transaction)
                        self.parsed_count += 1
                    else:
                        self.error_count += 1
                        self.errors.append(f"SMS {i}: Failed to parse")
                except Exception as e:
                    self.error_count += 1
                    error_msg = f"SMS {i}: {str(e)}"
                    self.errors.append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Parsed {self.parsed_count} transactions, {self.error_count} errors")
            return self.transactions
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing XML file: {e}")
            raise
    
    def _parse_sms_element(self, sms: ET.Element, index: int) -> Optional[Dict[str, Any]]:
        """Parse individual SMS element and return transaction data."""
        try:
            # Extract basic SMS attributes
            body = sms.get('body', '')
            address = sms.get('address', '')
            date = sms.get('date', '')
            readable_date = sms.get('readable_date', '')
            
            # Skip if not a MoMo SMS
            if not self._is_momo_sms(body, address):
                return None
            
            # Parse transaction data from SMS body
            transaction_data = self._extract_transaction_data(body)
            if not transaction_data:
                return None
            
            # Create transaction record
            transaction = {
                'amount': transaction_data.get('amount'),
                'phone': transaction_data.get('phone'),
                'date': self._parse_date(date, readable_date),
                'reference': transaction_data.get('reference'),
                'type': transaction_data.get('type'),
                'status': transaction_data.get('status'),
                'recipient_name': transaction_data.get('recipient_name'),
                'personal_id': transaction_data.get('personal_id'),
                'original_data': body,
                'raw_data': body,
                'xml_tag': 'sms',
                'xml_attributes': {
                    'address': address,
                    'date': date,
                    'readable_date': readable_date,
                    'protocol': sms.get('protocol'),
                    'type': sms.get('type'),
                    'status': sms.get('status')
                },
                'parsed_at': datetime.now().isoformat()
            }
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error parsing SMS element {index}: {e}")
            return None
    
    def _is_momo_sms(self, body: str, address: str) -> bool:
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
    
    def _extract_transaction_data(self, body: str) -> Optional[Dict[str, Any]]:
        """Extract transaction data from SMS body."""
        try:
            data = {}
            
            # Extract amount
            amount = self._extract_amount(body)
            if amount is None:
                return None
            data['amount'] = amount
            
            # Extract phone number
            phone = self._extract_phone(body)
            data['phone'] = phone
            
            # Extract reference/transaction ID
            reference = self._extract_reference(body)
            data['reference'] = reference
            
            # Determine transaction type
            transaction_type = self._determine_transaction_type(body)
            data['type'] = transaction_type
            
            # Determine status
            status = self._determine_status(body)
            data['status'] = status
            
            # Extract recipient name
            recipient_name = self._extract_recipient_name(body)
            data['recipient_name'] = recipient_name
            
            # Extract personal ID
            personal_id = self._extract_personal_id(body)
            data['personal_id'] = personal_id
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting transaction data: {e}")
            return None
    
    def _extract_amount(self, body: str) -> Optional[float]:
        """Extract amount from SMS text."""
        try:
            # Look for amount patterns - more comprehensive patterns
            amount_patterns = [
                # Standard RWF/UGX patterns
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*RWF',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*UGX',
                r'(\d+(?:\.\d{2})?)\s*RWF',
                r'(\d+(?:\.\d{2})?)\s*UGX',
                
                # Payment patterns
                r'payment of\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'Your payment of\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'paid\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                
                # Transfer patterns
                r'transferred\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'transfer of\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*RWF transferred',
                
                # Deposit patterns
                r'deposit of\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'received\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*RWF has been added',
                
                # Balance patterns (for queries)
                r'balance:\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'new balance:\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'NEW BALANCE\s*:\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                
                # Fee patterns
                r'Fee was\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'fee\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                
                # General number patterns (fallback)
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*RWF',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*UGX'
            ]
            
            for pattern in amount_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    # Only return if amount is reasonable (not 0 or negative)
                    if amount > 0:
                        return amount
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _extract_phone(self, body: str) -> Optional[str]:
        """Extract phone number from SMS text."""
        try:
            # Phone number patterns
            phone_patterns = [
                r'(\+?25[06]\d{9})',
                r'(\+?25[06]\d{8})',
                r'(0\d{9})',
                r'(\d{9,10})'
            ]
            
            for pattern in phone_patterns:
                match = re.search(pattern, body)
                if match:
                    phone = match.group(1)
                    # Normalize phone number
                    if phone.startswith('0'):
                        return '+250' + phone[1:]
                    elif phone.startswith('250'):
                        return '+' + phone
                    elif phone.startswith('256'):
                        return '+' + phone  # Keep Uganda numbers as-is
                    else:
                        return phone
            
            return None
            
        except Exception:
            return None
    
    def _extract_reference(self, body: str) -> Optional[str]:
        """Extract transaction reference from SMS text."""
        try:
            # Reference patterns
            ref_patterns = [
                r'TxId:\s*(\d+)',
                r'Transaction Id:\s*(\d+)',
                r'Financial Transaction Id:\s*(\d+)',
                r'External Transaction Id:\s*(\d+)',
                r'ID:\s*(\d+)',
                r'Ref:\s*(\w+)',
                r'Reference:\s*(\w+)',
                r'Financial Transaction Id:\s*(\w+)',
                r'Transaction Id:\s*(\w+)'
            ]
            
            for pattern in ref_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _determine_transaction_type(self, body: str) -> str:
        """Determine transaction type from SMS text."""
        body_lower = body.lower()
        
        if any(word in body_lower for word in ['deposit', 'received', 'added to your account']):
            return 'DEPOSIT'
        elif any(word in body_lower for word in ['withdraw', 'cashout', 'withdrawn']):
            return 'WITHDRAWAL'
        elif any(word in body_lower for word in ['transfer', 'transferred']):
            return 'TRANSFER'
        elif any(word in body_lower for word in ['payment', 'paid', 'bill']):
            return 'PAYMENT'
        elif any(word in body_lower for word in ['balance', 'query', 'statement']):
            return 'QUERY'
        elif any(word in body_lower for word in ['airtime', 'credit', 'topup']):
            return 'AIRTIME'
        elif any(word in body_lower for word in ['data bundle', 'data_bundle', 'internet']):
            return 'DATA_BUNDLE'
        else:
            return 'OTHER'
    
    def _determine_status(self, body: str) -> str:
        """Determine transaction status from SMS text."""
        body_lower = body.lower()
        
        if any(word in body_lower for word in ['completed', 'successful', 'success']):
            return 'SUCCESS'
        elif any(word in body_lower for word in ['failed', 'error', 'unsuccessful']):
            return 'FAILED'
        elif any(word in body_lower for word in ['pending', 'processing']):
            return 'PENDING'
        else:
            return 'SUCCESS'  # Default to success for MoMo SMS
    
    def _extract_recipient_name(self, body: str) -> Optional[str]:
        """Extract recipient name from SMS text."""
        try:
            # Recipient name patterns
            name_patterns = [
                r'transferred to\s+([^(]+?)\s*\(',
                r'payment to\s+([^(]+?)\s*\(',
                r'received from\s+([^(]+?)\s*\(',
                r'from\s+([^(]+?)\s*\(',
                r'to\s+([^(]+?)\s*\('
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up name
                    name = re.sub(r'\d+', '', name).strip()
                    if name and len(name) > 1:
                        return name
            
            return None
            
        except Exception:
            return None
    
    def _extract_personal_id(self, body: str) -> Optional[str]:
        """Extract personal ID from SMS text."""
        try:
            # Personal ID patterns
            id_patterns = [
                r'from\s+(\d+)',
                r'to\s+(\d+)',
                r'\((\d+)\)',
                r'ID:\s*(\d+)',
                r'Account:\s*(\d+)'
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _parse_date(self, timestamp: str, readable_date: str) -> Optional[str]:
        """Parse date from timestamp or readable date string."""
        try:
            if timestamp:
                # Convert Unix timestamp to ISO format
                timestamp_int = int(timestamp)
                dt = datetime.fromtimestamp(timestamp_int / 1000)  # Convert from milliseconds
                return dt.isoformat()
            elif readable_date:
                # Parse readable date
                from dateutil import parser
                dt = parser.parse(readable_date)
                return dt.isoformat()
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Error parsing date: {e}")
            return None
    
    def get_parsing_summary(self) -> Dict[str, Any]:
        """Get parsing summary stats."""
        return {
            'total_processed': self.parsed_count + self.error_count,
            'total_parsed': self.parsed_count,
            'parsing_errors': self.error_count,
            'error_rate': self.error_count / (self.parsed_count + self.error_count) if (self.parsed_count + self.error_count) > 0 else 0,
            'errors': self.errors[:10],  # First 10 errors
            'parsed_at': datetime.now().isoformat()
        }
    
    def get_transaction_count(self) -> int:
        """Get count of parsed transactions."""
        return len(self.transactions)
    
    def get_errors(self) -> List[str]:
        """Get parsing errors list."""
        return self.errors.copy()
