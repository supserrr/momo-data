"""
Configuration settings for MoMo Data Processing API
Team 11 - Enterprise Web Development
"""

import os
from typing import List, Dict, Any

# API Configuration
API_PREFIX = "/api"
TITLE = "MoMo Data Processing API"
DESCRIPTION = "Enterprise-level mobile money transaction processing and analytics API"
VERSION = "1.0.0"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"

# CORS Configuration
CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Database Configuration
DATABASE_HOST = "localhost"
DATABASE_PORT = 3306
DATABASE_NAME = "momo_sms_processing"
DATABASE_USER = "root"
DATABASE_PASSWORD = ""

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Response Templates
RESPONSE_TEMPLATES = {
    "success": {
        "success": True,
        "message": "Operation completed successfully",
        "timestamp": None
    },
    "error": {
        "success": False,
        "message": "An error occurred",
        "error_code": None,
        "timestamp": None
    },
    "validation_error": {
        "success": False,
        "message": "Validation error",
        "errors": [],
        "timestamp": None
    }
}

# Error Codes
ERROR_CODES = {
    "VALIDATION_ERROR": 400,
    "NOT_FOUND": 404,
    "INTERNAL_ERROR": 500,
    "DATABASE_ERROR": 503
}

# API Routers (simplified for now)
API_ROUTERS = []

# Settings object for easy access
class Settings:
    def __init__(self):
        self.api_prefix = API_PREFIX
        self.title = TITLE
        self.description = DESCRIPTION
        self.version = VERSION
        self.docs_url = DOCS_URL
        self.redoc_url = REDOC_URL
        self.cors_origins = CORS_ORIGINS
        self.cors_allow_credentials = CORS_ALLOW_CREDENTIALS
        self.cors_allow_methods = CORS_ALLOW_METHODS
        self.cors_allow_headers = CORS_ALLOW_HEADERS
        self.database_host = DATABASE_HOST
        self.database_port = DATABASE_PORT
        self.database_name = DATABASE_NAME
        self.database_user = DATABASE_USER
        self.database_password = DATABASE_PASSWORD
        self.log_level = LOG_LEVEL
        self.log_format = LOG_FORMAT

settings = Settings()
