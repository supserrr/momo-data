#!/usr/bin/env python3
"""
Unified REST API Server for MoMo SMS Data Processing
Implements comprehensive REST API with DSA demonstrations
"""

import json
import base64
import urllib.parse
import os
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import mimetypes
import io
import csv
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.parser import MTNParser
from etl.loader import MySQLDatabaseLoader
from dsa.search_comparison import SearchComparison
from dsa.sorting_comparison import SortingComparison

# Import database manager
from api.db import MySQLDatabaseManager

class UnifiedRESTAPIHandler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler for REST API endpoints.
    Provides transaction management and DSA demonstrations.
    """
    
    def __init__(self, *args, **kwargs):
        # Initialize data storage
        self.transactions = []
        self.transaction_id_counter = 1
        self.db_manager = MySQLDatabaseManager()
        self.load_sample_data()
        super().__init__(*args, **kwargs)
    
    def load_sample_data(self):
        """Load sample transaction data from XML file."""
        try:
            xml_file = Path(__file__).parent.parent / "data" / "raw" / "modified_sms_v2.xml"
            if xml_file.exists():
                parser = MTNParser()
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                for sms in root.findall('.//sms'):
                    body = sms.get('body', '')
                    date = sms.get('date', '')
                    
                    if self._is_momo_sms(body, sms.get('address', '')):
                        transaction = parser.parse_message(body, date)
                        if transaction:
                            transaction_dict = {
                                'id': self.transaction_id_counter,
                                'amount': transaction.amount,
                                'currency': transaction.currency,
                                'transaction_type': transaction.transaction_type,
                                'category': transaction.category,
                                'direction': transaction.direction,
                                'status': transaction.status,
                                'sender_name': transaction.sender_name,
                                'sender_phone': transaction.sender_phone,
                                'recipient_name': transaction.recipient_name,
                                'recipient_phone': transaction.recipient_phone,
                                'momo_code': transaction.momo_code,
                                'fee': transaction.fee,
                                'new_balance': transaction.new_balance,
                                'transaction_id': transaction.transaction_id,
                                'financial_transaction_id': transaction.financial_transaction_id,
                                'external_transaction_id': transaction.external_transaction_id,
                                'date': transaction.date,
                                'original_message': transaction.original_message,
                                'confidence': transaction.confidence
                            }
                            self.transactions.append(transaction_dict)
                            self.transaction_id_counter += 1
        except Exception as e:
            print(f"Error loading sample data: {e}")
            # Load sample data if XML parsing fails
            self.transactions = [
                {
                    'id': 1,
                    'amount': 1000.0,
                    'currency': 'RWF',
                    'transaction_type': 'TRANSFER',
                    'category': 'TRANSFER_OUTGOING',
                    'direction': 'debit',
                    'status': 'SUCCESS',
                    'sender_name': 'John Doe',
                    'sender_phone': '+250788123456',
                    'recipient_name': 'Jane Smith',
                    'recipient_phone': '+250789123456',
                    'date': '2024-01-01T10:00:00',
                    'original_message': 'Sample transaction message'
                },
                {
                    'id': 2,
                    'amount': 2000.0,
                    'currency': 'RWF',
                    'transaction_type': 'DEPOSIT',
                    'category': 'DEPOSIT_AGENT',
                    'direction': 'credit',
                    'status': 'SUCCESS',
                    'sender_name': 'Agent',
                    'sender_phone': '+250788654321',
                    'recipient_name': 'John Doe',
                    'recipient_phone': '+250788123456',
                    'date': '2024-01-01T11:00:00',
                    'original_message': 'Agent deposit message'
                }
            ]
            self.transaction_id_counter = 3
    
    def _is_momo_sms(self, body: str, address: str) -> bool:
        """Check if SMS is a MoMo transaction."""
        momo_addresses = ['M-Money', 'MTN', 'MoMo', 'Mobile Money']
        if any(addr.lower() in address.lower() for addr in momo_addresses):
            return True
        
        momo_keywords = [
            'RWF', 'UGX', 'deposit', 'withdraw', 'transfer', 'payment',
            'balance', 'mobile money', 'momo', 'transaction', 'TxId',
            'received', 'sent', 'completed', 'fee', 'new balance'
        ]
        
        body_lower = body.lower()
        return any(keyword.lower() in body_lower for keyword in momo_keywords)
    
    def _authenticate(self) -> bool:
        """Check Basic Authentication credentials."""
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        
        try:
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            return username == 'admin' and password == 'password'
        except Exception:
            return False
    
    def _send_response(self, status_code: int, data: Any = None, message: str = None, content_type: str = 'application/json'):
        """Send HTTP response with JSON data."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        if content_type == 'application/json':
            response = {}
            if data is not None:
                response['data'] = data
            if message:
                response['message'] = message
            if status_code >= 400:
                response['error'] = True
            
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        else:
            self.wfile.write(data)
    
    def _send_error(self, status_code: int, message: str):
        """Send error response."""
        self._send_response(status_code, message=message)
    
    def _parse_json_body(self) -> Dict[str, Any]:
        """Parse JSON from request body."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except Exception:
            return {}
    
    def _parse_query_params(self) -> Dict[str, str]:
        """Parse query parameters from URL."""
        query_string = urllib.parse.urlparse(self.path).query
        return dict(urllib.parse.parse_qsl(query_string))
    
    def _get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID using linear search (DSA requirement)."""
        for transaction in self.transactions:
            if transaction.get('id') == transaction_id:
                return transaction
        return None
    
    def _get_transaction_by_id_dict(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID using dictionary lookup (DSA requirement)."""
        transactions_dict = {t['id']: t for t in self.transactions}
        return transactions_dict.get(transaction_id)
    
    def _filter_transactions(self, transactions: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter transactions based on criteria."""
        filtered = transactions
        
        if filters.get('category'):
            filtered = [t for t in filtered if t.get('category') == filters['category']]
        
        if filters.get('status'):
            filtered = [t for t in filtered if t.get('status') == filters['status']]
        
        if filters.get('phone'):
            phone = filters['phone']
            filtered = [t for t in filtered if 
                       phone in t.get('sender_phone', '') or 
                       phone in t.get('recipient_phone', '')]
        
        if filters.get('transaction_type'):
            filtered = [t for t in filtered if t.get('transaction_type') == filters['transaction_type']]
        
        if filters.get('min_amount'):
            filtered = [t for t in filtered if t.get('amount', 0) >= float(filters['min_amount'])]
        
        if filters.get('max_amount'):
            filtered = [t for t in filtered if t.get('amount', 0) <= float(filters['max_amount'])]
        
        return filtered
    
    def _search_transactions(self, query: str, transactions: List[Dict]) -> List[Dict]:
        """Search transactions by text query."""
        query_lower = query.lower()
        results = []
        
        for transaction in transactions:
            # Search in various fields
            searchable_fields = [
                transaction.get('sender_name', ''),
                transaction.get('recipient_name', ''),
                transaction.get('sender_phone', ''),
                transaction.get('recipient_phone', ''),
                transaction.get('original_message', ''),
                transaction.get('transaction_type', ''),
                transaction.get('category', '')
            ]
            
            if any(query_lower in str(field).lower() for field in searchable_fields):
                results.append(transaction)
        
        return results
    
    def _get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard summary data."""
        total_transactions = len(self.transactions)
        total_amount = sum(t.get('amount', 0) for t in self.transactions)
        successful_transactions = len([t for t in self.transactions if t.get('status') in ['SUCCESS', 'COMPLETED']])
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Category distribution
        categories = {}
        for transaction in self.transactions:
            category = transaction.get('category', 'OTHER')
            amount = transaction.get('amount', 0)
            if category not in categories:
                categories[category] = {'count': 0, 'total_amount': 0, 'amounts': []}
            categories[category]['count'] += 1
            categories[category]['total_amount'] += amount
            categories[category]['amounts'].append(amount)
        
        # Amount distribution with smaller ranges for better visualization
        amount_ranges = {
            '0-500': 0,
            '500-1000': 0,
            '1000-2000': 0,
            '2000-5000': 0,
            '5000-10000': 0,
            '10000-20000': 0,
            '20000-50000': 0,
            '50000+': 0
        }
        
        for transaction in self.transactions:
            amount = transaction.get('amount', 0)
            if amount <= 500:
                amount_ranges['0-500'] += 1
            elif amount <= 1000:
                amount_ranges['500-1000'] += 1
            elif amount <= 2000:
                amount_ranges['1000-2000'] += 1
            elif amount <= 5000:
                amount_ranges['2000-5000'] += 1
            elif amount <= 10000:
                amount_ranges['5000-10000'] += 1
            elif amount <= 20000:
                amount_ranges['10000-20000'] += 1
            elif amount <= 50000:
                amount_ranges['20000-50000'] += 1
            else:
                amount_ranges['50000+'] += 1
        
        return {
            'summary': {
                'total_transactions': total_transactions,
                'total_amount': total_amount,
                'success_rate': success_rate,
                'average_transaction': total_amount / total_transactions if total_transactions > 0 else 0
            },
            'categories': [
                {
                    'category': k, 
                    'count': v['count'], 
                    'total_amount': v['total_amount'],
                    'avg_amount': v['total_amount'] / v['count'] if v['count'] > 0 else 0,
                    'min_amount': min(v['amounts']) if v['amounts'] else 0,
                    'max_amount': max(v['amounts']) if v['amounts'] else 0
                } 
                for k, v in categories.items()
            ],
            'amount_distribution': [{'amount_range': k, 'count': v} for k, v in amount_ranges.items()]
        }
    
    def _get_analytics_data(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get analytics data."""
        dashboard_data = self._get_dashboard_data()
        
        # Monthly stats
        monthly_stats = []
        for i in range(12):
            month_transactions = [t for t in self.transactions if t.get('date', '').startswith(f'2024-{i+1:02d}')]
            monthly_stats.append({
                'month': f'2024-{i+1:02d}',
                'count': len(month_transactions),
                'volume': sum(t.get('amount', 0) for t in month_transactions)  # Changed from 'amount' to 'volume'
            })
        
        # Transaction types by amount
        transaction_types = {}
        for transaction in self.transactions:
            t_type = transaction.get('transaction_type', 'OTHER')
            amount = transaction.get('amount', 0)
            if t_type not in transaction_types:
                transaction_types[t_type] = {'count': 0, 'total_amount': 0}
            transaction_types[t_type]['count'] += 1
            transaction_types[t_type]['total_amount'] += amount
        
        # Hourly pattern
        hourly_pattern = [{'count': 0, 'volume': 0} for _ in range(24)]
        for transaction in self.transactions:
            try:
                date_str = transaction.get('date', '')
                # Handle both ISO format (with T) and space-separated format
                if 'T' in date_str:
                    hour = int(date_str.split('T')[1].split(':')[0])
                elif ' ' in date_str:
                    # Handle format like "2024-05-10 16:30:51"
                    hour = int(date_str.split(' ')[1].split(':')[0])
                else:
                    continue
                    
                hourly_pattern[hour]['count'] += 1
                hourly_pattern[hour]['volume'] += transaction.get('amount', 0)
            except:
                pass
        
        return {
            'monthly_stats': monthly_stats,
            'transaction_types': [{'type': k, **v} for k, v in transaction_types.items()],
            'hourly_pattern': [{'hour': i, 'count': data['count'], 'volume': data['volume']} for i, data in enumerate(hourly_pattern)]
        }
    
    def _export_to_csv(self, data: List[Dict], filename: str) -> bytes:
        """Export data to CSV format."""
        if not data:
            return b''
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue().encode('utf-8')
    
    def _serve_static_file(self, file_path: str):
        """Serve static files."""
        try:
            full_path = Path(__file__).parent.parent / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                content_type, _ = mimetypes.guess_type(str(full_path))
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                self._send_response(200, content, content_type=content_type)
            else:
                self._send_error(404, "File not found")
        except Exception as e:
            self._send_error(500, f"Error serving file: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        path = urllib.parse.urlparse(self.path).path
        
        # Serve frontend and static files without authentication
        if path == '/' or path.startswith('/web/') or path.startswith('/data/'):
            if path == '/':
                self._serve_static_file('index.html')
            elif path.startswith('/web/'):
                self._serve_static_file(path[1:])  # Remove leading slash
            elif path.startswith('/data/'):
                self._serve_static_file(path[1:])  # Remove leading slash
            return
        
        # All API endpoints require authentication
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Invalid credentials")
            return
        
        query_params = self._parse_query_params()
        
        # API endpoints
        if path == '/api/transactions':
            self._handle_get_transactions(query_params)
        elif path.startswith('/api/transactions/'):
            transaction_id = int(path.split('/')[-1])
            self._handle_get_transaction(transaction_id)
        elif path == '/api/dashboard-data':
            self._handle_get_dashboard_data()
        elif path == '/api/analytics':
            self._handle_get_analytics(query_params)
        elif path == '/api/transaction-types-by-amount':
            self._handle_get_transaction_types_by_amount()
        elif path == '/api/monthly-stats':
            self._handle_get_monthly_stats()
        elif path == '/api/category-distribution':
            self._handle_get_category_distribution()
        elif path == '/api/hourly-pattern':
            self._handle_get_hourly_pattern()
        elif path == '/api/amount-distribution':
            self._handle_get_amount_distribution()
        elif path == '/api/search':
            self._handle_search_transactions(query_params)
        elif path == '/api/categories':
            self._handle_get_categories()
        elif path == '/api/etl/logs':
            self._handle_get_etl_logs(query_params)
        elif path == '/api/export/stats':
            self._handle_get_database_stats()
        elif path == '/api/health':
            self._handle_health_check()
        elif path == '/api/info':
            self._handle_get_api_info()
        elif path == '/api/transactions/filter':
            self._handle_get_transactions_filtered(query_params)
        elif path == '/api/export/transactions':
            self._handle_export_transactions(query_params)
        elif path == '/api/export/analytics':
            self._handle_export_analytics(query_params)
        elif path == '/api/export/dashboard':
            self._handle_export_dashboard(query_params)
        elif path == '/api/search/transactions':
            self._handle_search_transactions(query_params)
        elif path == '/api/stats/summary':
            self._handle_get_stats_summary(query_params)
        # Assignment-specific DSA endpoints
        elif path == '/dsa/linear-search':
            self._handle_linear_search_demo(query_params)
        elif path == '/dsa/dictionary-lookup':
            self._handle_dictionary_lookup_demo(query_params)
        elif path == '/dsa/comparison':
            self._handle_dsa_comparison()
        # Legacy assignment endpoints (without /api prefix)
        elif path == '/transactions':
            self._handle_get_transactions(query_params)
        elif path.startswith('/transactions/'):
            transaction_id = int(path.split('/')[-1])
            self._handle_get_transaction(transaction_id)
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests."""
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Invalid credentials")
            return
        
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/api/transactions' or path == '/transactions':
            data = self._parse_json_body()
            self._handle_create_transaction(data)
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_PUT(self):
        """Handle PUT requests."""
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Invalid credentials")
            return
        
        path = urllib.parse.urlparse(self.path).path
        
        if path.startswith('/api/transactions/') or path.startswith('/transactions/'):
            transaction_id = int(path.split('/')[-1])
            data = self._parse_json_body()
            self._handle_update_transaction(transaction_id, data)
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Invalid credentials")
            return
        
        path = urllib.parse.urlparse(self.path).path
        
        if path.startswith('/api/transactions/') or path.startswith('/transactions/'):
            transaction_id = int(path.split('/')[-1])
            self._handle_delete_transaction(transaction_id)
        else:
            self._send_error(404, "Endpoint not found")
    
    # Transaction handlers
    def _handle_get_transactions(self, query_params: Dict[str, str]):
        """Handle GET /api/transactions or /transactions"""
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))
        
        # Apply filters
        filtered_transactions = self._filter_transactions(self.transactions, query_params)
        
        # Apply pagination
        paginated_transactions = filtered_transactions[offset:offset + limit]
        
        self._send_response(200, paginated_transactions)
    
    def _handle_get_transaction(self, transaction_id: int):
        """Handle GET /api/transactions/{id} or /transactions/{id}"""
        transaction = self._get_transaction_by_id(transaction_id)
        if transaction:
            self._send_response(200, transaction)
        else:
            self._send_error(404, "Transaction not found")
    
    def _handle_create_transaction(self, data: Dict[str, Any]):
        """Handle POST /api/transactions or /transactions"""
        if not data:
            self._send_error(400, "Invalid JSON data")
            return
        
        required_fields = ['amount', 'currency', 'transaction_type']
        for field in required_fields:
            if field not in data:
                self._send_error(400, f"Missing required field: {field}")
                return
        
        new_transaction = {
            'id': self.transaction_id_counter,
            'amount': float(data['amount']),
            'currency': data['currency'],
            'transaction_type': data['transaction_type'],
            'category': data.get('category', 'OTHER'),
            'direction': data.get('direction', 'debit'),
            'status': data.get('status', 'SUCCESS'),
            'sender_name': data.get('sender_name'),
            'sender_phone': data.get('sender_phone'),
            'recipient_name': data.get('recipient_name'),
            'recipient_phone': data.get('recipient_phone'),
            'momo_code': data.get('momo_code'),
            'fee': data.get('fee', 0.0),
            'new_balance': data.get('new_balance'),
            'transaction_id': data.get('transaction_id'),
            'financial_transaction_id': data.get('financial_transaction_id'),
            'external_transaction_id': data.get('external_transaction_id'),
            'date': data.get('date', datetime.now().isoformat()),
            'original_message': data.get('original_message'),
            'confidence': data.get('confidence', 1.0)
        }
        
        self.transactions.append(new_transaction)
        self.transaction_id_counter += 1
        
        self._send_response(201, new_transaction, "Transaction created successfully")
    
    def _handle_update_transaction(self, transaction_id: int, data: Dict[str, Any]):
        """Handle PUT /api/transactions/{id} or /transactions/{id}"""
        for i, transaction in enumerate(self.transactions):
            if transaction.get('id') == transaction_id:
                for key, value in data.items():
                    if key != 'id':
                        transaction[key] = value
                
                self._send_response(200, transaction, "Transaction updated successfully")
                return
        
        self._send_error(404, "Transaction not found")
    
    def _handle_delete_transaction(self, transaction_id: int):
        """Handle DELETE /api/transactions/{id} or /transactions/{id}"""
        for i, transaction in enumerate(self.transactions):
            if transaction.get('id') == transaction_id:
                deleted_transaction = self.transactions.pop(i)
                self._send_response(200, deleted_transaction, "Transaction deleted successfully")
                return
        
        self._send_error(404, "Transaction not found")
    
    # Dashboard handlers
    def _handle_get_dashboard_data(self):
        """Handle GET /api/dashboard-data"""
        dashboard_data = self._get_dashboard_data()
        self._send_response(200, dashboard_data)
    
    # Analytics handlers
    def _handle_get_analytics(self, query_params: Dict[str, str]):
        """Handle GET /api/analytics"""
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        analytics_data = self._get_analytics_data(start_date, end_date)
        self._send_response(200, analytics_data)
    
    def _handle_get_transaction_types_by_amount(self):
        """Handle GET /api/transaction-types-by-amount"""
        analytics_data = self._get_analytics_data()
        transaction_types = analytics_data.get('transaction_types', [])
        # Return in format expected by frontend
        self._send_response(200, {'transaction_types_by_amount': transaction_types})
    
    def _handle_get_monthly_stats(self):
        """Handle GET /api/monthly-stats"""
        analytics_data = self._get_analytics_data()
        monthly_stats = analytics_data.get('monthly_stats', [])
        # Return in format expected by frontend
        self._send_response(200, {'monthly_stats': monthly_stats})
    
    def _handle_get_category_distribution(self):
        """Handle GET /api/category-distribution"""
        dashboard_data = self._get_dashboard_data()
        categories = dashboard_data.get('categories', [])
        # Return in format expected by frontend
        self._send_response(200, {'category_distribution': categories})
    
    def _handle_get_hourly_pattern(self):
        """Handle GET /api/hourly-pattern"""
        analytics_data = self._get_analytics_data()
        hourly_pattern = analytics_data.get('hourly_pattern', [])
        # Return in format expected by frontend
        self._send_response(200, {'hourly_pattern': hourly_pattern})
    
    def _handle_get_amount_distribution(self):
        """Handle GET /api/amount-distribution"""
        dashboard_data = self._get_dashboard_data()
        amount_distribution = dashboard_data.get('amount_distribution', [])
        # Return in format expected by frontend
        self._send_response(200, {'amount_distribution': amount_distribution})
    
    # Search handlers
    def _handle_search_transactions(self, query_params: Dict[str, str]):
        """Handle GET /api/search"""
        query = query_params.get('q', '')
        limit = int(query_params.get('limit', 50))
        
        if not query:
            self._send_error(400, "Search query is required")
            return
        
        results = self._search_transactions(query, self.transactions)
        limited_results = results[:limit]
        
        self._send_response(200, limited_results)
    
    def _handle_search_transactions(self, query_params: Dict[str, str]):
        """Handle GET /api/search/transactions"""
        query = query_params.get('q', '')
        limit = int(query_params.get('limit', 50))
        
        if not query:
            self._send_error(400, "Search query is required")
            return
        
        results = self._search_transactions(query, self.transactions)
        limited_results = results[:limit]
        
        response = {
            'success': True,
            'data': limited_results,
            'metadata': {
                'query': query,
                'count': len(limited_results),
                'limit': limit
            }
        }
        
        self._send_response(200, response)
    
    # Categories handlers
    def _handle_get_categories(self):
        """Handle GET /api/categories"""
        dashboard_data = self._get_dashboard_data()
        categories = dashboard_data.get('categories', [])
        self._send_response(200, categories)
    
    # ETL handlers
    def _handle_get_etl_logs(self, query_params: Dict[str, str]):
        """Handle GET /api/etl/logs"""
        limit = int(query_params.get('limit', 50))
        
        # Mock ETL logs
        etl_logs = [
            {
                'id': 1,
                'timestamp': '2024-01-01T10:00:00',
                'level': 'INFO',
                'message': 'ETL process started',
                'file': 'sample_sms.xml',
                'records_processed': 100
            },
            {
                'id': 2,
                'timestamp': '2024-01-01T10:05:00',
                'level': 'INFO',
                'message': 'ETL process completed successfully',
                'file': 'sample_sms.xml',
                'records_processed': 100
            }
        ]
        
        limited_logs = etl_logs[:limit]
        self._send_response(200, limited_logs)
    
    # Export handlers
    def _handle_get_database_stats(self):
        """Handle GET /api/export/stats"""
        stats = {
            'total_transactions': len(self.transactions),
            'total_amount': sum(t.get('amount', 0) for t in self.transactions),
            'categories_count': len(set(t.get('category', '') for t in self.transactions)),
            'date_range': {
                'earliest': min(t.get('date', '') for t in self.transactions) if self.transactions else None,
                'latest': max(t.get('date', '') for t in self.transactions) if self.transactions else None
            }
        }
        self._send_response(200, stats)
    
    def _handle_export_transactions(self, query_params: Dict[str, str]):
        """Handle GET /api/advanced/export/transactions"""
        format_type = query_params.get('format_type', 'json')
        limit = int(query_params.get('limit', 1000))
        
        # Apply filters
        filtered_transactions = self._filter_transactions(self.transactions, query_params)
        limited_transactions = filtered_transactions[:limit]
        
        if format_type.lower() == 'csv':
            csv_data = self._export_to_csv(limited_transactions, 'transactions.csv')
            self._send_response(200, csv_data, content_type='text/csv')
        else:
            self._send_response(200, limited_transactions)
    
    def _handle_export_analytics(self, query_params: Dict[str, str]):
        """Handle GET /api/advanced/export/analytics"""
        format_type = query_params.get('format_type', 'json')
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        analytics_data = self._get_analytics_data(start_date, end_date)
        
        if format_type.lower() == 'csv':
            # Flatten analytics data for CSV export
            csv_data = []
            for monthly in analytics_data.get('monthly_stats', []):
                csv_data.append({
                    'type': 'monthly_stats',
                    'month': monthly['month'],
                    'count': monthly['count'],
                    'amount': monthly['amount']
                })
            
            for t_type in analytics_data.get('transaction_types', []):
                csv_data.append({
                    'type': 'transaction_types',
                    'transaction_type': t_type['type'],
                    'count': t_type['count'],
                    'total_amount': t_type['total_amount']
                })
            
            csv_bytes = self._export_to_csv(csv_data, 'analytics.csv')
            self._send_response(200, csv_bytes, content_type='text/csv')
        else:
            self._send_response(200, analytics_data)
    
    def _handle_export_dashboard(self, query_params: Dict[str, str]):
        """Handle GET /api/advanced/export/dashboard"""
        format_type = query_params.get('format_type', 'json')
        dashboard_data = self._get_dashboard_data()
        
        if format_type.lower() == 'csv':
            # Flatten dashboard data for CSV export
            csv_data = []
            for category in dashboard_data.get('categories', []):
                csv_data.append({
                    'type': 'category',
                    'category': category['category'],
                    'count': category['count']
                })
            
            for amount_range in dashboard_data.get('amount_distribution', []):
                csv_data.append({
                    'type': 'amount_distribution',
                    'range': amount_range['range'],
                    'count': amount_range['count']
                })
            
            csv_bytes = self._export_to_csv(csv_data, 'dashboard.csv')
            self._send_response(200, csv_bytes, content_type='text/csv')
        else:
            self._send_response(200, dashboard_data)
    
    # Additional handlers
    def _handle_get_transactions_filtered(self, query_params: Dict[str, str]):
        """Handle GET /api/transactions/filter"""
        limit = int(query_params.get('limit', 100))
        offset = int(query_params.get('offset', 0))
        
        # Apply filters
        filtered_transactions = self._filter_transactions(self.transactions, query_params)
        
        # Apply pagination
        paginated_transactions = filtered_transactions[offset:offset + limit]
        
        response = {
            'success': True,
            'data': paginated_transactions,
            'metadata': {
                'count': len(paginated_transactions),
                'limit': limit,
                'offset': offset,
                'filters': {k: v for k, v in query_params.items() if k not in ['limit', 'offset']},
                'sorting': {
                    'sort_by': query_params.get('sort_by', 'date'),
                    'sort_order': query_params.get('sort_order', 'DESC')
                }
            }
        }
        
        self._send_response(200, response)
    
    def _handle_get_stats_summary(self, query_params: Dict[str, str]):
        """Handle GET /api/stats/summary"""
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        dashboard_data = self._get_dashboard_data()
        analytics_data = self._get_analytics_data(start_date, end_date)
        
        response = {
            'success': True,
            'data': {
                'summary': dashboard_data.get('summary', {}),
                'analytics': analytics_data,
                'category_breakdown': dashboard_data.get('categories', []),
                'hourly_pattern': analytics_data.get('hourly_pattern', []),
                'amount_distribution': dashboard_data.get('amount_distribution', []),
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
        }
        
        self._send_response(200, response)
    
    # Health and info handlers
    def _handle_health_check(self):
        """Handle GET /api/health"""
        try:
            # Test database connection (mock)
            health_data = {
                'status': 'healthy',
                'database': 'connected',
                'message': 'All systems operational',
                'timestamp': datetime.now().isoformat()
            }
            self._send_response(200, health_data)
        except Exception as e:
            self._send_error(503, f"Health check failed: {str(e)}")
    
    def _handle_get_api_info(self):
        """Handle GET /api/info"""
        api_info = {
            'name': 'Unified MoMo Data Processing API',
            'version': '1.0.0',
            'description': 'Unified REST API for mobile money SMS transaction processing with DSA demonstrations',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'transactions': '/api/transactions or /transactions',
                'analytics': '/api/analytics',
                'dashboard': '/api/dashboard-data',
                'etl': '/api/etl/logs',
                'categories': '/api/categories',
                'search': '/api/search',
                'export': '/api/export/stats',
                'health': '/api/health',
                'dsa_linear_search': '/dsa/linear-search',
                'dsa_dictionary_lookup': '/dsa/dictionary-lookup',
                'dsa_comparison': '/dsa/comparison'
            },
            'authentication': 'Basic Auth (admin:password)'
        }
        self._send_response(200, api_info)
    
    # DSA handlers (Assignment requirements)
    def _handle_linear_search_demo(self, query_params: Dict[str, str]):
        """Handle GET /dsa/linear-search"""
        target_id = int(query_params.get('id', 1))
        
        start_time = time.time()
        result = self._get_transaction_by_id(target_id)
        end_time = time.time()
        
        response = {
            'algorithm': 'Linear Search',
            'target_id': target_id,
            'found': result is not None,
            'result': result,
            'execution_time_ms': (end_time - start_time) * 1000,
            'comparisons': len(self.transactions) if result is None else self.transactions.index(result) + 1,
            'data_size': len(self.transactions)
        }
        
        self._send_response(200, response)
    
    def _handle_dictionary_lookup_demo(self, query_params: Dict[str, str]):
        """Handle GET /dsa/dictionary-lookup"""
        target_id = int(query_params.get('id', 1))
        
        start_time = time.time()
        result = self._get_transaction_by_id_dict(target_id)
        end_time = time.time()
        
        response = {
            'algorithm': 'Dictionary Lookup',
            'target_id': target_id,
            'found': result is not None,
            'result': result,
            'execution_time_ms': (end_time - start_time) * 1000,
            'comparisons': 1,
            'data_size': len(self.transactions)
        }
        
        self._send_response(200, response)
    
    def _handle_dsa_comparison(self):
        """Handle GET /dsa/comparison"""
        import random
        
        test_ids = random.sample([t['id'] for t in self.transactions], min(20, len(self.transactions)))
        
        linear_search_times = []
        dictionary_lookup_times = []
        
        for test_id in test_ids:
            # Linear search
            start_time = time.time()
            self._get_transaction_by_id(test_id)
            linear_search_times.append((time.time() - start_time) * 1000)
            
            # Dictionary lookup
            start_time = time.time()
            self._get_transaction_by_id_dict(test_id)
            dictionary_lookup_times.append((time.time() - start_time) * 1000)
        
        response = {
            'comparison': {
                'linear_search': {
                    'avg_time_ms': sum(linear_search_times) / len(linear_search_times),
                    'min_time_ms': min(linear_search_times),
                    'max_time_ms': max(linear_search_times),
                    'total_time_ms': sum(linear_search_times)
                },
                'dictionary_lookup': {
                    'avg_time_ms': sum(dictionary_lookup_times) / len(dictionary_lookup_times),
                    'min_time_ms': min(dictionary_lookup_times),
                    'max_time_ms': max(dictionary_lookup_times),
                    'total_time_ms': sum(dictionary_lookup_times)
                }
            },
            'data_size': len(self.transactions),
            'test_count': len(test_ids),
            'analysis': {
                'dictionary_lookup_faster_by': f"{sum(linear_search_times) / sum(dictionary_lookup_times):.2f}x",
                'explanation': "Dictionary lookup is O(1) average case while linear search is O(n), making it significantly faster for large datasets."
            }
        }
        
        self._send_response(200, response)
    
    def log_message(self, format, *args):
        """Override to reduce log verbosity."""
        pass


def run_unified_rest_api(port: int = 8000):
    """Run the unified REST API server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, UnifiedRESTAPIHandler)
    print(f"Unified REST API Server running on port {port}")
    print(f"Access the API at: http://localhost:{port}")
    print(f"Frontend available at: http://localhost:{port}/")
    print("\nAvailable Endpoints:")
    print("  Frontend & Static Files:")
    print("    GET    /                           - Frontend dashboard")
    print("    GET    /web/*                      - Static web files")
    print("    GET    /data/*                     - Static data files")
    print("  Core API:")
    print("    GET    /api/transactions           - List all transactions")
    print("    GET    /api/transactions/{id}      - Get specific transaction")
    print("    POST   /api/transactions           - Create new transaction")
    print("    PUT    /api/transactions/{id}      - Update transaction")
    print("    DELETE /api/transactions/{id}      - Delete transaction")
    print("  Dashboard & Analytics:")
    print("    GET    /api/dashboard-data         - Dashboard summary data")
    print("    GET    /api/analytics              - Analytics data")
    print("    GET    /api/transaction-types-by-amount - Transaction types")
    print("    GET    /api/monthly-stats          - Monthly statistics")
    print("    GET    /api/category-distribution  - Category breakdown")
    print("    GET    /api/hourly-pattern         - Hourly transaction pattern")
    print("    GET    /api/amount-distribution    - Amount distribution")
    print("  Search & Categories:")
    print("    GET    /api/search                 - Search transactions")
    print("    GET    /api/categories             - Category statistics")
    print("  ETL & Export:")
    print("    GET    /api/etl/logs               - ETL process logs")
    print("    GET    /api/export/stats           - Database statistics")
    print("  Additional Features:")
    print("    GET    /api/transactions/filter    - Transaction filtering")
    print("    GET    /api/export/transactions    - Export transactions")
    print("    GET    /api/export/analytics       - Export analytics")
    print("    GET    /api/export/dashboard       - Export dashboard")
    print("    GET    /api/search/transactions    - Search transactions")
    print("    GET    /api/stats/summary          - Statistics summary")
    print("  System:")
    print("    GET    /api/health                 - Health check")
    print("    GET    /api/info                   - API information")
    print("  DSA Demonstrations (Assignment Requirements):")
    print("    GET    /dsa/linear-search?id=X     - Linear search demo")
    print("    GET    /dsa/dictionary-lookup?id=X - Dictionary lookup demo")
    print("    GET    /dsa/comparison             - Performance comparison")
    print("  Legacy Assignment Endpoints:")
    print("    GET    /transactions               - List all transactions (legacy)")
    print("    GET    /transactions/{id}          - Get specific transaction (legacy)")
    print("    POST   /transactions               - Create new transaction (legacy)")
    print("    PUT    /transactions/{id}          - Update transaction (legacy)")
    print("    DELETE /transactions/{id}          - Delete transaction (legacy)")
    print("\nAuthentication: Basic Auth (admin:password)")
    print("Example: curl -u admin:password http://localhost:{port}/api/transactions")
    print("Example: curl -u admin:password http://localhost:{port}/dsa/comparison")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Unified Plain Python REST API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on')
    args = parser.parse_args()
    run_unified_rest_api(args.port)
