# JSON Schema Mapping Documentation

## Overview

This document outlines the mapping between our SQL database tables and JSON representations for the MoMo SMS data processing system. We designed these JSON schemas for API responses and data serialization.

## Table to JSON Mapping

### 1. Users Table → User JSON Schema

**SQL Table:** `users`
**JSON Schema:** `user_schema.json`

| SQL Column | JSON Field | Type | Description |
|------------|------------|------|-------------|
| user_id | user_id | integer | Primary key |
| phone_number | phone_number | string | Normalized phone number |
| display_name | display_name | string | User's display name |
| account_status | account_status | string | Account status enum |
| registration_date | registration_date | string (ISO 8601) | Registration timestamp |
| last_transaction_date | last_transaction_date | string (ISO 8601) | Last transaction timestamp |
| total_transactions | total_transactions | integer | Total transaction count |
| total_amount_sent | total_amount_sent | decimal | Total amount sent |
| total_amount_received | total_amount_received | decimal | Total amount received |
| created_at | created_at | string (ISO 8601) | Creation timestamp |
| updated_at | updated_at | string (ISO 8601) | Last update timestamp |
| - | metadata | object | Additional user metadata |

### 2. Transaction_Categories Table → Category JSON Schema

**SQL Table:** `transaction_categories`
**JSON Schema:** `transaction_category_schema.json`

| SQL Column | JSON Field | Type | Description |
|------------|------------|------|-------------|
| category_id | category_id | integer | Primary key |
| category_name | category_name | string | Category name |
| category_code | category_code | string | Short code |
| description | description | string | Category description |
| is_active | is_active | boolean | Active status |
| created_at | created_at | string (ISO 8601) | Creation timestamp |
| updated_at | updated_at | string (ISO 8601) | Last update timestamp |
| - | rules | object | Categorization rules |
| - | statistics | object | Category statistics |

### 3. Transactions Table → Transaction JSON Schema

**SQL Table:** `transactions`
**JSON Schema:** `transaction_schema.json`

| SQL Column | JSON Field | Type | Description |
|------------|------------|------|-------------|
| transaction_id | transaction_id | integer | Primary key |
| external_transaction_id | external_transaction_id | string | External system ID |
| sender_user_id | sender.user_id | integer | Sender user ID (nested) |
| receiver_user_id | receiver.user_id | integer | Receiver user ID (nested) |
| amount | amount | decimal | Transaction amount |
| fee | fee | decimal | Transaction fee |
| currency | currency | string | Currency code |
| transaction_date | transaction_date | string (ISO 8601) | Transaction timestamp |
| category_id | category.category_id | integer | Category ID (nested) |
| status | status | string | Transaction status |
| reference_number | reference_number | string | Transaction reference |
| description | description | string | Transaction description |
| raw_sms_data | raw_sms_data | string | Original SMS content |
| xml_attributes | xml_attributes | object | XML attributes (JSON) |
| processing_metadata | processing_metadata | object | ETL processing info (JSON) |
| created_at | created_at | string (ISO 8601) | Creation timestamp |
| updated_at | updated_at | string (ISO 8601) | Last update timestamp |

### 4. System_Logs Table → System Log JSON Schema

**SQL Table:** `system_logs`
**JSON Schema:** `system_log_schema.json`

| SQL Column | JSON Field | Type | Description |
|------------|------------|------|-------------|
| log_id | log_id | integer | Primary key |
| process_name | process_name | string | Process identifier |
| log_level | log_level | string | Log level enum |
| message | message | string | Log message |
| details | details | object | Additional details (JSON) |
| records_processed | records_processed | integer | Records processed |
| records_successful | records_successful | integer | Successful records |
| records_failed | records_failed | integer | Failed records |
| execution_time_seconds | execution_time_seconds | decimal | Execution time |
| created_at | created_at | string (ISO 8601) | Creation timestamp |
| - | error_details | object | Error details (if applicable) |

### 5. Transaction_Statistics Table → Statistics JSON Schema

**SQL Table:** `transaction_statistics`
**JSON Schema:** `transaction_statistics_schema.json`

| SQL Column | JSON Field | Type | Description |
|------------|------------|------|-------------|
| stat_id | stat_id | integer | Primary key |
| stat_type | stat_type | string | Statistic type |
| stat_period | stat_period | string | Time period |
| stat_date | stat_date | string (ISO 8601) | Statistic date |
| category_id | category.category_id | integer | Category ID (nested) |
| user_id | user.user_id | integer | User ID (nested) |
| transaction_count | transaction_count | integer | Transaction count |
| total_amount | total_amount | decimal | Total amount |
| average_amount | average_amount | decimal | Average amount |
| min_amount | min_amount | decimal | Minimum amount |
| max_amount | max_amount | decimal | Maximum amount |
| success_rate | success_rate | decimal | Success rate percentage |
| created_at | created_at | string (ISO 8601) | Creation timestamp |
| updated_at | updated_at | string (ISO 8601) | Last update timestamp |
| - | breakdown | object | Detailed breakdown |

## Complex JSON Objects

### Complete Transaction Example

The `complete_transaction_example.json` demonstrates how to serialize a complete transaction with all related data:

1. **Transaction Details** - Core transaction information
2. **Sender Information** - Complete sender user data with risk profile
3. **Receiver Information** - Complete receiver user data with risk profile
4. **Category Information** - Transaction category with rules and statistics
5. **Related Transactions** - Array of related transactions
6. **System Logs** - Processing logs for the transaction
7. **Statistics** - Daily and user-specific statistics
8. **API Metadata** - Request/response metadata

## Serialization Guidelines

### 1. Date/Time Formatting
- All timestamps use ISO 8601 format: `YYYY-MM-DDTHH:mm:ssZ`
- Timezone is always UTC (Z suffix)
- Example: `2024-05-10T16:30:51Z`

### 2. Decimal Precision
- Monetary amounts use 2 decimal places
- Example: `2000.00`
- Percentages use 2 decimal places
- Example: `95.56`

### 3. Nested Objects
- Foreign key relationships are resolved into nested objects
- Example: `category_id` becomes `category: { category_id: 1, category_name: "Transfer" }`

### 4. JSON Field Handling
- SQL JSON columns are parsed into native JSON objects
- Example: `xml_attributes` JSON column becomes `xml_attributes` object

### 5. Null Value Handling
- Null values are omitted from JSON responses
- Use `null` for explicitly null values
- Use empty objects `{}` for empty relationships

## API Response Patterns

### Single Entity Response
```json
{
  "success": true,
  "data": { /* entity object */ },
  "timestamp": "2024-05-10T16:30:51Z"
}
```

### Collection Response
```json
{
  "success": true,
  "data": {
    "items": [ /* array of entities */ ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 1000,
      "pages": 20
    }
  },
  "timestamp": "2024-05-10T16:30:51Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid phone number format",
    "details": { /* error details */ }
  },
  "timestamp": "2024-05-10T16:30:51Z"
}
```

## Performance Considerations

1. **Lazy Loading** - Only load related data when requested
2. **Pagination** - Limit large result sets
3. **Field Selection** - Allow clients to specify required fields
4. **Caching** - Cache frequently accessed data
5. **Compression** - Use gzip compression for large responses

## Security Considerations

1. **Data Masking** - Mask sensitive information in logs
2. **Access Control** - Implement proper authorization
3. **Audit Trail** - Log all data access
4. **Encryption** - Encrypt sensitive data in transit and at rest
5. **Rate Limiting** - Implement API rate limiting
