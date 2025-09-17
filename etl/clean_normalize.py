"""
Data Cleaning and Normalization
Team 11 - Enterprise Web Development
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dateutil import parser
from .config import (
    MAX_AMOUNT, MIN_AMOUNT, MAX_PHONE_LENGTH, MIN_PHONE_LENGTH,
    PHONE_PATTERNS, DATE_FORMATS
)

logger = logging.getLogger(__name__)

class DataCleaner:
    """Clean and normalize transaction data."""
    
    def __init__(self):
        self.cleaned_count = 0
        self.error_count = 0
        self.errors = []
    
    def clean_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize a list of transactions.
        
        Args:
            transactions: List of raw transaction dictionaries
            
        Returns:
            List of cleaned transaction dictionaries
        """
        cleaned_transactions = []
        
        for i, transaction in enumerate(transactions):
            try:
                cleaned = self.clean_transaction(transaction)
                if cleaned:
                    cleaned_transactions.append(cleaned)
                    self.cleaned_count += 1
                else:
                    self.error_count += 1
                    self.errors.append(f"Transaction {i}: Failed to clean")
            except Exception as e:
                self.error_count += 1
                self.errors.append(f"Transaction {i}: {str(e)}")
                logger.error(f"Error cleaning transaction {i}: {e}")
        
        logger.info(f"Cleaned {self.cleaned_count} transactions, {self.error_count} errors")
        return cleaned_transactions
    
    def clean_transaction(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean and normalize a single transaction.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Cleaned transaction dictionary or None if cleaning failed
        """
        try:
            cleaned = transaction.copy()
            
            # Clean amount
            cleaned['amount'] = self.clean_amount(transaction.get('amount'))
            if cleaned['amount'] is None:
                return None
            
            # Clean phone number
            cleaned['phone'] = self.clean_phone(transaction.get('phone'))
            if cleaned['phone'] is None:
                return None
            
            # Clean date
            cleaned['date'] = self.clean_date(transaction.get('date'))
            
            # Clean reference
            cleaned['reference'] = self.clean_reference(transaction.get('reference'))
            
            # Clean type/status
            cleaned['type'] = self.clean_type(transaction.get('type'))
            cleaned['status'] = self.clean_status(transaction.get('status'))
            
            # Add metadata
            cleaned['cleaned_at'] = datetime.now().isoformat()
            cleaned['original_data'] = transaction.get('raw_data', '')
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning transaction: {e}")
            return None
    
    def clean_amount(self, amount: Any) -> Optional[float]:
        """
        Clean and validate amount.
        
        Args:
            amount: Raw amount value
            
        Returns:
            Cleaned amount as float or None if invalid
        """
        if amount is None:
            return None
        
        try:
            # Convert to string and clean
            if isinstance(amount, (int, float)):
                amount_str = str(amount)
            else:
                amount_str = str(amount).strip()
            
            # Remove currency symbols and separators
            cleaned = re.sub(r'[^\d.-]', '', amount_str)
            
            # Handle multiple decimal points
            if cleaned.count('.') > 1:
                parts = cleaned.split('.')
                cleaned = '.'.join(parts[:-1]) + parts[-1]
            
            # Convert to float
            amount_float = float(cleaned)
            
            # Validate range
            if MIN_AMOUNT <= amount_float <= MAX_AMOUNT:
                return round(amount_float, 2)
            else:
                logger.warning(f"Amount {amount_float} outside valid range [{MIN_AMOUNT}, {MAX_AMOUNT}]")
                return None
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid amount format: {amount} - {e}")
            return None
    
    def clean_phone(self, phone: Any) -> Optional[str]:
        """
        Clean and normalize phone number.
        
        Args:
            phone: Raw phone number
            
        Returns:
            Cleaned phone number or None if invalid
        """
        if phone is None:
            return None
        
        try:
            # Convert to string and clean
            phone_str = str(phone).strip()
            
            # Remove common separators
            cleaned = re.sub(r'[^\d+]', '', phone_str)
            
            # Normalize Uganda phone numbers
            if cleaned.startswith('+256'):
                # +256XXXXXXXXX format
                if len(cleaned) == 13:
                    return cleaned
            elif cleaned.startswith('256'):
                # 256XXXXXXXXX format
                if len(cleaned) == 12:
                    return '+' + cleaned
            elif cleaned.startswith('0'):
                # 0XXXXXXXXX format
                if len(cleaned) == 10:
                    return '+256' + cleaned[1:]
            
            # Try to extract phone number from text
            phone_match = re.search(r'(\+?256\d{9}|0\d{9})', phone_str)
            if phone_match:
                return self.clean_phone(phone_match.group(1))
            
            # Validate length
            if MIN_PHONE_LENGTH <= len(cleaned) <= MAX_PHONE_LENGTH:
                return cleaned
            
            logger.warning(f"Invalid phone number format: {phone}")
            return None
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid phone format: {phone} - {e}")
            return None
    
    def clean_date(self, date: Any) -> Optional[str]:
        """
        Clean and normalize date.
        
        Args:
            date: Raw date value
            
        Returns:
            ISO formatted date string or None if invalid
        """
        if date is None:
            return None
        
        try:
            # Convert to string
            date_str = str(date).strip()
            
            if not date_str:
                return None
            
            # Try parsing with dateutil (most flexible)
            try:
                parsed_date = parser.parse(date_str)
                return parsed_date.isoformat()
            except:
                pass
            
            # Try specific formats
            for fmt in DATE_FORMATS:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            # Try to extract date from text
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
                r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    return self.clean_date(match.group(1))
            
            logger.warning(f"Could not parse date: {date}")
            return date_str  # Return as-is if parsing fails
            
        except Exception as e:
            logger.warning(f"Error cleaning date: {date} - {e}")
            return None
    
    def clean_reference(self, reference: Any) -> Optional[str]:
        """
        Clean reference number.
        
        Args:
            reference: Raw reference value
            
        Returns:
            Cleaned reference string or None if invalid
        """
        if reference is None:
            return None
        
        try:
            ref_str = str(reference).strip()
            
            # Remove extra whitespace and normalize
            cleaned = re.sub(r'\s+', ' ', ref_str)
            
            # Basic validation - should not be empty
            if cleaned:
                return cleaned
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Error cleaning reference: {reference} - {e}")
            return None
    
    def clean_type(self, transaction_type: Any) -> str:
        """
        Clean transaction type.
        
        Args:
            transaction_type: Raw transaction type
            
        Returns:
            Cleaned transaction type
        """
        if transaction_type is None:
            return 'UNKNOWN'
        
        try:
            type_str = str(transaction_type).strip().upper()
            
            # Map common variations
            type_mapping = {
                'DEP': 'DEPOSIT',
                'WIT': 'WITHDRAWAL',
                'TRF': 'TRANSFER',
                'PAY': 'PAYMENT',
                'BAL': 'QUERY',
                'STMT': 'QUERY',
                'QRY': 'QUERY',
                'UNK': 'UNKNOWN',
                'OTH': 'OTHER'
            }
            
            return type_mapping.get(type_str, type_str)
            
        except Exception as e:
            logger.warning(f"Error cleaning transaction type: {transaction_type} - {e}")
            return 'UNKNOWN'
    
    def clean_status(self, status: Any) -> str:
        """
        Clean transaction status.
        
        Args:
            status: Raw transaction status
            
        Returns:
            Cleaned transaction status
        """
        if status is None:
            return 'UNKNOWN'
        
        try:
            status_str = str(status).strip().upper()
            
            # Map common variations
            status_mapping = {
                'SUCC': 'SUCCESS',
                'FAIL': 'FAILED',
                'PEND': 'PENDING',
                'PROC': 'PROCESSING',
                'COMP': 'COMPLETED',
                'CANC': 'CANCELLED',
                'REJ': 'REJECTED',
                'TIMEOUT': 'FAILED',
                'ERROR': 'FAILED'
            }
            
            return status_mapping.get(status_str, status_str)
            
        except Exception as e:
            logger.warning(f"Error cleaning status: {status} - {e}")
            return 'UNKNOWN'
    
    def get_cleaning_summary(self) -> Dict[str, Any]:
        """Get summary of cleaning results."""
        return {
            'total_processed': self.cleaned_count + self.error_count,
            'successfully_cleaned': self.cleaned_count,
            'cleaning_errors': self.error_count,
            'error_rate': self.error_count / (self.cleaned_count + self.error_count) if (self.cleaned_count + self.error_count) > 0 else 0,
            'errors': self.errors[:10],  # First 10 errors
            'cleaned_at': datetime.now().isoformat()
        }
