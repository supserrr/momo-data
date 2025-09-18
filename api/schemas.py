"""
API Data Models
Team 11 - Enterprise Web Development
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"

class TransactionCategory(str, Enum):
    """Transaction category enumeration."""
    # Enhanced categories from parser
    TRANSFER_INCOMING = "TRANSFER_INCOMING"
    TRANSFER_OUTGOING = "TRANSFER_OUTGOING"
    PAYMENT_PERSONAL = "PAYMENT_PERSONAL"
    PAYMENT_BUSINESS = "PAYMENT_BUSINESS"
    DEPOSIT_AGENT = "DEPOSIT_AGENT"
    DEPOSIT_CASH = "DEPOSIT_CASH"
    DEPOSIT_BANK_TRANSFER = "DEPOSIT_BANK_TRANSFER"
    DEPOSIT_OTHER = "DEPOSIT_OTHER"
    AIRTIME = "AIRTIME"
    DATA_BUNDLE = "DATA_BUNDLE"
    # Legacy categories for backward compatibility
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    QUERY = "QUERY"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

class TransactionType(str, Enum):
    """Transaction type enumeration."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    RECEIVE = "RECEIVE"
    QUERY = "QUERY"
    AIRTIME = "AIRTIME"
    DATA_BUNDLE = "DATA_BUNDLE"
    PURCHASE = "PURCHASE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

class TransactionBase(BaseModel):
    """Base transaction model."""
    amount: float = Field(..., description="Transaction amount", gt=0)
    phone: Optional[str] = Field(None, description="Phone number", min_length=10, max_length=15)
    date: Optional[str] = Field(None, description="Transaction date (ISO format)")
    reference: Optional[str] = Field(None, description="Transaction reference")
    type: Optional[str] = Field(None, description="Transaction type")
    status: Optional[str] = Field(None, description="Transaction status")
    category: Optional[str] = Field(None, description="Transaction category")
    category_description: Optional[str] = Field(None, description="Detailed description of the transaction category")
    category_confidence: Optional[float] = Field(None, description="Category confidence score", ge=0, le=1)

class TransactionCreate(TransactionBase):
    """Model for creating a new transaction."""
    pass

class TransactionUpdate(BaseModel):
    """Model for updating a transaction."""
    amount: Optional[float] = Field(None, description="Transaction amount", gt=0)
    phone: Optional[str] = Field(None, description="Phone number", min_length=10, max_length=15)
    date: Optional[str] = Field(None, description="Transaction date (ISO format)")
    reference: Optional[str] = Field(None, description="Transaction reference")
    type: Optional[str] = Field(None, description="Transaction type")
    status: Optional[str] = Field(None, description="Transaction status")
    category: Optional[str] = Field(None, description="Transaction category")
    category_description: Optional[str] = Field(None, description="Detailed description of the transaction category")
    category_confidence: Optional[float] = Field(None, description="Category confidence score", ge=0, le=1)

class Transaction(TransactionBase):
    """Complete transaction model."""
    id: int = Field(..., description="Transaction ID")
    personal_id: Optional[str] = Field(None, description="Personal ID")
    
    # Enhanced parser fields
    transaction_type: Optional[str] = Field(None, description="Transaction type")
    direction: Optional[str] = Field(None, description="Transaction direction (credit/debit)")
    sender_name: Optional[str] = Field(None, description="Sender name")
    sender_phone: Optional[str] = Field(None, description="Sender phone number")
    recipient_name: Optional[str] = Field(None, description="Recipient name")
    recipient_phone: Optional[str] = Field(None, description="Recipient phone number")
    momo_code: Optional[str] = Field(None, description="Momo code")
    sender_momo_id: Optional[str] = Field(None, description="Sender momo ID")
    agent_momo_number: Optional[str] = Field(None, description="Agent momo number")
    business_name: Optional[str] = Field(None, description="Business name")
    new_balance: Optional[float] = Field(None, description="New balance after transaction")
    confidence_score: Optional[float] = Field(None, description="Parser confidence score")
    financial_transaction_id: Optional[str] = Field(None, description="Financial transaction ID")
    
    # Original data
    original_data: Optional[str] = Field(None, description="Original raw data")
    original_message: Optional[str] = Field(None, description="Original SMS message")
    raw_data: Optional[str] = Field(None, description="Raw XML data")
    xml_tag: Optional[str] = Field(None, description="XML tag name")
    xml_attributes: Optional[Dict[str, Any]] = Field(None, description="XML attributes")
    cleaned_at: Optional[str] = Field(None, description="Data cleaning timestamp")
    categorized_at: Optional[str] = Field(None, description="Categorization timestamp")
    loaded_at: Optional[str] = Field(None, description="Database loading timestamp")

    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    """Transaction summary statistics."""
    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: float = Field(..., description="Total transaction amount")
    avg_amount: float = Field(..., description="Average transaction amount")
    successful_transactions: int = Field(..., description="Number of successful transactions")
    failed_transactions: int = Field(..., description="Number of failed transactions")
    success_rate: float = Field(..., description="Success rate percentage")

class CategoryStats(BaseModel):
    """Category statistics model."""
    category: str = Field(..., description="Transaction category")
    count: int = Field(..., description="Number of transactions")
    total_amount: float = Field(..., description="Total amount for category")
    avg_amount: float = Field(..., description="Average amount for category")
    min_amount: float = Field(..., description="Minimum amount for category")
    max_amount: float = Field(..., description="Maximum amount for category")
    last_updated: str = Field(..., description="Last update timestamp")

class AmountDistribution(BaseModel):
    """Amount distribution model."""
    amount_range: str = Field(..., description="Amount range")
    count: int = Field(..., description="Number of transactions in range")

class DashboardData(BaseModel):
    """Dashboard data model."""
    summary: TransactionSummary = Field(..., description="Transaction summary")
    categories: List[CategoryStats] = Field(..., description="Category statistics")
    amount_distribution: List[AmountDistribution] = Field(..., description="Amount distribution")
    recent_transactions: List[Transaction] = Field(..., description="Recent transactions")

class AnalyticsData(BaseModel):
    """Analytics data model."""
    daily_data: List[Dict[str, Any]] = Field(..., description="Daily transaction data")
    category_performance: List[Dict[str, Any]] = Field(..., description="Category performance")
    phone_analysis: List[Dict[str, Any]] = Field(..., description="Phone number analysis")

class ETLProcessLog(BaseModel):
    """ETL process log model."""
    id: int = Field(..., description="Log ID")
    process_name: str = Field(..., description="Process name")
    status: str = Field(..., description="Process status")
    records_processed: int = Field(..., description="Number of records processed")
    records_successful: int = Field(..., description="Number of successful records")
    records_failed: int = Field(..., description="Number of failed records")
    start_time: Optional[str] = Field(None, description="Process start time")
    end_time: Optional[str] = Field(None, description="Process end time")
    error_message: Optional[str] = Field(None, description="Error message if any")
    created_at: str = Field(..., description="Log creation timestamp")

class DatabaseStats(BaseModel):
    """Database statistics model."""
    transaction_count: int = Field(..., description="Total transaction count")
    log_count: int = Field(..., description="Total log count")
    stats_count: int = Field(..., description="Total stats count")
    database_size_bytes: int = Field(..., description="Database size in bytes")
    database_size_mb: float = Field(..., description="Database size in MB")

class TransactionFilters(BaseModel):
    """Transaction filters model."""
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by status")
    phone: Optional[str] = Field(None, description="Filter by phone number")
    start_date: Optional[str] = Field(None, description="Start date filter (ISO format)")
    end_date: Optional[str] = Field(None, description="End date filter (ISO format)")

class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., description="Search query", min_length=1, max_length=100)
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)

class ETLRunRequest(BaseModel):
    """ETL run request model."""
    xml_file: Optional[str] = Field(None, description="Path to XML file")
    export_json: bool = Field(True, description="Whether to export dashboard JSON")
    dry_run: bool = Field(False, description="Whether to run in dry-run mode")

class ETLRunResponse(BaseModel):
    """ETL run response model."""
    status: str = Field(..., description="ETL process status")
    message: Optional[str] = Field(None, description="Status message")
    duration_seconds: Optional[float] = Field(None, description="Process duration")
    total_processed: Optional[int] = Field(None, description="Total records processed")
    final_loaded: Optional[int] = Field(None, description="Final loaded records")

class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
