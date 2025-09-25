"""
Configuration Management for MoMo Data Processing System
Enhanced with environment variables and production settings
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings with environment variable support."""
    
    # API Configuration
    API_PREFIX: str = "/api"
    TITLE: str = "MoMo Data Processing API"
    DESCRIPTION: str = "Enhanced API for Mobile Money SMS Data Processing with DSA Implementation"
    VERSION: str = "2.0.0"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Server Configuration
    HOST: str = os.getenv("API_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "momo_sms_processing")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_UNIX_SOCKET: str = os.getenv("DB_UNIX_SOCKET", "/tmp/mysql.sock")
    
    # Authentication Configuration
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "password")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ETL Configuration
    ETL_LOG_LEVEL: str = os.getenv("ETL_LOG_LEVEL", "INFO")
    ETL_BATCH_SIZE: int = int(os.getenv("ETL_BATCH_SIZE", "1000"))
    ETL_MAX_RETRIES: int = int(os.getenv("ETL_MAX_RETRIES", "3"))
    
    # File Processing
    DATA_RAW_DIR: str = os.getenv("DATA_RAW_DIR", "data/raw")
    DATA_PROCESSED_DIR: str = os.getenv("DATA_PROCESSED_DIR", "data/processed")
    DATA_LOGS_DIR: str = os.getenv("DATA_LOGS_DIR", "data/logs")
    
    # Performance Configuration
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "10"))
    CONNECTION_TIMEOUT: int = int(os.getenv("CONNECTION_TIMEOUT", "30"))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", "60"))
    
    # Export Configuration
    EXPORT_FORMATS: List[str] = ["json", "csv", "xlsx"]
    EXPORT_MAX_RECORDS: int = int(os.getenv("EXPORT_MAX_RECORDS", "10000"))
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'database': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'unix_socket': self.DB_UNIX_SOCKET,
            'autocommit': True,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'connection_timeout': self.CONNECTION_TIMEOUT,
            'sql_mode': 'TRADITIONAL'
        }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

# Global settings instance
settings = Settings()

# Response templates
SUCCESS_RESPONSE = {
    "success": True,
    "message": "Operation completed successfully",
    "timestamp": None,
    "data": None
}

ERROR_RESPONSE = {
    "success": False,
    "message": "An error occurred",
    "error_code": 500,
    "timestamp": None,
    "path": None
}

VALIDATION_ERROR_RESPONSE = {
    "success": False,
    "message": "Validation error",
    "error_code": 422,
    "timestamp": None,
    "path": None,
    "details": None
}