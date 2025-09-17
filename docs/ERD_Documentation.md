# Entity Relationship Diagram (ERD) Documentation

## Design Overview

For our MoMo SMS data processing system, we implemented a simplified database schema optimized for rapid development and straightforward data processing. Our design prioritizes ease of implementation and maintenance while providing sufficient structure for transaction processing and analytics.

## Core Entities and Relationships

### 1. Transactions (Central Entity)
The **Transactions** entity is the heart of our system, capturing all transaction details in a flat, denormalized structure. This approach simplifies data access and processing while maintaining all necessary transaction information. The table includes comprehensive transaction metadata, processing timestamps, and categorization data.

### 2. ETL_Logs (Process Tracking)
The **ETL_Logs** entity tracks ETL process execution and performance metrics. This table provides comprehensive audit trails for data processing operations, including success/failure rates, processing times, and error messages.

### 3. Category_Stats (Aggregated Analytics)
The **Category_Stats** entity implements a denormalized approach for performance optimization. By pre-calculating category-level statistics, our system can deliver real-time dashboard performance without expensive aggregations on large transaction datasets.

### 4. Transactions_Backup (Data Preservation)
The **Transactions_Backup** entity serves as a backup and migration table, preserving historical transaction data during system updates and providing data recovery capabilities.

## Design Decisions

**Simplified Schema Strategy**: Our design prioritizes simplicity and rapid development over complex normalization. This flat structure approach reduces complexity while maintaining all necessary functionality for transaction processing and analytics.

**Data Storage Approach**: We use a denormalized structure that stores all transaction data in a single table, including:
- Core transaction fields (amount, phone, date, reference, type, status)
- Categorization data (category, category_confidence)
- User information (personal_id, recipient_name)
- Processing metadata (original_data, raw_data, xml_tag, xml_attributes)
- Timestamps (cleaned_at, categorized_at, loaded_at)

**Performance Optimization**: We implemented strategic indexing on frequently queried columns (phone, date, category, amount) to ensure efficient data access. A unique index on original_data prevents duplicate processing.

**Data Integrity**: We use application-level validation and constraints rather than database-level foreign keys, providing flexibility while maintaining data quality through our ETL pipeline.

**Scalability**: Our design supports easy data migration and backup through the transactions_backup table, while the flat structure allows for straightforward horizontal scaling and data partitioning.

**ETL Process Integration**: The schema is designed to work seamlessly with our ETL pipeline, with dedicated logging and statistics tables that support real-time monitoring and analytics.

This simplified database design provides an efficient foundation for our MoMo SMS processing system while maintaining the flexibility to evolve with changing requirements.
