# REST API Documentation
## MoMo SMS Data Processing System

**Team 11 - Enterprise Web Development**  
**API Implementation and Security Analysis**

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Core Endpoints](#core-endpoints)
5. [Dashboard & Analytics](#dashboard--analytics)
6. [Search & Filtering](#search--filtering)
7. [Data Structures & Algorithms](#data-structures--algorithms)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Testing Examples](#testing-examples)
11. [Security Considerations](#security-considerations)
12. [Performance Analysis](#performance-analysis)
13. [API Versioning](#api-versioning)
14. [Setup Instructions](#setup-instructions)

---

## Overview

This REST API provides secure access to mobile money SMS transaction data. The API implements comprehensive CRUD operations with Basic Authentication and includes Data Structures & Algorithms demonstrations for performance analysis.

### Key Features

- **Complete CRUD Operations**: Create, Read, Update, Delete transactions
- **Advanced Filtering**: Filter by category, status, date range, amount, phone number
- **Search Functionality**: Full-text search across transaction data
- **Analytics & Dashboard**: Comprehensive analytics and dashboard data
- **DSA Demonstrations**: Linear search vs Dictionary lookup performance comparison
- **Export Capabilities**: Export data in JSON and CSV formats
- **Real-time Data**: Live transaction data from XML processing
- **Comprehensive Logging**: ETL process logs and system monitoring

### API Information

**Base URL:** `http://localhost:8080`  
**API Version:** 2.0.0  
**Protocol:** HTTP/HTTPS  
**Data Format:** JSON  
**Authentication:** Basic Authentication (admin:password)  
**Content-Type:** `application/json`

### Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": true,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

## Getting Started

### Quick Start

1. **Start the API Server:**
   ```bash
   python api/momo_api_server.py --port 8080
   ```

2. **Test Authentication:**
   ```bash
   curl -u admin:password http://localhost:8080/api/health
   ```

3. **Get All Transactions:**
   ```bash
   curl -u admin:password http://localhost:8080/api/transactions
   ```

### Prerequisites

- Python 3.8+
- MySQL 8.0+ (for database operations)
- Required Python packages (see `requirements.txt`)

### Environment Setup

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=momo_sms_processing
DB_USER=root
DB_PASSWORD=your_password

# API Configuration
API_HOST=127.0.0.1
API_PORT=8080
DEBUG=true
ENVIRONMENT=development

# Authentication
AUTH_USERNAME=admin
AUTH_PASSWORD=password
SECRET_KEY=your-secret-key-here
```

### API Client Setup

#### Using curl

```bash
# Set base URL and credentials
BASE_URL="http://localhost:8080"
USERNAME="admin"
PASSWORD="password"

# Test API health
curl -u $USERNAME:$PASSWORD $BASE_URL/api/health

# Get transactions
curl -u $USERNAME:$PASSWORD $BASE_URL/api/transactions
```

#### Using Python requests

```python
import requests
from requests.auth import HTTPBasicAuth

# API configuration
base_url = "http://localhost:8080"
auth = HTTPBasicAuth("admin", "password")

# Test API health
response = requests.get(f"{base_url}/api/health", auth=auth)
print(response.json())

# Get transactions
response = requests.get(f"{base_url}/api/transactions", auth=auth)
transactions = response.json()
```

#### Using JavaScript fetch

```javascript
// API configuration
const baseURL = 'http://localhost:8080';
const credentials = btoa('admin:password');

// Test API health
fetch(`${baseURL}/api/health`, {
  headers: {
    'Authorization': `Basic ${credentials}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Get transactions
fetch(`${baseURL}/api/transactions`, {
  headers: {
    'Authorization': `Basic ${credentials}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Authentication

### Authentication Method

All API endpoints require **Basic Authentication**. This is a simple authentication scheme built into the HTTP protocol.

### How to Authenticate

Include the Authorization header in your requests with your credentials encoded in Base64:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

### Default Credentials

**Username:** `admin`  
**Password:** `password`

> ⚠️ **Security Note:** These are default credentials for development. Change them in production!

### Generating Authorization Header

The Authorization header is generated by Base64 encoding the string `username:password`:

```bash
# Using command line
echo -n "admin:password" | base64
# Output: YWRtaW46cGFzc3dvcmQ=

# Using Python
import base64
credentials = base64.b64encode(b"admin:password").decode("utf-8")
print(credentials)  # YWRtaW46cGFzc3dvcmQ=
```

### Authentication Examples

#### curl
```bash
curl -u admin:password http://localhost:8080/api/transactions
```

#### Python requests
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    "http://localhost:8080/api/transactions",
    auth=HTTPBasicAuth("admin", "password")
)
```

#### JavaScript fetch
```javascript
const credentials = btoa('admin:password');
fetch('http://localhost:8080/api/transactions', {
  headers: {
    'Authorization': `Basic ${credentials}`
  }
});
```

#### Postman
1. Go to the **Authorization** tab
2. Select **Basic Auth**
3. Enter username: `admin`
4. Enter password: `password`

### Authentication Errors

**401 Unauthorized - Missing Credentials:**
```json
{
  "success": false,
  "error": true,
  "message": "Unauthorized: Authentication required",
  "error_code": "AUTH_REQUIRED",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**401 Unauthorized - Invalid Credentials:**
```json
{
  "success": false,
  "error": true,
  "message": "Unauthorized: Invalid credentials",
  "error_code": "AUTH_INVALID",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**401 Unauthorized - Malformed Header:**
```json
{
  "success": false,
  "error": true,
  "message": "Unauthorized: Malformed authorization header",
  "error_code": "AUTH_MALFORMED",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

## Core Endpoints

### Transaction Management

#### 1. List All Transactions

**Endpoint:** `GET /api/transactions` or `GET /transactions`  
**Description:** Retrieve all SMS transactions with optional filtering and pagination  
**Authentication:** Required  
**Rate Limit:** 100 requests/minute

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Maximum number of transactions to return (1-1000) |
| `offset` | integer | 0 | Number of transactions to skip for pagination |
| `category` | string | - | Filter by transaction category |
| `status` | string | - | Filter by transaction status |
| `phone` | string | - | Filter by phone number (partial match) |
| `transaction_type` | string | - | Filter by transaction type |
| `min_amount` | float | - | Minimum transaction amount |
| `max_amount` | float | - | Maximum transaction amount |
| `start_date` | string | - | Start date filter (YYYY-MM-DD) |
| `end_date` | string | - | End date filter (YYYY-MM-DD) |
| `sort_by` | string | date | Sort field (date, amount, status, category) |
| `sort_order` | string | DESC | Sort order (ASC, DESC) |

**Request Examples:**

```bash
# Get all transactions
curl -u admin:password http://localhost:8080/api/transactions

# Get first 10 transactions
curl -u admin:password "http://localhost:8080/api/transactions?limit=10"

# Filter by category and status
curl -u admin:password "http://localhost:8080/api/transactions?category=TRANSFER_OUTGOING&status=SUCCESS"

# Filter by date range and amount
curl -u admin:password "http://localhost:8080/api/transactions?start_date=2024-01-01&end_date=2024-01-31&min_amount=1000"

# Search by phone number
curl -u admin:password "http://localhost:8080/api/transactions?phone=+250788"

# Pagination
curl -u admin:password "http://localhost:8080/api/transactions?limit=20&offset=40"
```

**Response Example:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "amount": 1000.0,
      "currency": "RWF",
      "transaction_type": "TRANSFER",
      "category": "TRANSFER_OUTGOING",
      "direction": "debit",
      "status": "SUCCESS",
      "sender_name": "John Doe",
      "sender_phone": "+250788123456",
      "recipient_name": "Jane Smith",
      "recipient_phone": "+250789123456",
      "momo_code": "123456",
      "fee": 50.0,
      "new_balance": 5000.0,
      "transaction_id": "TXN001",
      "financial_transaction_id": "FT001",
      "external_transaction_id": "EXT001",
      "date": "2024-01-01T10:00:00",
      "original_message": "Sample transaction message",
      "confidence": 0.95,
      "xml_attributes": {},
      "processing_metadata": {},
      "loaded_at": "2024-01-01T10:05:00"
    }
  ],
  "message": "Transactions retrieved successfully",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique transaction identifier |
| `amount` | float | Transaction amount |
| `currency` | string | Currency code (RWF, UGX, etc.) |
| `transaction_type` | string | Type of transaction |
| `category` | string | Transaction category |
| `direction` | string | Transaction direction (credit/debit) |
| `status` | string | Transaction status |
| `sender_name` | string | Sender's name |
| `sender_phone` | string | Sender's phone number |
| `recipient_name` | string | Recipient's name |
| `recipient_phone` | string | Recipient's phone number |
| `momo_code` | string | MoMo transaction code |
| `fee` | float | Transaction fee |
| `new_balance` | float | Balance after transaction |
| `transaction_id` | string | Internal transaction ID |
| `financial_transaction_id` | string | Financial system transaction ID |
| `external_transaction_id` | string | External system transaction ID |
| `date` | string | Transaction date (ISO 8601) |
| `original_message` | string | Original SMS message |
| `confidence` | float | Parser confidence score (0-1) |
| `xml_attributes` | object | Original XML attributes |
| `processing_metadata` | object | ETL processing metadata |
| `loaded_at` | string | Database loading timestamp |

**Error Responses:**

**400 Bad Request - Invalid Parameters:**
```json
{
  "success": false,
  "error": true,
  "message": "Invalid query parameters",
  "error_code": "INVALID_PARAMS",
  "details": {
    "limit": "Must be between 1 and 1000"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "error": true,
  "message": "Unauthorized: Invalid credentials",
  "error_code": "AUTH_INVALID",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**429 Too Many Requests:**
```json
{
  "success": false,
  "error": true,
  "message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": true,
  "message": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

### 2. Get Specific Transaction

**Endpoint:** `GET /transactions/{id}`  
**Description:** Retrieve a specific transaction by ID  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password http://localhost:8080/transactions/1
```

**Response Example:**
```json
{
  "data": {
    "id": 1,
    "amount": 1000.0,
    "currency": "RWF",
    "transaction_type": "TRANSFER",
    "category": "TRANSFER_OUTGOING",
    "direction": "debit",
    "status": "SUCCESS",
    "sender_name": "John Doe",
    "sender_phone": "+250788123456",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+250789123456",
    "date": "2024-01-01T10:00:00",
    "original_message": "Sample transaction message"
  }
}
```

**Error Codes:**
- `400` - Invalid transaction ID
- `401` - Unauthorized (invalid credentials)
- `404` - Transaction not found
- `500` - Internal server error

---

### 3. Create New Transaction

**Endpoint:** `POST /transactions`  
**Description:** Create a new SMS transaction  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password -X POST http://localhost:8080/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.0,
    "currency": "RWF",
    "transaction_type": "DEPOSIT",
    "category": "DEPOSIT_AGENT",
    "direction": "credit",
    "status": "SUCCESS",
    "sender_name": "Agent",
    "sender_phone": "+250788654321",
    "recipient_name": "John Doe",
    "recipient_phone": "+250788123456",
    "date": "2024-01-01T12:00:00",
    "original_message": "Agent deposit"
  }'
```

**Response Example:**
```json
{
  "data": {
    "id": 3,
    "amount": 5000.0,
    "currency": "RWF",
    "transaction_type": "DEPOSIT",
    "category": "DEPOSIT_AGENT",
    "direction": "credit",
    "status": "SUCCESS",
    "sender_name": "Agent",
    "sender_phone": "+250788654321",
    "recipient_name": "John Doe",
    "recipient_phone": "+250788123456",
    "date": "2024-01-01T12:00:00",
    "original_message": "Agent deposit"
  },
  "message": "Transaction created successfully"
}
```

**Required Fields:**
- `amount` (number) - Transaction amount
- `currency` (string) - Currency code (e.g., "RWF")
- `transaction_type` (string) - Type of transaction

**Error Codes:**
- `400` - Invalid JSON data or missing required fields
- `401` - Unauthorized (invalid credentials)
- `500` - Internal server error

---

### 4. Update Transaction

**Endpoint:** `PUT /transactions/{id}`  
**Description:** Update an existing transaction  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password -X PUT http://localhost:8080/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.0,
    "status": "SUCCESS"
  }'
```

**Response Example:**
```json
{
  "data": {
    "id": 1,
    "amount": 1500.0,
    "currency": "RWF",
    "transaction_type": "TRANSFER",
    "category": "TRANSFER_OUTGOING",
    "direction": "debit",
    "status": "SUCCESS",
    "sender_name": "John Doe",
    "sender_phone": "+250788123456",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+250789123456",
    "date": "2024-01-01T10:00:00",
    "original_message": "Sample transaction message"
  },
  "message": "Transaction updated successfully"
}
```

**Error Codes:**
- `400` - Invalid JSON data or transaction ID
- `401` - Unauthorized (invalid credentials)
- `404` - Transaction not found
- `500` - Internal server error

---

### 5. Delete Transaction

**Endpoint:** `DELETE /transactions/{id}`  
**Description:** Delete a specific transaction  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password -X DELETE http://localhost:8080/transactions/1
```

**Response Example:**
```json
{
  "data": {
    "id": 1,
    "amount": 1000.0,
    "currency": "RWF",
    "transaction_type": "TRANSFER",
    "category": "TRANSFER_OUTGOING",
    "direction": "debit",
    "status": "SUCCESS",
    "sender_name": "John Doe",
    "sender_phone": "+250788123456",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+250789123456",
    "date": "2024-01-01T10:00:00",
    "original_message": "Sample transaction message"
  },
  "message": "Transaction deleted successfully"
}
```

**Error Codes:**
- `400` - Invalid transaction ID
- `401` - Unauthorized (invalid credentials)
- `404` - Transaction not found
- `500` - Internal server error

---

## Data Structures & Algorithms

### Performance Comparison Endpoints

The API includes specialized endpoints to demonstrate and compare different data structures and algorithms for transaction lookup, fulfilling the assignment requirements for DSA integration.

### 6. Linear Search Demonstration

**Endpoint:** `GET /dsa/linear-search?id={transaction_id}`  
**Description:** Demonstrate linear search algorithm for finding transactions by ID  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password "http://localhost:8080/dsa/linear-search?id=1"
```

**Response Example:**
```json
{
  "data": {
    "algorithm": "Linear Search",
    "target_id": 1,
    "found": true,
    "result": {
      "id": 1,
      "amount": 1000.0,
      "currency": "RWF",
      "transaction_type": "TRANSFER"
    },
    "execution_time_ms": 0.123,
    "comparisons": 1,
    "data_size": 100
  }
}
```

**Query Parameters:**
- `id` (required) - Transaction ID to search for

---

### 7. Dictionary Lookup Demonstration

**Endpoint:** `GET /dsa/dictionary-lookup?id={transaction_id}`  
**Description:** Demonstrate dictionary lookup for finding transactions by ID  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password "http://localhost:8080/dsa/dictionary-lookup?id=1"
```

**Response Example:**
```json
{
  "data": {
    "algorithm": "Dictionary Lookup",
    "target_id": 1,
    "found": true,
    "result": {
      "id": 1,
      "amount": 1000.0,
      "currency": "RWF",
      "transaction_type": "TRANSFER"
    },
    "execution_time_ms": 0.045,
    "comparisons": 1,
    "data_size": 100
  }
}
```

**Query Parameters:**
- `id` (required) - Transaction ID to search for

---

### 8. Performance Comparison

**Endpoint:** `GET /dsa/comparison`  
**Description:** Compare performance of linear search vs dictionary lookup  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password http://localhost:8080/dsa/comparison
```

**Response Example:**
```json
{
  "data": {
    "comparison": {
      "linear_search": {
        "avg_time_ms": 0.156,
        "min_time_ms": 0.123,
        "max_time_ms": 0.189,
        "total_time_ms": 3.12
      },
      "dictionary_lookup": {
        "avg_time_ms": 0.045,
        "min_time_ms": 0.032,
        "max_time_ms": 0.058,
        "total_time_ms": 0.90
      }
    },
    "data_size": 100,
    "test_count": 20,
    "analysis": {
      "dictionary_lookup_faster_by": "3.47x",
      "explanation": "Dictionary lookup is O(1) average case while linear search is O(n), making it significantly faster for large datasets."
    }
  }
}
```

---

## Rate Limiting

### Rate Limit Information

The API implements rate limiting to ensure fair usage and prevent abuse. Different endpoints have different rate limits based on their resource intensity.

### Rate Limits by Endpoint

| Endpoint Category | Rate Limit | Window |
|-------------------|------------|---------|
| Transaction CRUD | 50 requests/minute | Per IP |
| Transaction Listing | 100 requests/minute | Per IP |
| Dashboard & Analytics | 60 requests/minute | Per IP |
| Search & Filtering | 100 requests/minute | Per IP |
| DSA Demonstrations | 200 requests/minute | Per IP |
| Health & Info | 300 requests/minute | Per IP |

### Rate Limit Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

**429 Too Many Requests:**
```json
{
  "success": false,
  "error": true,
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_time": "2024-01-01T10:01:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Best Practices

1. **Implement Exponential Backoff:** If you receive a 429 response, wait before retrying
2. **Cache Responses:** Cache frequently accessed data to reduce API calls
3. **Batch Requests:** Combine multiple operations when possible
4. **Monitor Headers:** Check rate limit headers to avoid hitting limits

---

## Error Handling

### Error Response Format

All API endpoints return consistent error responses following this structure:

```json
{
  "success": false,
  "error": true,
  "message": "Human-readable error description",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### HTTP Status Codes

| Status Code | Description | Common Scenarios |
|-------------|-------------|------------------|
| `200` | OK | Successful GET, PUT requests |
| `201` | Created | Successful POST requests |
| `400` | Bad Request | Invalid JSON, missing required fields, validation errors |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Valid authentication but insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Resource already exists or conflict with current state |
| `422` | Unprocessable Entity | Valid JSON but invalid data values |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Service temporarily unavailable |

### Error Codes Reference

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `AUTH_INVALID` | 401 | Invalid credentials |
| `AUTH_MALFORMED` | 401 | Malformed authorization header |
| `INVALID_JSON` | 400 | Invalid JSON in request body |
| `MISSING_REQUIRED_FIELD` | 400 | Required field missing |
| `INVALID_PARAMS` | 400 | Invalid query parameters |
| `INVALID_ID` | 400 | Invalid resource ID format |
| `TRANSACTION_NOT_FOUND` | 404 | Transaction doesn't exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `DATABASE_ERROR` | 500 | Database connection or query error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Handling Examples

**400 Bad Request - Validation Error:**
```json
{
  "success": false,
  "error": true,
  "message": "Validation failed",
  "error_code": "INVALID_PARAMS",
  "details": {
    "amount": "Must be greater than 0",
    "currency": "Must be a valid currency code"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": true,
  "message": "Transaction with ID 999 not found",
  "error_code": "TRANSACTION_NOT_FOUND",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": true,
  "message": "An unexpected error occurred",
  "error_code": "INTERNAL_ERROR",
  "details": {
    "request_id": "req_123456789"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Error Handling Best Practices

1. **Always Check Status Codes:** Don't rely solely on the response body
2. **Handle Rate Limits:** Implement exponential backoff for 429 responses
3. **Validate Input:** Check for required fields and data types
4. **Log Errors:** Include request IDs for debugging
5. **User-Friendly Messages:** Display human-readable error messages to users

---

## API Versioning

### Version Information

**Current Version:** 2.0.0  
**API Base URL:** `http://localhost:8080`  
**Version Header:** `API-Version: 2.0.0`

### Versioning Strategy

The API uses URL-based versioning with backward compatibility:

- **Current Version:** `/api/v2/` (default)
- **Legacy Version:** `/api/v1/` (deprecated)
- **No Version:** `/api/` (defaults to current version)

### Version Headers

Include the API version in your requests:

```bash
curl -u admin:password \
  -H "API-Version: 2.0.0" \
  http://localhost:8080/api/transactions
```

### Breaking Changes

| Version | Breaking Changes | Migration Guide |
|---------|------------------|-----------------|
| 2.0.0 | Enhanced response format, new fields | Update response parsing |
| 1.0.0 | Initial release | N/A |

### Deprecation Policy

1. **6 months notice** before removing deprecated endpoints
2. **3 months notice** before removing deprecated fields
3. **Version headers** to specify API version
4. **Backward compatibility** maintained for at least 12 months

---

## Testing Examples

### Using curl

**List all transactions:**
```bash
curl -u admin:password http://localhost:8080/transactions
```

**Get specific transaction:**
```bash
curl -u admin:password http://localhost:8080/transactions/1
```

**Create new transaction:**
```bash
curl -u admin:password -X POST http://localhost:8080/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "currency": "RWF", "transaction_type": "TRANSFER"}'
```

**Update transaction:**
```bash
curl -u admin:password -X PUT http://localhost:8080/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"amount": 2000}'
```

**Delete transaction:**
```bash
curl -u admin:password -X DELETE http://localhost:8080/transactions/1
```

**Test unauthorized access:**
```bash
curl http://localhost:8080/transactions
```

### Using Postman

#### Setup

1. **Set Base URL:** `http://localhost:8080`
2. **Configure Authentication:**
   - Go to **Authorization** tab
   - Select **Basic Auth**
   - Username: `admin`
   - Password: `password`
3. **Set Headers:**
   - `Content-Type: application/json`
   - `Accept: application/json`

#### Postman Collection

Create a new collection with these requests:

**1. Health Check**
- Method: `GET`
- URL: `{{base_url}}/api/health`
- Description: Check API health status

**2. Get All Transactions**
- Method: `GET`
- URL: `{{base_url}}/api/transactions`
- Description: Retrieve all transactions

**3. Get Transaction by ID**
- Method: `GET`
- URL: `{{base_url}}/api/transactions/1`
- Description: Get specific transaction

**4. Create Transaction**
- Method: `POST`
- URL: `{{base_url}}/api/transactions`
- Body (raw JSON):
```json
{
  "amount": 1000.0,
  "currency": "RWF",
  "transaction_type": "TRANSFER",
  "category": "TRANSFER_OUTGOING",
  "direction": "debit",
  "status": "SUCCESS",
  "sender_name": "John Doe",
  "sender_phone": "+250788123456",
  "recipient_name": "Jane Smith",
  "recipient_phone": "+250789123456",
  "date": "2024-01-01T10:00:00",
  "original_message": "Test transaction"
}
```

**5. Update Transaction**
- Method: `PUT`
- URL: `{{base_url}}/api/transactions/1`
- Body (raw JSON):
```json
{
  "amount": 1500.0,
  "status": "SUCCESS"
}
```

**6. Delete Transaction**
- Method: `DELETE`
- URL: `{{base_url}}/api/transactions/1`

**7. Search Transactions**
- Method: `GET`
- URL: `{{base_url}}/api/search?q=John&limit=10`

**8. Get Dashboard Data**
- Method: `GET`
- URL: `{{base_url}}/api/dashboard-data`

**9. DSA Linear Search**
- Method: `GET`
- URL: `{{base_url}}/dsa/linear-search?id=1`

**10. DSA Dictionary Lookup**
- Method: `GET`
- URL: `{{base_url}}/dsa/dictionary-lookup?id=1`

**11. DSA Performance Comparison**
- Method: `GET`
- URL: `{{base_url}}/dsa/comparison`

#### Environment Variables

Create a Postman environment with:
- `base_url`: `http://localhost:8080`
- `username`: `admin`
- `password`: `password`

---

## Security Considerations

### Basic Authentication Limitations

**Why Basic Auth is Weak:**
1. **Credentials in Plain Text:** Base64 encoding is easily decoded
2. **No Session Management:** Credentials sent with every request
3. **No Token Expiration:** Credentials remain valid until changed
4. **Vulnerable to Man-in-the-Middle:** No encryption of credentials
5. **No Multi-Factor Authentication:** Single factor authentication only

**Stronger Alternatives:**
1. **JWT (JSON Web Tokens):** Stateless, secure token-based authentication
2. **OAuth 2.0:** Industry standard for authorization
3. **API Keys:** Unique keys for each client
4. **Certificate-based Authentication:** Mutual TLS authentication
5. **Multi-Factor Authentication:** Additional security layers

### Recommended Security Improvements

1. **Use HTTPS:** Encrypt all communications
2. **Implement JWT:** Token-based authentication with expiration
3. **Rate Limiting:** Prevent abuse and DoS attacks
4. **Input Validation:** Sanitize all inputs
5. **Audit Logging:** Track all API access
6. **CORS Configuration:** Restrict cross-origin requests
7. **API Versioning:** Maintain backward compatibility

---

## Performance Analysis

### DSA Comparison Results

**Linear Search (O(n) complexity):**
- Time complexity: O(n) where n is the number of transactions
- Space complexity: O(1)
- Best case: O(1) - element at first position
- Worst case: O(n) - element at last position or not found
- Average case: O(n/2)

**Dictionary Lookup (O(1) complexity):**
- Time complexity: O(1) average case, O(n) worst case (hash collisions)
- Space complexity: O(n) - requires additional memory for hash table
- Best case: O(1) - no collisions
- Worst case: O(n) - all elements hash to same bucket
- Average case: O(1)

**Performance Improvement:**
Dictionary lookup is typically **3-5x faster** than linear search for datasets with 20+ records, with the performance gap increasing significantly as dataset size grows.

**Recommendation:**
For production systems with large datasets, use hash tables or database indexes for O(1) or O(log n) lookup performance instead of linear search.

---

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the REST API Server:**
   ```bash
   python api/plain_rest_api.py --port 8080
   ```

3. **Test the API:**
   ```bash
   curl -u admin:password http://localhost:8080/transactions
   ```

4. **Access DSA Endpoints:**
   ```bash
   curl -u admin:password http://localhost:8080/dsa/comparison
   ```

---

## Conclusion

This REST API provides a secure interface for accessing mobile money SMS transaction data. The implementation includes CRUD operations, Basic Authentication, and DSA demonstrations showing performance differences between linear search and dictionary lookup algorithms.

The API demonstrates fundamental concepts in web API development, security, and algorithm performance analysis.
