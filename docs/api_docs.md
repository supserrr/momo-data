# REST API Documentation
## MoMo SMS Data Processing System

**Team 11 - Enterprise Web Development**  
**API Implementation and Security Analysis**

---

## Overview

This REST API provides secure access to mobile money SMS transaction data. The API implements CRUD operations with Basic Authentication and includes Data Structures & Algorithms demonstrations for performance analysis.

**Base URL:** `http://localhost:8080`  
**Authentication:** Basic Authentication (admin:password)

---

## Authentication

All endpoints require Basic Authentication. Include the Authorization header in your requests:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Credentials:**
- Username: `admin`
- Password: `password`

**Error Response (401 Unauthorized):**
```json
{
  "error": true,
  "message": "Unauthorized: Invalid credentials"
}
```

---

## Endpoints

### 1. List All Transactions

**Endpoint:** `GET /transactions`  
**Description:** Retrieve all SMS transactions  
**Authentication:** Required

**Request Example:**
```bash
curl -u admin:password http://localhost:8080/transactions
```

**Response Example:**
```json
{
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
      "date": "2024-01-01T10:00:00",
      "original_message": "Sample transaction message"
    }
  ]
}
```

**Error Codes:**
- `401` - Unauthorized (invalid credentials)
- `500` - Internal server error

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

## Data Structures & Algorithms (DSA) Endpoints

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

## Error Handling

All endpoints return consistent error responses:

**Error Response Format:**
```json
{
  "error": true,
  "message": "Error description"
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication required)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server-side error)

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

1. Set Base URL: `http://localhost:8080`
2. Go to Authorization tab
3. Select "Basic Auth"
4. Username: `admin`
5. Password: `password`
6. Make requests to endpoints

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
