"""
Enhanced MTN MobileMoney Parser
Based on detailed message type analysis
Team 11 - Enterprise Web Development
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParsedTransaction:
    """Structured transaction data."""
    amount: float
    currency: str = "RWF"
    transaction_type: str = ""
    category: str = ""
    direction: str = ""  # "credit" or "debit"
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    momo_code: Optional[str] = None
    sender_momo_id: Optional[str] = None
    agent_momo_number: Optional[str] = None
    business_name: Optional[str] = None
    fee: float = 0.0
    new_balance: Optional[float] = None
    transaction_id: Optional[str] = None
    financial_transaction_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    date: Optional[str] = None
    original_message: str = ""
    confidence: float = 0.0

class EnhancedMTNParser:
    """Enhanced parser for MTN MobileMoney messages with detailed categorization."""
    
    def __init__(self):
        self.parsed_count = 0
        self.error_count = 0
        self.errors = []
    
    def parse_message(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse a single MTN MobileMoney message."""
        try:
            # Determine message type and extract data
            message_type = self._identify_message_type(message)
            
            if message_type == "UNKNOWN":
                return None
            
            # Extract data based on message type
            transaction = self._extract_transaction_data(message, message_type, timestamp)
            
            if transaction:
                self.parsed_count += 1
                return transaction
            else:
                self.error_count += 1
                self.errors.append(f"Failed to parse message: {message[:100]}...")
                return None
                
        except Exception as e:
            self.error_count += 1
            error_msg = f"Error parsing message: {str(e)}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return None
    
    def _identify_message_type(self, message: str) -> str:
        """Identify the type of MTN MobileMoney message."""
        message_upper = message.upper()
        
        # 1. INCOMING MONEY (from another person's number)
        if "YOU HAVE RECEIVED" in message_upper:
            return "INCOMING_MONEY"
        
        # 2. AIRTIME PURCHASE (*162*TxId format) - check this first
        elif "*162*TXID:" in message_upper and "AIRTIME" in message_upper:
            return "AIRTIME_PURCHASE"
        
        # 3. DATA BUNDLE PURCHASE (*162*TxId format) - check this first
        elif "*162*TXID:" in message_upper and "BUNDLES AND PACKS" in message_upper:
            return "DATA_BUNDLE_PURCHASE"
        
        # 4. BUSINESS PAYMENT (*162*TxId format with company names) - check this before generic payment
        elif "*162*TXID:" in message_upper and any(company in message_upper for company in ["ONAFRIQ", "ESICIA", "MTN"]):
            return "BUSINESS_PAYMENT"
        
        # 5. PAYMENT TO MOMO CODE (registered to a person)
        elif "TXID:" in message_upper and "YOUR PAYMENT OF" in message_upper and "HAS BEEN COMPLETED" in message_upper:
            return "PAYMENT_MOMO_CODE"
        
        # 3. DEPOSIT FROM MOMO AGENT/MERCHANT (*113*R* with "bank deposit")
        elif "*113*R*" in message_upper and "bank deposit" in message_upper.lower():
            return "DEPOSIT_AGENT"
        
        # 3b. OTHER *113*R* TRANSACTIONS (need to analyze content)
        elif "*113*R*" in message_upper:
            return "DEPOSIT_OTHER"
        
        # 4. MONEY TRANSFER TO MOBILE NUMBER
        elif "*165*S*" in message_upper and "TRANSFERRED TO" in message_upper:
            return "TRANSFER_MOBILE"
        
        
        # 7. DATA BUNDLE PURCHASE (*164* with "Data Bundle")
        elif "*164*S*" in message_upper and "DATA BUNDLE" in message_upper:
            return "DATA_BUNDLE_PURCHASE"
        
        # 8. BUSINESS PAYMENT (*164* without "Data Bundle")
        elif "*164*S*" in message_upper:
            return "BUSINESS_PAYMENT"
        
        
        # 9. CASH WITHDRAWAL
        elif "HAVE VIA AGENT:" in message_upper and "WITHDRAWN" in message_upper:
            return "CASH_WITHDRAWAL"
        
        # 10. TRANSFER (imbank.bank format)
        elif "YOU HAVE TRANSFERRED" in message_upper and "IMBANK.BANK" in message_upper:
            return "TRANSFER_IMBANK"
        
        # 11. PAYMENT (different format)
        elif "YOUR PAYMENT OF" in message_upper and "HAS BEEN COMPLETED" in message_upper and "TXID:" not in message_upper:
            return "PAYMENT_ALTERNATIVE"
        
        # 12. FAILED TRANSACTION
        elif "*143*" in message_upper and ("HAS FAILED" in message_upper or "has failed" in message.lower() or "FAILED AT" in message_upper):
            return "FAILED_TRANSACTION"
        
        # 13. REVERSAL MESSAGE
        elif "REVERSAL HAS BEEN INITIATED" in message_upper or "HAS BEEN REVERSED" in message_upper:
            return "REVERSAL"
        
        # 14. DEPOSIT (different format)
        elif "DEPOSIT RWF" in message_upper and "RECEIVER:" in message_upper:
            return "DEPOSIT_ALTERNATIVE"
        
        else:
            return "UNKNOWN"
    
    def _extract_transaction_data(self, message: str, message_type: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Extract transaction data based on message type."""
        
        if message_type == "INCOMING_MONEY":
            return self._parse_incoming_money(message, timestamp)
        elif message_type == "PAYMENT_MOMO_CODE":
            return self._parse_payment_momo_code(message, timestamp)
        elif message_type == "DEPOSIT_AGENT":
            return self._parse_deposit_agent(message, timestamp)
        elif message_type == "DEPOSIT_OTHER":
            return self._parse_deposit_other(message, timestamp)
        elif message_type == "TRANSFER_MOBILE":
            return self._parse_transfer_mobile(message, timestamp)
        elif message_type == "AIRTIME_PURCHASE":
            return self._parse_airtime_purchase(message, timestamp)
        elif message_type == "DATA_BUNDLE_PURCHASE":
            return self._parse_data_bundle_purchase(message, timestamp)
        elif message_type == "BUSINESS_PAYMENT":
            return self._parse_business_payment(message, timestamp)
        elif message_type == "CASH_WITHDRAWAL":
            return self._parse_cash_withdrawal(message, timestamp)
        elif message_type == "TRANSFER_IMBANK":
            return self._parse_transfer_imbank(message, timestamp)
        elif message_type == "PAYMENT_ALTERNATIVE":
            return self._parse_payment_alternative(message, timestamp)
        elif message_type == "FAILED_TRANSACTION":
            return self._parse_failed_transaction(message, timestamp)
        elif message_type == "REVERSAL":
            return self._parse_reversal(message, timestamp)
        elif message_type == "DEPOSIT_ALTERNATIVE":
            return self._parse_deposit_alternative(message, timestamp)
        else:
            return None
    
    def _parse_incoming_money(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse incoming money message."""
        try:
            # Extract amount
            amount_match = re.search(r'YOU HAVE RECEIVED ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract sender name
            sender_match = re.search(r'FROM ([^(]+) \(', message.upper())
            sender_name = sender_match.group(1).strip() if sender_match else None
            
            # Extract sender phone (masked)
            phone_match = re.search(r'\(([^)]+)\)', message)
            sender_phone = phone_match.group(1) if phone_match else None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:?([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract transaction ID
            tx_id_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="RECEIVE",
                category="TRANSFER_INCOMING",
                direction="credit",
                sender_name=sender_name,
                sender_phone=sender_phone,
                new_balance=new_balance,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing incoming money: {e}")
            return None
    
    def _parse_payment_momo_code(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse payment to momo code message."""
        try:
            # Extract amount
            amount_match = re.search(r'YOUR PAYMENT OF ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract recipient name and momo code
            recipient_match = re.search(r'TO ([^(]+) (\d{5})', message.upper())
            if recipient_match:
                recipient_name = recipient_match.group(1).strip()
                momo_code = recipient_match.group(2)
            else:
                return None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee
            fee_match = re.search(r'FEE WAS (\d+) RWF', message.upper())
            fee = float(fee_match.group(1)) if fee_match else 0.0
            
            # Extract transaction ID
            tx_id_match = re.search(r'TXID: (\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="PAYMENT",
                category="PAYMENT_PERSONAL",
                direction="debit",
                recipient_name=recipient_name,
                momo_code=momo_code,
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing payment momo code: {e}")
            return None
    
    def _parse_deposit_agent(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse deposit from agent message."""
        try:
            # Extract amount - try multiple patterns
            amount_match = None
            patterns = [
                r'a bank deposit of (\d+) rwf',
                r'bank deposit of (\d+) rwf',
                r'deposit of (\d+) rwf'
            ]
            
            for pattern in patterns:
                amount_match = re.search(pattern, message.lower())
                if amount_match:
                    break
            
            if not amount_match:
                print(f"DEBUG: No amount match found in: {message}")
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'your new balance :?(\d+) rwf', message.lower())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract agent momo number
            agent_match = re.search(r'::(\d{12})', message)
            agent_momo_number = agent_match.group(1) if agent_match else None
            
            # Extract date
            date_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.lower())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="DEPOSIT",
                category="DEPOSIT_AGENT",
                direction="credit",
                recipient_name="Self",
                agent_momo_number=agent_momo_number,
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing deposit agent: {e}")
            return None
    
    def _parse_deposit_other(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse other *113*R* transactions by analyzing message content."""
        try:
            message_lower = message.lower()
            
            # Analyze message content to determine specific type
            if "bank deposit" in message_lower:
                # This should have been caught by DEPOSIT_AGENT, but handle it here too
                return self._parse_deposit_agent(message, timestamp)
            elif "cash deposit" in message_lower:
                # Cash deposit from agent
                return self._parse_cash_deposit(message, timestamp)
            elif "transfer" in message_lower:
                # Bank transfer
                return self._parse_bank_transfer(message, timestamp)
            else:
                # Generic deposit - try to extract basic info
                return self._parse_generic_deposit(message, timestamp)
                
        except Exception as e:
            logger.error(f"Error parsing deposit other: {e}")
            return None
    
    def _parse_cash_deposit(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse cash deposit message."""
        try:
            # Extract amount
            amount_match = re.search(r'([\d,]+(?:\.\d{2})?) rwf', message.lower())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'your new balance :?(\d+) rwf', message.lower())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract agent momo number
            agent_match = re.search(r'::(\d{12})', message)
            agent_momo_number = agent_match.group(1) if agent_match else None
            
            # Extract date
            date_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.lower())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="DEPOSIT",
                category="DEPOSIT_CASH",
                direction="credit",
                recipient_name="Self",
                agent_momo_number=agent_momo_number,
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error parsing cash deposit: {e}")
            return None
    
    def _parse_bank_transfer(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse bank transfer message."""
        try:
            # Extract amount
            amount_match = re.search(r'([\d,]+(?:\.\d{2})?) rwf', message.lower())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'your new balance :?(\d+) rwf', message.lower())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract date
            date_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.lower())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="DEPOSIT",
                category="DEPOSIT_BANK_TRANSFER",
                direction="credit",
                recipient_name="Self",
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error parsing bank transfer: {e}")
            return None
    
    def _parse_generic_deposit(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse generic deposit message."""
        try:
            # Extract amount
            amount_match = re.search(r'([\d,]+(?:\.\d{2})?) rwf', message.lower())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'your new balance :?(\d+) rwf', message.lower())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract date
            date_match = re.search(r'at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.lower())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="DEPOSIT",
                category="DEPOSIT_OTHER",
                direction="credit",
                recipient_name="Self",
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.80
            )
            
        except Exception as e:
            logger.error(f"Error parsing generic deposit: {e}")
            return None
    
    def _parse_transfer_mobile(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse transfer to mobile number message."""
        try:
            # Extract amount
            amount_match = re.search(r'\*165\*S\*(\d+) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract recipient name and phone
            recipient_match = re.search(r'TRANSFERRED TO ([^(]+) \(([^)]+)\)', message.upper())
            if recipient_match:
                recipient_name = recipient_match.group(1).strip()
                recipient_phone = recipient_match.group(2)
            else:
                return None
            
            # Extract sender momo ID
            sender_match = re.search(r'FROM (\d{8})', message.upper())
            sender_momo_id = sender_match.group(1) if sender_match else None
            
            # Extract fee
            fee_match = re.search(r'FEE WAS:? (\d+) RWF', message.upper())
            fee = float(fee_match.group(1)) if fee_match else 0.0
            
            # Extract new balance
            balance_match = re.search(r'NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="TRANSFER",
                category="TRANSFER_OUTGOING",
                direction="debit",
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                sender_momo_id=sender_momo_id,
                fee=fee,
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing transfer mobile: {e}")
            return None
    
    def _parse_airtime_purchase(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse airtime purchase message."""
        try:
            # Extract amount
            amount_match = re.search(r'YOUR PAYMENT OF ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee
            fee_match = re.search(r'FEE WAS (\d+) RWF', message.upper())
            fee = float(fee_match.group(1)) if fee_match else 0.0
            
            # Extract transaction ID
            tx_id_match = re.search(r'TXID:(\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="PURCHASE",
                category="AIRTIME",
                direction="debit",
                recipient_name="Self",
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing airtime purchase: {e}")
            return None
    
    def _parse_data_bundle_purchase(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse data bundle purchase message."""
        try:
            # Extract amount - handle both formats
            amount_match = re.search(r'(?:TRANSACTION OF|YOUR PAYMENT OF) ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee - handle both formats
            fee_match = re.search(r'FEE (?:WAS|WAS) ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0.0
            
            # Extract transaction ID - handle both formats
            tx_id_match = re.search(r'TXID:(\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract financial transaction ID
            fin_tx_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            financial_transaction_id = fin_tx_match.group(1) if fin_tx_match else None
            
            # Extract external transaction ID
            ext_tx_match = re.search(r'EXTERNAL TRANSACTION ID: (\d+)', message.upper())
            external_transaction_id = ext_tx_match.group(1) if ext_tx_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="PURCHASE",
                category="DATA_BUNDLE",
                direction="debit",
                recipient_name="Self",
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                financial_transaction_id=financial_transaction_id,
                external_transaction_id=external_transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing data bundle purchase: {e}")
            return None
    
    def _parse_business_payment(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse business payment message."""
        try:
            # Extract amount - handle both formats
            amount_match = re.search(r'(?:TRANSACTION OF|YOUR PAYMENT OF) ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract business name - handle both formats
            business_match = re.search(r'(?:BY ([^O]+) ON YOUR MOMO ACCOUNT|TO ([^W]+) WITH)', message.upper())
            business_name = None
            if business_match:
                business_name = business_match.group(1) or business_match.group(2)
                business_name = business_name.strip() if business_name else None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee - handle both formats
            fee_match = re.search(r'FEE (?:WAS|WAS) ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0.0
            
            # Extract transaction ID - handle both formats
            tx_id_match = re.search(r'TXID:(\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract financial transaction ID
            fin_tx_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            financial_transaction_id = fin_tx_match.group(1) if fin_tx_match else None
            
            # Extract external transaction ID
            ext_tx_match = re.search(r'EXTERNAL TRANSACTION ID: (\d+)', message.upper())
            external_transaction_id = ext_tx_match.group(1) if ext_tx_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="PAYMENT",
                category="PAYMENT_BUSINESS",
                direction="debit",
                business_name=business_name,
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                financial_transaction_id=financial_transaction_id,
                external_transaction_id=external_transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing business payment: {e}")
            return None
    
    def _parse_cash_withdrawal(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse cash withdrawal message."""
        try:
            # Extract amount
            amount_match = re.search(r'WITHDRAWN ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract user name
            name_match = re.search(r'YOU ([^(]+) \(', message.upper())
            user_name = name_match.group(1).strip() if name_match else None
            
            # Extract agent name and phone
            agent_match = re.search(r'AGENT: ([^(]+) \(([^)]+)\)', message.upper())
            agent_name = agent_match.group(1).strip() if agent_match else None
            agent_phone = agent_match.group(2) if agent_match else None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee
            fee_match = re.search(r'FEE PAID:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0.0
            
            # Extract transaction ID
            tx_id_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="WITHDRAWAL",
                category="CASH_WITHDRAWAL",
                direction="debit",
                sender_name=user_name,
                agent_momo_number=agent_phone,
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing cash withdrawal: {e}")
            return None
    
    def _parse_transfer_imbank(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse transfer imbank message."""
        try:
            # Extract amount
            amount_match = re.search(r'TRANSFERRED ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract recipient name and phone
            recipient_match = re.search(r'TO ([^(]+) \(([^)]+)\)', message.upper())
            recipient_name = recipient_match.group(1).strip() if recipient_match else None
            recipient_phone = recipient_match.group(2) if recipient_match else None
            
            # Extract transaction ID
            tx_id_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="TRANSFER",
                category="TRANSFER_OUTGOING",
                direction="debit",
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing transfer imbank: {e}")
            return None
    
    def _parse_payment_alternative(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse alternative payment message format."""
        try:
            # Extract amount
            amount_match = re.search(r'YOUR PAYMENT OF ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract recipient name and phone
            recipient_match = re.search(r'TO ([^(]+) \(([^)]+)\)', message.upper())
            recipient_name = recipient_match.group(1).strip() if recipient_match else None
            recipient_phone = recipient_match.group(2) if recipient_match else None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE:? ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract fee
            fee_match = re.search(r'FEE WAS ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0.0
            
            # Extract transaction ID
            tx_id_match = re.search(r'FINANCIAL TRANSACTION ID: (\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract external transaction ID
            ext_tx_match = re.search(r'EXTERNAL TRANSACTION ID: ([^-]+)', message.upper())
            external_transaction_id = ext_tx_match.group(1).strip() if ext_tx_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="PAYMENT",
                category="PAYMENT_PERSONAL",
                direction="debit",
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                fee=fee,
                new_balance=new_balance,
                transaction_id=transaction_id,
                external_transaction_id=external_transaction_id,
                date=date,
                original_message=message,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error parsing payment alternative: {e}")
            return None
    
    def _parse_failed_transaction(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse failed transaction message."""
        try:
            # Extract amount - handle both "AMOUNT" and "YOUR PAYMENT OF" formats
            amount_match = re.search(r'(?:AMOUNT|YOUR PAYMENT OF) ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract service name - handle both formats
            service_match = re.search(r'(?:FOR ([^W]+) WITH|TO ([^(]+))', message.upper())
            service_name = None
            if service_match:
                service_name = service_match.group(1) or service_match.group(2)
                service_name = service_name.strip() if service_name else None
            
            # Extract transaction ID
            tx_id_match = re.search(r'TXID:(\d+)', message.upper())
            transaction_id = tx_id_match.group(1) if tx_id_match else None
            
            # Extract date
            date_match = re.search(r'(?:FAILED AT|has failed at) (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="FAILED",
                category="FAILED_TRANSACTION",
                direction="debit",
                recipient_name=service_name,
                transaction_id=transaction_id,
                date=date,
                original_message=message,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error parsing failed transaction: {e}")
            return None
    
    def _parse_reversal(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse reversal message."""
        try:
            # Extract amount
            amount_match = re.search(r'WITH ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract recipient name and phone
            recipient_match = re.search(r'TO ([^(]+) \(([^)]+)\)', message.upper())
            recipient_name = recipient_match.group(1).strip() if recipient_match else None
            recipient_phone = recipient_match.group(2) if recipient_match else None
            
            # Extract new balance
            balance_match = re.search(r'YOUR NEW BALANCE IS ([\d,]+(?:\.\d{2})?) RWF', message.upper())
            new_balance = float(balance_match.group(1).replace(',', '')) if balance_match else None
            
            # Extract date
            date_match = re.search(r'AT (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', message.upper())
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="REVERSAL",
                category="REVERSAL",
                direction="credit",
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                new_balance=new_balance,
                date=date,
                original_message=message,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error parsing reversal: {e}")
            return None
    
    def _parse_deposit_alternative(self, message: str, timestamp: Optional[str] = None) -> Optional[ParsedTransaction]:
        """Parse alternative deposit message format."""
        try:
            # Extract amount
            amount_match = re.search(r'DEPOSIT RWF ([\d,]+(?:\.\d{2})?)', message.upper())
            if not amount_match:
                return None
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract receiver phone
            receiver_match = re.search(r'RECEIVER: (\d+)', message.upper())
            receiver_phone = receiver_match.group(1) if receiver_match else None
            
            # Extract date from message
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
            date = date_match.group(1) if date_match else timestamp
            
            return ParsedTransaction(
                amount=amount,
                transaction_type="DEPOSIT",
                category="DEPOSIT_ALTERNATIVE",
                direction="credit",
                recipient_name="Self",
                recipient_phone=receiver_phone,
                date=date,
                original_message=message,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Error parsing deposit alternative: {e}")
            return None
    
    def get_parsing_summary(self) -> Dict[str, Any]:
        """Get parsing summary statistics."""
        return {
            'total_processed': self.parsed_count + self.error_count,
            'total_parsed': self.parsed_count,
            'parsing_errors': self.error_count,
            'error_rate': self.error_count / (self.parsed_count + self.error_count) if (self.parsed_count + self.error_count) > 0 else 0,
            'errors': self.errors[:10],  # First 10 errors
            'parsed_at': datetime.now().isoformat()
        }
