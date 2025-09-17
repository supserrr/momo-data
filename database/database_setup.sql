-- MoMo SMS Data Processing System - Database Setup
-- Team 11 - Enterprise Web Development
-- Database: momo_sms_processing
-- Purpose: Store and manage mobile money transaction data

-- Drop existing tables for clean setup

DROP TABLE IF EXISTS transaction_statistics;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS users;

-- Create core entities

-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    account_status TEXT DEFAULT 'ACTIVE' CHECK (account_status IN ('ACTIVE', 'SUSPENDED', 'CLOSED')),
    registration_date DATETIME,
    last_transaction_date DATETIME,
    total_transactions INTEGER DEFAULT 0,
    total_amount_sent DECIMAL(15,2) DEFAULT 0.00,
    total_amount_received DECIMAL(15,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_phone_length CHECK (LENGTH(phone_number) >= 10),
    CONSTRAINT chk_amounts_positive CHECK (total_amount_sent >= 0 AND total_amount_received >= 0),
    CONSTRAINT chk_transaction_count CHECK (total_transactions >= 0)
);

-- Transaction categories table
CREATE TABLE transaction_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    category_code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_category_name_length CHECK (LENGTH(category_name) >= 2),
    CONSTRAINT chk_category_code_length CHECK (LENGTH(category_code) >= 2)
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_transaction_id VARCHAR(50) UNIQUE,
    sender_user_id INTEGER,
    receiver_user_id INTEGER,
    amount DECIMAL(15,2) NOT NULL,
    fee DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'RWF',
    transaction_date DATETIME NOT NULL,
    category_id INTEGER,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('SUCCESS', 'FAILED', 'PENDING', 'PROCESSING', 'CANCELLED', 'REJECTED')),
    reference_number VARCHAR(100),
    description TEXT,
    raw_sms_data TEXT,
    xml_attributes JSON,
    processing_metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (receiver_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE SET NULL,
    
    -- Check Constraints
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_fee_non_negative CHECK (fee >= 0),
    CONSTRAINT chk_currency_length CHECK (LENGTH(currency) = 3),
    CONSTRAINT chk_transaction_date_not_future CHECK (transaction_date <= CURRENT_TIMESTAMP)
);

-- System logs table
CREATE TABLE system_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_name VARCHAR(100) NOT NULL,
    log_level TEXT DEFAULT 'INFO' CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    details JSON,
    records_processed INTEGER DEFAULT 0,
    records_successful INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    execution_time_seconds DECIMAL(10,3),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_records_non_negative CHECK (records_processed >= 0 AND records_successful >= 0 AND records_failed >= 0),
    CONSTRAINT chk_execution_time_positive CHECK (execution_time_seconds >= 0)
);

-- Transaction statistics table
CREATE TABLE transaction_statistics (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_type VARCHAR(50) NOT NULL,
    stat_period VARCHAR(20),
    stat_date DATE,
    category_id INTEGER,
    user_id INTEGER,
    transaction_count INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    average_amount DECIMAL(15,2) DEFAULT 0.00,
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    success_rate DECIMAL(5,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT chk_stat_amounts_non_negative CHECK (total_amount >= 0 AND average_amount >= 0),
    CONSTRAINT chk_success_rate_range CHECK (success_rate >= 0 AND success_rate <= 100),
    CONSTRAINT chk_transaction_count_positive CHECK (transaction_count >= 0)
);

-- Create indexes for performance

-- Users table indexes
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_status ON users(account_status);
CREATE INDEX idx_users_last_transaction ON users(last_transaction_date);

-- Transactions table indexes
CREATE INDEX idx_transactions_sender ON transactions(sender_user_id);
CREATE INDEX idx_transactions_receiver ON transactions(receiver_user_id);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_external_id ON transactions(external_transaction_id);
CREATE INDEX idx_transactions_date_amount ON transactions(transaction_date, amount);

-- Composite indexes for common queries
CREATE INDEX idx_transactions_user_date ON transactions(sender_user_id, transaction_date);
CREATE INDEX idx_transactions_category_date ON transactions(category_id, transaction_date);
CREATE INDEX idx_transactions_status_date ON transactions(status, transaction_date);

-- System logs indexes
CREATE INDEX idx_logs_process ON system_logs(process_name);
CREATE INDEX idx_logs_level ON system_logs(log_level);
CREATE INDEX idx_logs_created ON system_logs(created_at);
CREATE INDEX idx_logs_process_created ON system_logs(process_name, created_at);

-- Statistics indexes
CREATE INDEX idx_stats_type ON transaction_statistics(stat_type);
CREATE INDEX idx_stats_period ON transaction_statistics(stat_period);
CREATE INDEX idx_stats_date ON transaction_statistics(stat_date);
CREATE INDEX idx_stats_category ON transaction_statistics(category_id);
CREATE INDEX idx_stats_user ON transaction_statistics(user_id);

-- Insert sample data

-- Transaction categories
INSERT INTO transaction_categories (category_name, category_code, description, is_active) VALUES
('Deposit', 'DEP', 'Money deposited into account', TRUE),
('Withdrawal', 'WIT', 'Money withdrawn from account', TRUE),
('Transfer', 'TRF', 'Money transferred between accounts', TRUE),
('Payment', 'PAY', 'Payment for goods or services', TRUE),
('Query', 'QRY', 'Balance inquiry or statement request', TRUE),
('Other', 'OTH', 'Other transaction types', TRUE);

-- Sample users
INSERT INTO users (phone_number, display_name, account_status, registration_date, last_transaction_date, total_transactions, total_amount_sent, total_amount_received) VALUES
('+250788110381', 'Primary Account', 'ACTIVE', '2024-01-01 00:00:00', '2024-05-21 14:38:14', 45, 125000.00, 89000.00),
('+250791666666', 'Jane Smith', 'ACTIVE', '2024-01-15 00:00:00', '2024-05-21 17:42:48', 23, 45000.00, 67000.00),
('+250790777777', 'Samuel Carter', 'ACTIVE', '2024-02-01 00:00:00', '2024-05-21 14:38:14', 18, 32000.00, 28000.00),
('+250788999999', 'Robert Brown', 'ACTIVE', '2024-02-15 00:00:00', '2024-05-21 17:05:45', 12, 15000.00, 12000.00),
('+250789888888', 'Linda Green', 'ACTIVE', '2024-03-01 00:00:00', '2024-05-21 17:05:45', 8, 8000.00, 15000.00);

-- Sample transactions
INSERT INTO transactions (external_transaction_id, sender_user_id, receiver_user_id, amount, fee, currency, transaction_date, category_id, status, reference_number, description, raw_sms_data) VALUES
('TXN001', 1, 2, 2000.00, 0.00, 'RWF', '2024-05-10 16:30:51', 3, 'SUCCESS', '76662021700', 'Transfer to Jane Smith', 'You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700.'),
('TXN002', 1, 2, 1000.00, 0.00, 'RWF', '2024-05-10 16:31:39', 3, 'SUCCESS', '73214484437', 'Payment to Jane Smith', 'TxId: 73214484437. Your payment of 1,000 RWF to Jane Smith 12845 has been completed at 2024-05-10 16:31:39. Your new balance: 1,000 RWF. Fee was 0 RWF.'),
('TXN003', 1, 3, 600.00, 0.00, 'RWF', '2024-05-10 21:32:32', 3, 'SUCCESS', '51732411227', 'Transfer to Samuel Carter', 'TxId: 51732411227. Your payment of 600 RWF to Samuel Carter 95464 has been completed at 2024-05-10 21:32:32. Your new balance: 400 RWF. Fee was 0 RWF.'),
('TXN004', 1, 1, 40000.00, 0.00, 'RWF', '2024-05-11 18:43:49', 1, 'SUCCESS', 'BANK_DEP_001', 'Bank deposit', '*113*R*A bank deposit of 40000 RWF has been added to your mobile money account at 2024-05-11 18:43:49. Your NEW BALANCE :40400 RWF. Cash Deposit::CASH::::0::250795963036.Thank you for using MTN MobileMoney.*EN#'),
('TXN005', 1, 2, 2000.00, 0.00, 'RWF', '2024-05-11 18:48:42', 3, 'SUCCESS', '17818959211', 'Transfer to Samuel Carter', 'TxId: 17818959211. Your payment of 2,000 RWF to Samuel Carter 14965 has been completed at 2024-05-11 18:48:42. Your new balance: 38,400 RWF. Fee was 0 RWF.');

-- System logs
INSERT INTO system_logs (process_name, log_level, message, records_processed, records_successful, records_failed, execution_time_seconds) VALUES
('xml_parser', 'INFO', 'Successfully parsed XML file', 1693, 1685, 8, 45.234),
('data_cleaner', 'INFO', 'Data cleaning completed', 1685, 1680, 5, 12.456),
('categorizer', 'INFO', 'Transaction categorization completed', 1680, 1675, 5, 8.789),
('database_loader', 'INFO', 'Transactions loaded to database', 1675, 1675, 0, 15.123),
('etl_pipeline', 'INFO', 'ETL pipeline execution completed', 1693, 1675, 18, 82.602);

-- Transaction statistics
INSERT INTO transaction_statistics (stat_type, stat_period, stat_date, category_id, transaction_count, total_amount, average_amount, min_amount, max_amount, success_rate) VALUES
('daily', '2024-05-10', '2024-05-10', 3, 3, 3600.00, 1200.00, 600.00, 2000.00, 100.00),
('daily', '2024-05-11', '2024-05-11', 1, 1, 40000.00, 40000.00, 40000.00, 40000.00, 100.00),
('daily', '2024-05-11', '2024-05-11', 3, 1, 2000.00, 2000.00, 2000.00, 2000.00, 100.00),
('monthly', '2024-05', '2024-05-01', 1, 15, 250000.00, 16666.67, 5000.00, 50000.00, 100.00),
('monthly', '2024-05', '2024-05-01', 3, 45, 125000.00, 2777.78, 500.00, 10000.00, 95.56);

-- Create views for common queries

-- Drop existing views if they exist
DROP VIEW IF EXISTS v_transaction_summary;
DROP VIEW IF EXISTS v_daily_stats;
DROP VIEW IF EXISTS v_user_summary;

-- Transaction summary view
CREATE VIEW v_transaction_summary AS
SELECT 
    t.transaction_id,
    t.external_transaction_id,
    su.phone_number as sender_phone,
    su.display_name as sender_name,
    ru.phone_number as receiver_phone,
    ru.display_name as receiver_name,
    t.amount,
    t.fee,
    t.currency,
    t.transaction_date,
    tc.category_name,
    t.status,
    t.reference_number,
    t.description
FROM transactions t
LEFT JOIN users su ON t.sender_user_id = su.user_id
LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id;

-- Daily transaction statistics view
CREATE VIEW v_daily_stats AS
SELECT 
    DATE(transaction_date) as transaction_date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_amount,
    AVG(amount) as average_amount,
    MIN(amount) as min_amount,
    MAX(amount) as max_amount,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_transactions,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_transactions,
    ROUND((COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) * 100.0 / COUNT(*)), 2) as success_rate
FROM transactions
GROUP BY DATE(transaction_date)
ORDER BY transaction_date DESC;

-- User transaction summary view
CREATE VIEW v_user_summary AS
SELECT 
    u.user_id,
    u.phone_number,
    u.display_name,
    u.account_status,
    u.total_transactions,
    u.total_amount_sent,
    u.total_amount_received,
    u.last_transaction_date,
    COUNT(t.transaction_id) as actual_transaction_count,
    SUM(CASE WHEN t.sender_user_id = u.user_id THEN t.amount ELSE 0 END) as actual_amount_sent,
    SUM(CASE WHEN t.receiver_user_id = u.user_id THEN t.amount ELSE 0 END) as actual_amount_received
FROM users u
LEFT JOIN transactions t ON (u.user_id = t.sender_user_id OR u.user_id = t.receiver_user_id)
GROUP BY u.user_id, u.phone_number, u.display_name, u.account_status, u.total_transactions, u.total_amount_sent, u.total_amount_received, u.last_transaction_date;

-- Create triggers for data consistency

-- Trigger to update user statistics when transaction is inserted
CREATE TRIGGER tr_update_user_stats_insert
AFTER INSERT ON transactions
BEGIN
    -- Update sender statistics
    UPDATE users 
    SET 
        total_transactions = total_transactions + 1,
        total_amount_sent = total_amount_sent + NEW.amount,
        last_transaction_date = NEW.transaction_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.sender_user_id;
    
    -- Update receiver statistics
    UPDATE users 
    SET 
        total_transactions = total_transactions + 1,
        total_amount_received = total_amount_received + NEW.amount,
        last_transaction_date = NEW.transaction_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.receiver_user_id;
END;

-- Trigger to update user statistics when transaction is updated
CREATE TRIGGER tr_update_user_stats_update
AFTER UPDATE ON transactions
WHEN OLD.sender_user_id != NEW.sender_user_id OR OLD.receiver_user_id != NEW.receiver_user_id OR OLD.amount != NEW.amount
BEGIN
    -- Handle sender changes
    UPDATE users 
    SET 
        total_transactions = total_transactions - 1,
        total_amount_sent = total_amount_sent - OLD.amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = OLD.sender_user_id;
    
    UPDATE users 
    SET 
        total_transactions = total_transactions + 1,
        total_amount_sent = total_amount_sent + NEW.amount,
        last_transaction_date = NEW.transaction_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.sender_user_id;
    
    -- Handle receiver changes
    UPDATE users 
    SET 
        total_transactions = total_transactions - 1,
        total_amount_received = total_amount_received - OLD.amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = OLD.receiver_user_id;
    
    UPDATE users 
    SET 
        total_transactions = total_transactions + 1,
        total_amount_received = total_amount_received + NEW.amount,
        last_transaction_date = NEW.transaction_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.receiver_user_id;
END;

-- Note: SQLite doesn't support stored procedures, but here's the equivalent logic
-- that would be implemented in application code

-- Note: SQLite doesn't support user permissions, but for production MySQL/PostgreSQL:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON momo_sms_processing.* TO 'momo_app'@'localhost';
-- GRANT SELECT ON momo_sms_processing.* TO 'momo_readonly'@'localhost';

-- Verification queries

-- Verify table creation
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Verify sample data
SELECT 'Users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'Transaction Categories', COUNT(*) FROM transaction_categories
UNION ALL
SELECT 'Transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'System Logs', COUNT(*) FROM system_logs
UNION ALL
SELECT 'Transaction Statistics', COUNT(*) FROM transaction_statistics;

-- Verify relationships
SELECT 
    'Foreign Key Check' as check_type,
    COUNT(*) as total_transactions,
    COUNT(sender_user_id) as transactions_with_sender,
    COUNT(receiver_user_id) as transactions_with_receiver,
    COUNT(category_id) as transactions_with_category
FROM transactions;

-- End of database setup
