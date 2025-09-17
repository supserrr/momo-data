-- MoMo SMS Data Processing System - Database Setup
-- Team 11 - Enterprise Web Development
-- Database: momo_sms_processing
-- Purpose: Store and manage mobile money transaction data

-- Drop existing tables for clean setup

DROP TABLE IF EXISTS transactions_backup;
DROP TABLE IF EXISTS category_stats;
DROP TABLE IF EXISTS etl_logs;
DROP TABLE IF EXISTS transactions;

-- Create core entities

-- ETL logs table
CREATE TABLE etl_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_name TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER,
    records_successful INTEGER,
    records_failed INTEGER,
    start_time TEXT,
    end_time TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Category stats table
CREATE TABLE category_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    count INTEGER NOT NULL,
    total_amount REAL,
    avg_amount REAL,
    min_amount REAL,
    max_amount REAL,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category)
);

-- Transactions backup table
CREATE TABLE transactions_backup (
    id INT,
    amount REAL,
    phone TEXT,
    date TEXT,
    reference TEXT,
    type TEXT,
    status TEXT,
    category TEXT,
    category_confidence REAL,
    original_data TEXT,
    raw_data TEXT,
    xml_tag TEXT,
    xml_attributes TEXT,
    cleaned_at TEXT,
    categorized_at TEXT,
    loaded_at TEXT
);

-- Main transactions table
CREATE TABLE IF NOT EXISTS "transactions" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    phone TEXT,
    date TEXT,
    reference TEXT,
    type TEXT,
    status TEXT,
    category TEXT,
    category_confidence REAL,
    personal_id TEXT,
    recipient_name TEXT,
    original_data TEXT,
    raw_data TEXT,
    xml_tag TEXT,
    xml_attributes TEXT,
    cleaned_at TEXT,
    categorized_at TEXT,
    loaded_at TEXT
);

-- Create indexes for performance

-- Transactions table indexes
CREATE INDEX idx_transactions_phone ON transactions(phone);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE UNIQUE INDEX idx_transactions_original_data_unique 
ON transactions(original_data) 
WHERE original_data IS NOT NULL AND original_data != '';


-- End of database setup
