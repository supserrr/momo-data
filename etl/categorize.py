"""
Transaction Categorization System
Team 11 - Enterprise Web Development
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import TRANSACTION_CATEGORIES

logger = logging.getLogger(__name__)

class TransactionCategorizer:
    """Categorize transactions based on content analysis."""
    
    def __init__(self):
        self.categorized_count = 0
        self.uncategorized_count = 0
        self.category_stats = {}
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of cleaned transaction dictionaries
            
        Returns:
            List of transactions with added category information
        """
        categorized_transactions = []
        
        for transaction in transactions:
            try:
                categorized = self.categorize_transaction(transaction)
                categorized_transactions.append(categorized)
                
                # Update statistics
                category = categorized.get('category', 'UNKNOWN')
                self.category_stats[category] = self.category_stats.get(category, 0) + 1
                
                if category != 'UNKNOWN':
                    self.categorized_count += 1
                else:
                    self.uncategorized_count += 1
                    
            except Exception as e:
                logger.error(f"Error categorizing transaction: {e}")
                # Add transaction with unknown category
                transaction['category'] = 'UNKNOWN'
                transaction['category_confidence'] = 0.0
                categorized_transactions.append(transaction)
                self.uncategorized_count += 1
        
        logger.info(f"Categorized {self.categorized_count} transactions, {self.uncategorized_count} uncategorized")
        return categorized_transactions
    
    def categorize_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize a single transaction.
        
        Args:
            transaction: Cleaned transaction dictionary
            
        Returns:
            Transaction with added category information
        """
        categorized = transaction.copy()
        
        # Get category and confidence
        category, confidence = self._determine_category(transaction)
        
        categorized['category'] = category
        categorized['category_confidence'] = confidence
        categorized['categorized_at'] = datetime.now().isoformat()
        
        return categorized
    
    def _determine_category(self, transaction: Dict[str, Any]) -> tuple:
        """
        Determine transaction category and confidence.
        Uses keyword matching and heuristics to classify transactions.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Tuple of (category, confidence_score)
        """
        # Combine all text fields for analysis
        text_fields = [
            transaction.get('type', ''),
            transaction.get('status', ''),
            transaction.get('reference', ''),
            transaction.get('original_data', ''),
            transaction.get('raw_data', '')
        ]
        
        combined_text = ' '.join(str(field) for field in text_fields if field).lower()
        
        # Rule-based categorization using keyword matching
        category_scores = {}
        
        for category, keywords in TRANSACTION_CATEGORIES.items():
            score = self._calculate_category_score(combined_text, keywords)
            if score > 0:
                category_scores[category] = score
        
        # Amount-based heuristics
        amount = transaction.get('amount', 0)
        amount_category, amount_confidence = self._categorize_by_amount(amount, combined_text)
        if amount_category and amount_confidence > 0:
            category_scores[amount_category] = category_scores.get(amount_category, 0) + amount_confidence
        
        # Phone number analysis
        phone_category, phone_confidence = self._categorize_by_phone(transaction.get('phone', ''), combined_text)
        if phone_category and phone_confidence > 0:
            category_scores[phone_category] = category_scores.get(phone_category, 0) + phone_confidence
        
        # Select best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[best_category] / 2.0, 1.0)  # Normalize confidence
            return best_category, confidence
        else:
            return 'UNKNOWN', 0.0
    
    def _calculate_category_score(self, text: str, keywords: List[str]) -> float:
        """Calculate category score based on keyword matching."""
        if not text or not keywords:
            return 0.0
        
        score = 0.0
        text_lower = text.lower()
        
        for keyword in keywords:
            # Exact match
            if keyword in text_lower:
                score += 1.0
            
            # Partial match (word boundary)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                score += 0.5
            
            # Fuzzy match (contains)
            if keyword in text_lower:
                score += 0.3
        
        return score
    
    def _categorize_by_amount(self, amount: float, text: str) -> tuple:
        """Categorize based on amount patterns."""
        if not amount or amount <= 0:
            return None, 0.0
        
        text_lower = text.lower()
        
        # Small amounts might be queries or fees
        if amount < 1000:
            if any(word in text_lower for word in ['balance', 'query', 'statement', 'check']):
                return 'QUERY', 0.8
            return 'OTHER', 0.3
        
        # Medium amounts are typically transactions
        elif amount < 100000:
            if any(word in text_lower for word in ['deposit', 'credit', 'receive']):
                return 'DEPOSIT', 0.6
            elif any(word in text_lower for word in ['withdraw', 'debit', 'send']):
                return 'WITHDRAWAL', 0.6
            else:
                return 'TRANSFER', 0.4
        
        # Large amounts are likely transfers or payments
        else:
            if any(word in text_lower for word in ['payment', 'bill', 'merchant', 'utility']):
                return 'PAYMENT', 0.7
            else:
                return 'TRANSFER', 0.5
    
    def _categorize_by_phone(self, phone: str, text: str) -> tuple:
        """Categorize based on phone number patterns."""
        if not phone:
            return None, 0.0
        
        text_lower = text.lower()
        
        # Check for merchant/service numbers (often start with specific patterns)
        if phone.startswith('+256700') or phone.startswith('+256701'):
            if any(word in text_lower for word in ['payment', 'bill', 'merchant']):
                return 'PAYMENT', 0.6
        
        # Check for bank numbers
        if phone.startswith('+256700') and any(word in text_lower for word in ['bank', 'account']):
            return 'TRANSFER', 0.5
        
        return None, 0.0
    
    def _categorize_by_time_pattern(self, date_str: str, text: str) -> tuple:
        """Categorize based on time patterns."""
        if not date_str:
            return None, 0.0
        
        try:
            from dateutil import parser
            parsed_date = parser.parse(date_str)
            hour = parsed_date.hour
            
            # Business hours transactions might be different
            if 9 <= hour <= 17:
                return 'TRANSFER', 0.2
            else:
                return 'DEPOSIT', 0.2
                
        except:
            return None, 0.0
    
    def get_categorization_summary(self) -> Dict[str, Any]:
        """Get summary of categorization results."""
        total = self.categorized_count + self.uncategorized_count
        
        return {
            'total_transactions': total,
            'categorized': self.categorized_count,
            'uncategorized': self.uncategorized_count,
            'categorization_rate': self.categorized_count / total if total > 0 else 0,
            'category_distribution': self.category_stats,
            'categorized_at': datetime.now().isoformat()
        }
    
    def get_category_rules(self) -> Dict[str, List[str]]:
        """Get the current categorization rules."""
        return TRANSACTION_CATEGORIES.copy()
    
    def add_custom_rule(self, category: str, keywords: List[str]) -> None:
        """Add custom categorization rule."""
        if category not in TRANSACTION_CATEGORIES:
            TRANSACTION_CATEGORIES[category] = []
        
        TRANSACTION_CATEGORIES[category].extend(keywords)
        logger.info(f"Added custom rule for category '{category}' with keywords: {keywords}")
    
    def update_category_rule(self, category: str, keywords: List[str]) -> None:
        """Update existing categorization rule."""
        TRANSACTION_CATEGORIES[category] = keywords
        logger.info(f"Updated rule for category '{category}' with keywords: {keywords}")
