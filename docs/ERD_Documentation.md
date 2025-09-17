# Entity Relationship Diagram (ERD) Documentation

## Design Overview

For our MoMo SMS data processing system, we designed a database around five core entities that capture the complete transaction lifecycle and system monitoring requirements. Our design prioritizes data integrity, query performance, and scalability while maintaining flexibility for future enhancements.

## Core Entities and Relationships

### 1. Users (1:M with Transactions)
We designed the **Users** entity as the central hub for all customer information, storing both sender and receiver data. This approach eliminates data redundancy by maintaining a single user record that can participate in multiple transactions. We included comprehensive user statistics (total transactions, amounts sent/received) to support real-time analytics without complex aggregations.

### 2. Transaction_Categories (1:M with Transactions)
The **Transaction_Categories** entity provides a flexible categorization system that can evolve with business requirements. We used a normalized approach that allows for easy addition of new transaction types and supports rule-based categorization logic. The many-to-one relationship with transactions enables efficient filtering and reporting by transaction type.

### 3. Transactions (Central Entity)
The **Transactions** entity is the heart of our system, capturing all transaction details with full audit trails. Our design includes both sender and receiver foreign keys to the Users table, supporting bidirectional transaction queries. We used JSON fields for `xml_attributes` and `processing_metadata` to provide flexibility for storing variable transaction data without schema changes.

### 4. System_Logs (Independent Entity)
The **System_Logs** entity operates independently to track ETL processes and system health. We separated this to ensure that logging doesn't impact transaction performance while providing comprehensive audit trails for data processing operations.

### 5. Transaction_Statistics (Aggregated Data)
The **Transaction_Statistics** entity implements a denormalized approach for performance optimization. By pre-calculating common analytics queries, our system can deliver real-time dashboard performance without expensive aggregations on large transaction datasets.

## Design Decisions

**Normalization Strategy**: Our design follows 3NF principles while strategically denormalizing the statistics table for performance. This hybrid approach balances data integrity with query efficiency.

**Relationship Cardinality**: We used appropriate cardinalities (1:M, M:N) with proper foreign key constraints. Our design includes several many-to-many relationships:

- **Users ↔ Transactions (M:N)**: A user can participate in many transactions as sender or receiver, and each transaction involves multiple users. This M:N relationship is resolved through foreign keys (`sender_user_id`, `receiver_user_id`) in the transactions table.
- **Users ↔ Categories (M:N through Transactions)**: Users can have transactions in multiple categories, and categories can involve multiple users. This indirect M:N relationship is resolved through the transactions table as a junction table.

This approach avoids unnecessary junction tables while maintaining proper normalization and referential integrity.

**Performance Optimization**: We implemented strategic indexing on frequently queried columns (transaction_date, user_id, status) to ensure sub-second response times even with large datasets. Composite indexes support complex analytical queries.

**Data Integrity**: We added comprehensive CHECK constraints to validate data quality at the database level, while triggers maintain referential integrity and automatically update user statistics.

**Scalability**: Our design supports horizontal scaling through sharding strategies and includes JSON fields for flexible metadata storage without schema migrations.

This database design provides a robust foundation for our MoMo SMS processing system while maintaining the flexibility to adapt to evolving business requirements and data volumes.
