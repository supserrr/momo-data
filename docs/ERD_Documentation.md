# Entity Relationship Diagram (ERD) Documentation

## Design Overview

For our MoMo SMS data processing system, we implemented a fully normalized database schema following Third Normal Form (3NF) principles. Our design prioritizes data integrity, referential consistency, and scalability while providing comprehensive transaction processing and analytics capabilities.

## Core Entities and Relationships

### 1. Users (Primary Entity)
The **Users** entity stores customer information with comprehensive account management features. Each user has a unique phone number, account status, and aggregated transaction statistics. This entity serves as the foundation for all user-related operations and maintains referential integrity with transactions.

**Key Attributes:**
- `user_id` (Primary Key)
- `phone_number` (Unique, indexed)
- `display_name`, `account_status`
- `registration_date`, `last_transaction_date`
- Aggregated statistics: `total_transactions`, `total_amount_sent`, `total_amount_received`

### 2. Transaction_Categories (Lookup Entity)
The **Transaction_Categories** entity provides a normalized approach to transaction classification. This entity supports dynamic category management and ensures consistent categorization across the system.

**Key Attributes:**
- `category_id` (Primary Key)
- `category_name`, `category_code` (Unique)
- `description`, `is_active`
- Audit timestamps: `created_at`, `updated_at`

### 3. Tags (Classification Entity)
The **Tags** entity enables flexible transaction labeling and classification. This entity supports many-to-many relationships with transactions, allowing for complex categorization and filtering.

**Key Attributes:**
- `tag_id` (Primary Key)
- `tag_name` (Unique)
- `tag_description`, `tag_color`
- `is_active` status

### 4. Transactions (Central Entity)
The **Transactions** entity is the heart of our system, capturing all transaction details with proper normalization. This entity maintains referential integrity with users, categories, and tags through foreign key relationships.

**Key Attributes:**
- `transaction_id` (Primary Key)
- `external_transaction_id` (Unique)
- Foreign Keys: `sender_user_id`, `receiver_user_id`, `category_id`
- Core transaction data: `amount`, `fee`, `currency`, `transaction_date`
- Status and metadata: `status`, `reference_number`, `description`
- Processing data: `raw_sms_data`, `xml_attributes` (JSON), `processing_metadata` (JSON)

### 5. Transaction_Tags (Junction Table - Many-to-Many)
The **Transaction_Tags** junction table implements the many-to-many relationship between transactions and tags. This design allows transactions to have multiple tags and tags to be applied to multiple transactions.

**Key Attributes:**
- Composite Primary Key: `transaction_id`, `tag_id`
- `assigned_at` timestamp
- `assigned_by` (Foreign Key to Users)

### 6. User_Preferences (Junction Table - Many-to-Many)
The **User_Preferences** junction table implements the many-to-many relationship between users and transaction categories. This design allows users to have preferences for multiple categories and categories to be preferred by multiple users.

**Key Attributes:**
- Composite Primary Key: `user_id`, `category_id`, `preference_type`
- `preference_type` enum: 'FAVORITE', 'BLOCKED', 'NOTIFICATION'

### 7. System_Logs (Audit Entity)
The **System_Logs** entity provides comprehensive audit trails for all system operations. This entity tracks ETL processes, errors, and performance metrics.

**Key Attributes:**
- `log_id` (Primary Key)
- `process_name`, `log_level`, `message`
- Performance metrics: `records_processed`, `records_successful`, `records_failed`
- `execution_time_seconds`, `details` (JSON)

### 8. Transaction_Statistics (Analytics Entity)
The **Transaction_Statistics** entity provides pre-calculated statistics for performance optimization. This entity supports multi-dimensional analysis across users, categories, and tags.

**Key Attributes:**
- `stat_id` (Primary Key)
- `stat_type`, `stat_period`, `stat_date`
- Foreign Keys: `category_id`, `user_id`, `tag_id`
- Statistical data: `transaction_count`, `total_amount`, `average_amount`, `min_amount`, `max_amount`, `success_rate`

## Design Decisions

### Normalization Strategy
**Third Normal Form (3NF) Compliance**: Our design eliminates data redundancy by properly normalizing all entities. This approach ensures data consistency, reduces storage requirements, and simplifies maintenance.

**Referential Integrity**: We implement comprehensive foreign key constraints to maintain data consistency across all relationships. This ensures that orphaned records cannot exist and maintains data quality.

### Many-to-Many Relationships
**Transaction-Tag Relationship**: The `transaction_tags` junction table allows transactions to be tagged with multiple labels (e.g., "High Value", "Business", "Verified"). This provides flexible categorization beyond the primary category system.

**User-Category Preferences**: The `user_preferences` junction table allows users to set preferences for multiple transaction categories (favorites, blocked categories, notification preferences). This supports personalized user experiences.

### Performance Optimization
**Strategic Indexing**: We implement comprehensive indexing strategies including:
- Primary key indexes on all entities
- Unique indexes on business keys (phone_number, external_transaction_id)
- Composite indexes for common query patterns
- Foreign key indexes for join performance

**Pre-calculated Statistics**: The `transaction_statistics` table provides pre-calculated analytics to support real-time dashboard performance without expensive aggregations.

### Data Integrity
**Check Constraints**: We implement comprehensive check constraints to ensure data quality:
- Phone number length validation
- Amount positivity checks
- Date range validations
- Enum value constraints

**JSON Data Handling**: We use MySQL's native JSON data type for flexible metadata storage while maintaining queryability and indexing capabilities.

### Scalability Considerations
**Horizontal Scaling**: The normalized design supports horizontal scaling through proper partitioning strategies on date-based columns.

**Audit Trail**: Comprehensive logging and statistics tables provide full audit capabilities and support compliance requirements.

**Flexible Metadata**: JSON columns allow for schema evolution without structural changes to core tables.

## Relationship Cardinalities

1. **Users ↔ Transactions**: One-to-Many (1:M)
   - One user can have many transactions (as sender or receiver)
   - Each transaction has at most one sender and one receiver

2. **Transaction_Categories ↔ Transactions**: One-to-Many (1:M)
   - One category can have many transactions
   - Each transaction belongs to at most one category

3. **Transactions ↔ Tags**: Many-to-Many (M:N)
   - One transaction can have many tags
   - One tag can be applied to many transactions
   - Resolved through `transaction_tags` junction table

4. **Users ↔ Transaction_Categories**: Many-to-Many (M:N)
   - One user can have preferences for many categories
   - One category can be preferred by many users
   - Resolved through `user_preferences` junction table

5. **Users ↔ Transaction_Statistics**: One-to-Many (1:M)
   - One user can have many statistics records
   - Each statistic record belongs to at most one user

6. **Transaction_Categories ↔ Transaction_Statistics**: One-to-Many (1:M)
   - One category can have many statistics records
   - Each statistic record belongs to at most one category

7. **Tags ↔ Transaction_Statistics**: One-to-Many (1:M)
   - One tag can have many statistics records
   - Each statistic record belongs to at most one tag

This normalized database design provides a robust, scalable foundation for our MoMo SMS processing system while maintaining data integrity and supporting complex analytical queries.
