"""
Configuration Settings
Team 11 - Enterprise Web Development
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOGS_DIR = DATA_DIR / "logs"
DEAD_LETTER_DIR = LOGS_DIR / "dead_letter"

# File paths
XML_INPUT_FILE = RAW_DIR / "momo.xml"
DATABASE_FILE = DATA_DIR / "db.sqlite3"
DASHBOARD_JSON_FILE = PROCESSED_DIR / "dashboard.json"
ETL_LOG_FILE = LOGS_DIR / "etl.log"

# Database configuration
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# ETL thresholds and limits
MAX_AMOUNT = 10000000  # 10M UGX
MIN_AMOUNT = 100  # 100 UGX
MAX_PHONE_LENGTH = 15
MIN_PHONE_LENGTH = 10

# Transaction categories
TRANSACTION_CATEGORIES = {
    'DEPOSIT': ['deposit', 'credit', 'topup', 'receive'],
    'WITHDRAWAL': ['withdraw', 'debit', 'cashout', 'send'],
    'TRANSFER': ['transfer', 'send_money', 'mobile_money'],
    'PAYMENT': ['payment', 'bill', 'utility', 'merchant'],
    'DATA_BUNDLE': ['data bundle', 'data_bundle', 'bundle', 'internet', 'data', 'mtn data', 'yello', '*164*'],
    'AIRTIME': ['airtime', 'credit', 'topup', 'recharge'],
    'QUERY': ['balance', 'statement', 'inquiry'],
    'OTHER': ['other', 'unknown', 'misc']
}

# Phone number patterns (Uganda)
PHONE_PATTERNS = [
    r'^\+256\d{9}$',  # +256XXXXXXXXX
    r'^256\d{9}$',    # 256XXXXXXXXX
    r'^0\d{9}$'       # 0XXXXXXXXX
]

# Date formats to try parsing
DATE_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d',
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y',
    '%m/%d/%Y %H:%M:%S',
    '%m/%d/%Y'
]

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API configuration (if using FastAPI)
API_HOST = os.getenv('API_HOST', 'localhost')
API_PORT = int(os.getenv('API_PORT', 8000))
API_DEBUG = os.getenv('API_DEBUG', 'True').lower() == 'true'

# Frontend configuration
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', 3000))
FRONTEND_HOST = os.getenv('FRONTEND_HOST', 'localhost')
