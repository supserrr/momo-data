"""
MySQL Database Operations for MoMo Data
Team 11 - Enterprise Web Development
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from .config import DASHBOARD_JSON_FILE

logger = logging.getLogger(__name__)

class MySQLDatabaseLoader:
    """Loads categorized transactions into MySQL database with normalized schema."""
    
    def __init__(self, host: str = 'localhost', port: int = 3306, 
                 database: str = 'momo_sms_processing', user: str = 'root', 
                 password: str = ''):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.unix_socket = '/tmp/mysql.sock'
        self.connection = None
        self.loaded_count = 0
        self.error_count = 0
        self.errors = []
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self):
        """Connect to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                unix_socket=self.unix_socket,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            
            if self.connection.is_connected():
                logger.info(f"Connected to MySQL database: {self.database}")
                
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL database connection closed")
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Load transactions into normalized MySQL database."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            for i, transaction in enumerate(transactions):
                try:
                    transaction_id = self._process_transaction(cursor, transaction)
                    if transaction_id:
                        self.loaded_count += 1
                    else:
                        # Transaction was a duplicate, count as skipped
                        logger.debug(f"Transaction {i}: Skipped duplicate (external_transaction_id: {transaction.get('external_transaction_id')})")
                except Exception as e:
                    self.error_count += 1
                    error_msg = f"Transaction {i}: {str(e)}"
                    self.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Log ETL process
            self._log_etl_process(cursor, len(transactions))
            
            self.connection.commit()
            
            logger.info(f"Loaded {self.loaded_count} transactions, {self.error_count} errors")
            
            return self.get_loading_summary()
            
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def _process_transaction(self, cursor, transaction: Dict[str, Any]) -> Optional[int]:
        """Process a single transaction with normalized schema."""
        try:
            # Get or create users
            sender_user_id = self._get_or_create_user(cursor, transaction.get('phone'))
            receiver_user_id = self._get_or_create_user(cursor, transaction.get('recipient_phone'))
            
            # Get or create category
            category_id = self._get_or_create_category(cursor, transaction.get('category'))
            
            # Insert transaction
            transaction_id = self._insert_transaction(cursor, transaction, sender_user_id, receiver_user_id, category_id)
            
            # Add tags if specified and transaction was successfully inserted
            if transaction_id and transaction.get('tags'):
                self._add_transaction_tags(cursor, transaction_id, transaction['tags'], sender_user_id)
            
            return transaction_id
            
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            raise
    
    def _get_or_create_user(self, cursor, phone: str) -> Optional[int]:
        """Get or create user by phone number."""
        if not phone:
            return None
        
        # Try to get existing user
        cursor.execute("SELECT user_id FROM users WHERE phone_number = %s", (phone,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new user
        user_data = {
            'phone_number': phone,
            'display_name': f"User {phone}",
            'account_status': 'ACTIVE',
            'registration_date': datetime.now(),
            'total_transactions': 0,
            'total_amount_sent': 0.00,
            'total_amount_received': 0.00
        }
        
        cursor.execute("""
            INSERT INTO users (phone_number, display_name, account_status, registration_date, 
                             total_transactions, total_amount_sent, total_amount_received)
            VALUES (%(phone_number)s, %(display_name)s, %(account_status)s, %(registration_date)s,
                    %(total_transactions)s, %(total_amount_sent)s, %(total_amount_received)s)
        """, user_data)
        
        return cursor.lastrowid
    
    def _get_or_create_category(self, cursor, category_name: str) -> Optional[int]:
        """Get or create transaction category."""
        if not category_name:
            return None
        
        # Try to get existing category
        cursor.execute("SELECT category_id FROM transaction_categories WHERE category_name = %s", (category_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new category
        category_code = category_name[:3].upper() if len(category_name) >= 3 else category_name.upper()
        category_data = {
            'category_name': category_name,
            'category_code': category_code,
            'description': f"Auto-generated category for {category_name}",
            'is_active': True
        }
        
        cursor.execute("""
            INSERT IGNORE INTO transaction_categories (category_name, category_code, description, is_active)
            VALUES (%(category_name)s, %(category_code)s, %(description)s, %(is_active)s)
        """, category_data)
        
        # Check if the insert was successful (not ignored due to duplicate)
        if cursor.lastrowid == 0:
            # Row was ignored due to duplicate, get the existing category ID
            cursor.execute("SELECT category_id FROM transaction_categories WHERE category_name = %s", (category_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        else:
            return cursor.lastrowid
    
    def _insert_transaction(self, cursor, transaction: Dict[str, Any], 
                          sender_user_id: Optional[int], receiver_user_id: Optional[int], 
                          category_id: Optional[int]) -> int:
        """Insert transaction into database."""
        
        external_transaction_id = transaction.get('external_transaction_id')
        
        # Check if transaction already exists
        if external_transaction_id:
            cursor.execute("""
                SELECT transaction_id FROM transactions 
                WHERE external_transaction_id = %s
            """, (external_transaction_id,))
            result = cursor.fetchone()
            if result:
                # Transaction already exists, return existing ID
                return result[0]
        
        # Parse transaction date
        transaction_date = self._parse_transaction_date(transaction.get('date'))
        
        # Determine status
        status = self._determine_transaction_status(transaction)
        
        transaction_data = {
            'external_transaction_id': transaction.get('external_transaction_id'),
            'financial_transaction_id': transaction.get('financial_transaction_id'),
            'sender_user_id': sender_user_id,
            'receiver_user_id': receiver_user_id,
            'amount': float(transaction.get('amount', 0)),
            'fee': float(transaction.get('fee', 0.0)),
            'currency': transaction.get('currency', 'RWF'),
            'transaction_date': transaction_date,
            'category_id': category_id,
            'transaction_type': transaction.get('transaction_type', ''),
            'direction': transaction.get('direction', ''),
            'status': status,
            'reference_number': transaction.get('reference'),
            'description': transaction.get('type', ''),
            
            # Enhanced parser fields
            'sender_name': transaction.get('sender_name'),
            'sender_phone': transaction.get('sender_phone'),
            'recipient_name': transaction.get('recipient_name'),
            'recipient_phone': transaction.get('recipient_phone'),
            'momo_code': transaction.get('momo_code'),
            'sender_momo_id': transaction.get('sender_momo_id'),
            'agent_momo_number': transaction.get('agent_momo_number'),
            'business_name': transaction.get('business_name'),
            'new_balance': transaction.get('new_balance'),
            'confidence_score': transaction.get('confidence', 0.0),
            
            # Original data
            'raw_sms_data': transaction.get('original_data', ''),
            'original_message': transaction.get('original_message', ''),
            'xml_attributes': json.dumps(transaction.get('xml_attributes', {})),
            'processing_metadata': json.dumps({
                'cleaned_at': transaction.get('cleaned_at'),
                'categorized_at': transaction.get('categorized_at'),
                'confidence_score': transaction.get('confidence', 0.0),
                'processing_version': '2.0'
            })
        }
        
        cursor.execute("""
            INSERT INTO transactions (
                external_transaction_id, financial_transaction_id, sender_user_id, receiver_user_id, 
                amount, fee, currency, transaction_date, category_id, transaction_type, direction, 
                status, reference_number, description, sender_name, sender_phone, recipient_name, 
                recipient_phone, momo_code, sender_momo_id, agent_momo_number, business_name, 
                new_balance, confidence_score, raw_sms_data, original_message, xml_attributes, 
                processing_metadata
            ) VALUES (
                %(external_transaction_id)s, %(financial_transaction_id)s, %(sender_user_id)s, 
                %(receiver_user_id)s, %(amount)s, %(fee)s, %(currency)s, %(transaction_date)s, 
                %(category_id)s, %(transaction_type)s, %(direction)s, %(status)s, 
                %(reference_number)s, %(description)s, %(sender_name)s, %(sender_phone)s, 
                %(recipient_name)s, %(recipient_phone)s, %(momo_code)s, %(sender_momo_id)s, 
                %(agent_momo_number)s, %(business_name)s, %(new_balance)s, %(confidence_score)s, 
                %(raw_sms_data)s, %(original_message)s, %(xml_attributes)s, %(processing_metadata)s
            )
        """, transaction_data)
        
        # Check if the insert was successful (not ignored due to duplicate)
        if cursor.lastrowid == 0:
            # Row was ignored due to duplicate, get the existing transaction ID
            cursor.execute("""
                SELECT transaction_id FROM transactions 
                WHERE external_transaction_id = %s
            """, (transaction_data['external_transaction_id'],))
            result = cursor.fetchone()
            return result[0] if result else None
        else:
            return cursor.lastrowid
    
    def _add_transaction_tags(self, cursor, transaction_id: int, tags: List[str], assigned_by: int):
        """Add tags to transaction."""
        for tag_name in tags:
            # Get or create tag
            tag_id = self._get_or_create_tag(cursor, tag_name)
            
            # Add transaction-tag relationship
            cursor.execute("""
                INSERT IGNORE INTO transaction_tags (transaction_id, tag_id, assigned_by)
                VALUES (%s, %s, %s)
            """, (transaction_id, tag_id, assigned_by))
    
    def _get_or_create_tag(self, cursor, tag_name: str) -> int:
        """Get or create tag."""
        # Try to get existing tag
        cursor.execute("SELECT tag_id FROM tags WHERE tag_name = %s", (tag_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new tag
        tag_data = {
            'tag_name': tag_name,
            'tag_description': f"Auto-generated tag: {tag_name}",
            'tag_color': '#007bff',
            'is_active': True
        }
        
        cursor.execute("""
            INSERT INTO tags (tag_name, tag_description, tag_color, is_active)
            VALUES (%(tag_name)s, %(tag_description)s, %(tag_color)s, %(is_active)s)
        """, tag_data)
        
        return cursor.lastrowid
    
    def _parse_transaction_date(self, date_str: str) -> datetime:
        """Parse transaction date string."""
        if not date_str:
            return datetime.now()
        
        # Try ISO format first (most common from our ETL pipeline)
        try:
            # Handle ISO format with microseconds
            if 'T' in date_str:
                # Remove microseconds if present
                if '.' in date_str:
                    date_str = date_str.split('.')[0]
                return datetime.fromisoformat(date_str)
        except ValueError:
            pass
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return current time
        logger.warning(f"Could not parse date: {date_str}, using current time")
        return datetime.now()
    
    def _determine_transaction_status(self, transaction: Dict[str, Any]) -> str:
        """Determine transaction status based on available data."""
        # Check if transaction has success indicators
        original_data = transaction.get('original_data', '').lower()
        
        if any(word in original_data for word in ['success', 'completed', 'successful']):
            return 'SUCCESS'
        elif any(word in original_data for word in ['failed', 'error', 'unsuccessful']):
            return 'FAILED'
        elif any(word in original_data for word in ['pending', 'processing']):
            return 'PENDING'
        else:
            return 'SUCCESS'  # Default to success for processed transactions
    
    def _log_etl_process(self, cursor, total_records: int):
        """Log ETL process info."""
        try:
            log_data = {
                'process_name': 'mysql_load_transactions',
                'log_level': 'INFO',
                'message': f'ETL process completed: {self.loaded_count} successful, {self.error_count} failed',
                'records_processed': total_records,
                'records_successful': self.loaded_count,
                'records_failed': self.error_count,
                'execution_time_seconds': 0.0,  # Could be calculated if needed
                'details': json.dumps({
                    'errors': self.errors[:5] if self.errors else [],
                    'database': self.database,
                    'timestamp': datetime.now().isoformat()
                })
            }
            
            cursor.execute("""
                INSERT INTO system_logs (
                    process_name, log_level, message, records_processed, records_successful,
                    records_failed, execution_time_seconds, details
                ) VALUES (
                    %(process_name)s, %(log_level)s, %(message)s, %(records_processed)s,
                    %(records_successful)s, %(records_failed)s, %(execution_time_seconds)s, %(details)s
                )
            """, log_data)
            
        except Exception as e:
            logger.error(f"Error logging ETL process: {e}")
    
    def export_dashboard_json(self) -> Dict[str, Any]:
        """Export data for dashboard visualization."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_transactions
                FROM transactions
            """)
            summary = cursor.fetchone()
            
            # Calculate success rate
            if summary['total_transactions'] > 0:
                summary['success_rate'] = (summary['successful_transactions'] / summary['total_transactions']) * 100
            else:
                summary['success_rate'] = 0
            
            summary['last_updated'] = datetime.now().isoformat()
            
            # Get recent transactions with user info
            cursor.execute("""
                SELECT 
                    t.transaction_date as date,
                    t.amount,
                    t.status,
                    t.description as type,
                    su.phone_number as sender_phone,
                    ru.phone_number as receiver_phone,
                    tc.category_name as category
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                ORDER BY t.transaction_date DESC
                LIMIT 100
            """)
            transactions = cursor.fetchall()
            
            # Get category distribution
            cursor.execute("""
                SELECT tc.category_name as category, COUNT(*) as count
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                WHERE tc.category_name IS NOT NULL
                GROUP BY tc.category_name
                ORDER BY count DESC
            """)
            category_distribution = {row['category']: row['count'] for row in cursor.fetchall()}
            
            # Get amount distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN amount < 10000 THEN '0-10000'
                        WHEN amount < 50000 THEN '10000-50000'
                        WHEN amount < 100000 THEN '50000-100000'
                        ELSE '100000+'
                    END as amount_range,
                    COUNT(*) as count
                FROM transactions
                GROUP BY amount_range
                ORDER BY 
                    CASE 
                        WHEN amount_range = '0-10000' THEN 1
                        WHEN amount_range = '10000-50000' THEN 2
                        WHEN amount_range = '50000-100000' THEN 3
                        ELSE 4
                    END
            """)
            amount_distribution = {row['amount_range']: row['count'] for row in cursor.fetchall()}
            
            # Get tag statistics
            cursor.execute("""
                SELECT 
                    tag.tag_name,
                    COUNT(tt.transaction_id) as count
                FROM tags tag
                LEFT JOIN transaction_tags tt ON tag.tag_id = tt.tag_id
                GROUP BY tag.tag_name
                ORDER BY count DESC
            """)
            tag_distribution = {row['tag_name']: row['count'] for row in cursor.fetchall()}
            
            # Compile dashboard data
            dashboard_data = {
                'summary': summary,
                'transactions': transactions,
                'analytics': {
                    'amountDistribution': amount_distribution,
                    'transactionTypes': category_distribution,
                    'tagDistribution': tag_distribution
                },
                'exported_at': datetime.now().isoformat()
            }
            
            # Save to JSON file
            DASHBOARD_JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DASHBOARD_JSON_FILE, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            logger.info(f"Dashboard data exported to {DASHBOARD_JSON_FILE}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_loading_summary(self) -> Dict[str, Any]:
        """Get loading summary stats."""
        return {
            'total_processed': self.loaded_count + self.error_count,
            'successfully_loaded': self.loaded_count,
            'loading_errors': self.error_count,
            'error_rate': self.error_count / (self.loaded_count + self.error_count) if (self.loaded_count + self.error_count) > 0 else 0,
            'errors': self.errors[:10],  # First 10 errors
            'loaded_at': datetime.now().isoformat()
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database stats."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # Get table counts
            tables = ['users', 'transaction_categories', 'tags', 'transactions', 
                     'transaction_tags', 'user_preferences', 'system_logs', 'transaction_statistics']
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            stats['last_updated'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
