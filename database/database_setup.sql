-- MoMo SMS Data Processing System - Normalized MySQL Database Setup
-- Team 11 - Enterprise Web Development
-- Database: momo_sms_processing
-- Purpose: Store and manage mobile money transaction data with proper normalization

-- Create database
CREATE DATABASE IF NOT EXISTS momo_sms_processing
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE momo_sms_processing;

-- Drop existing tables for clean setup (in correct order due to foreign keys)
DROP TABLE IF EXISTS transaction_tags;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS transaction_statistics;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS users;

-- Create core entities

-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    account_status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') DEFAULT 'ACTIVE',
    registration_date DATETIME,
    last_transaction_date DATETIME,
    total_transactions INT DEFAULT 0,
    total_amount_sent DECIMAL(15,2) DEFAULT 0.00,
    total_amount_received DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_phone_length CHECK (CHAR_LENGTH(phone_number) >= 10),
    CONSTRAINT chk_amounts_positive CHECK (total_amount_sent >= 0 AND total_amount_received >= 0),
    CONSTRAINT chk_transaction_count CHECK (total_transactions >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transaction categories table
CREATE TABLE transaction_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    category_code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_category_name_length CHECK (CHAR_LENGTH(category_name) >= 2),
    CONSTRAINT chk_category_code_length CHECK (CHAR_LENGTH(category_code) >= 2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tags table (for many-to-many relationship with transactions)
CREATE TABLE tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    tag_description TEXT,
    tag_color VARCHAR(7) DEFAULT '#007bff', -- Hex color for UI
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_tag_name_length CHECK (CHAR_LENGTH(tag_name) >= 2),
    CONSTRAINT chk_tag_color_format CHECK (tag_color REGEXP '^#[0-9A-Fa-f]{6}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transactions table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    external_transaction_id VARCHAR(50) UNIQUE,
    financial_transaction_id VARCHAR(50),
    sender_user_id INT,
    receiver_user_id INT,
    amount DECIMAL(15,2) NOT NULL,
    fee DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'RWF',
    transaction_date DATETIME NOT NULL,
    category_id INT,
    transaction_type VARCHAR(50) NOT NULL,
    direction ENUM('credit', 'debit') NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'PENDING', 'PROCESSING', 'CANCELLED', 'REJECTED') DEFAULT 'SUCCESS',
    reference_number VARCHAR(100),
    description TEXT,
    
    -- Enhanced parser fields
    sender_name VARCHAR(100),
    sender_phone VARCHAR(15),
    recipient_name VARCHAR(100),
    recipient_phone VARCHAR(15),
    momo_code VARCHAR(10),
    sender_momo_id VARCHAR(20),
    agent_momo_number VARCHAR(15),
    business_name VARCHAR(100),
    new_balance DECIMAL(15,2),
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    
    -- Original data
    raw_sms_data TEXT,
    original_message TEXT,
    xml_attributes JSON,
    processing_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (receiver_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE SET NULL,
    
    -- Check Constraints
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_fee_non_negative CHECK (fee >= 0),
    CONSTRAINT chk_currency_length CHECK (CHAR_LENGTH(currency) = 3),
    CONSTRAINT chk_transaction_date_not_future CHECK (transaction_date <= '2030-12-31 23:59:59'),
    CONSTRAINT chk_confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT chk_balance_non_negative CHECK (new_balance IS NULL OR new_balance >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Junction table for many-to-many relationship: Transactions <-> Tags
CREATE TABLE transaction_tags (
    transaction_id INT,
    tag_id INT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INT, -- User who assigned the tag
    
    -- Composite Primary Key
    PRIMARY KEY (transaction_id, tag_id),
    
    -- Foreign Key Constraints
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Constraints
    -- Note: Self-assignment check removed due to MySQL constraint limitations
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Junction table for many-to-many relationship: Users <-> Transaction Categories (preferences)
CREATE TABLE user_preferences (
    user_id INT,
    category_id INT,
    preference_type ENUM('FAVORITE', 'BLOCKED', 'NOTIFICATION') DEFAULT 'FAVORITE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Composite Primary Key
    PRIMARY KEY (user_id, category_id, preference_type),
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System logs table
CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    log_level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') DEFAULT 'INFO',
    message TEXT NOT NULL,
    details JSON,
    records_processed INT DEFAULT 0,
    records_successful INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    execution_time_seconds DECIMAL(10,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_records_non_negative CHECK (records_processed >= 0 AND records_successful >= 0 AND records_failed >= 0),
    CONSTRAINT chk_execution_time_positive CHECK (execution_time_seconds >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transaction statistics table
CREATE TABLE transaction_statistics (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,
    stat_period VARCHAR(20),
    stat_date DATE,
    category_id INT,
    user_id INT,
    tag_id INT,
    transaction_count INT DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    average_amount DECIMAL(15,2) DEFAULT 0.00,
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    success_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT chk_stat_amounts_non_negative CHECK (total_amount >= 0 AND average_amount >= 0),
    CONSTRAINT chk_success_rate_range CHECK (success_rate >= 0 AND success_rate <= 100),
    CONSTRAINT chk_transaction_count_positive CHECK (transaction_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

-- Tags table indexes
CREATE INDEX idx_tags_name ON tags(tag_name);
CREATE INDEX idx_tags_active ON tags(is_active);

-- Junction table indexes
CREATE INDEX idx_transaction_tags_transaction ON transaction_tags(transaction_id);
CREATE INDEX idx_transaction_tags_tag ON transaction_tags(tag_id);
CREATE INDEX idx_transaction_tags_assigned_by ON transaction_tags(assigned_by);

CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_category ON user_preferences(category_id);
CREATE INDEX idx_user_preferences_type ON user_preferences(preference_type);

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
CREATE INDEX idx_stats_tag ON transaction_statistics(tag_id);

-- Insert sample data

-- Transaction categories
INSERT INTO transaction_categories (category_name, category_code, description, is_active) VALUES
-- Enhanced categories from parser with detailed descriptions
('Transfer Incoming', 'TRANSFER_INCOMING', 'Money received from another person via mobile money transfer. This includes peer-to-peer transfers where someone sends you money directly to your mobile wallet. Examples: receiving money from family, friends, or other individuals through their phone numbers or momo codes.', TRUE),
('Transfer Outgoing', 'TRANSFER_OUTGOING', 'Money sent to another person via mobile money transfer. This includes peer-to-peer transfers where you send money directly to someone else\'s mobile wallet. Examples: sending money to family, friends, or other individuals through their phone numbers or momo codes.', TRUE),
('Payment Personal', 'PAYMENT_PERSONAL', 'Payment made to a momo code registered to an individual person. This includes payments to friends, family, or individuals for personal services, loans, or personal transactions. Examples: paying a friend back, buying from a small vendor, personal service payments.', TRUE),
('Payment Business', 'PAYMENT_BUSINESS', 'Payment made to businesses, merchants, or commercial entities. This includes payments for goods, services, bills, utilities, or any commercial transactions through business momo codes. Examples: paying for groceries, restaurant bills, utility payments, online purchases.', TRUE),
('Deposit Agent', 'DEPOSIT_AGENT', 'Cash deposit made through a mobile money agent or merchant. This includes depositing physical cash at an agent location to add funds to your mobile wallet. Examples: visiting an MTN agent to deposit cash, merchant cash deposits, agent-assisted deposits.', TRUE),
('Deposit Cash', 'DEPOSIT_CASH', 'Direct cash deposit to your mobile wallet. This includes cash deposits made at agent locations, ATMs, or other cash deposit points to increase your mobile wallet balance. Examples: ATM cash deposits, direct cash deposits at agent locations.', TRUE),
('Deposit Bank Transfer', 'DEPOSIT_BANK_TRANSFER', 'Bank transfer deposit to your mobile wallet. This includes transfers from your bank account to your mobile money wallet, or deposits made through banking channels. Examples: bank-to-mobile transfers, salary deposits, bank account transfers.', TRUE),
('Deposit Other', 'DEPOSIT_OTHER', 'Other types of deposits not covered by specific categories. This includes deposits from various sources such as salary payments, refunds, or other miscellaneous deposit types. Examples: salary deposits, refunds, government payments, other institutional deposits.', TRUE),
('Airtime', 'AIRTIME', 'Mobile airtime purchase for your phone number or another number. This includes buying airtime credit for voice calls, SMS, or other mobile services. Examples: buying airtime for yourself, gifting airtime to others, voice call credit purchases.', TRUE),
('Data Bundle', 'DATA_BUNDLE', 'Mobile data bundle purchase for internet access. This includes buying data packages for mobile internet usage, social media bundles, or other data services. Examples: internet data bundles, social media data packages, streaming data bundles.', TRUE),
-- Legacy categories for backward compatibility with detailed descriptions
('Deposit', 'DEP', 'General money deposit into your mobile wallet account. This is a broad category covering various types of deposits that increase your wallet balance.', TRUE),
('Withdrawal', 'WIT', 'Money withdrawn from your mobile wallet account. This includes cash withdrawals at agent locations, ATMs, or other withdrawal points to get physical cash from your mobile wallet. Examples: ATM cash withdrawals, agent cash withdrawals, cash-out transactions.', TRUE),
('Transfer', 'TRF', 'General money transfer between mobile wallet accounts. This is a broad category covering various types of transfers between different mobile money accounts.', TRUE),
('Payment', 'PAY', 'General payment for goods or services using mobile money. This is a broad category covering various types of payments made through mobile money for purchases or services.', TRUE),
('Query', 'QRY', 'Balance inquiry or account statement request. This includes checking your mobile wallet balance, requesting transaction history, or other account information queries. Examples: balance checks, transaction history requests, account information queries.', TRUE),
('Other', 'OTH', 'Other transaction types not covered by specific categories. This includes miscellaneous transactions, system adjustments, or other unique transaction types. Examples: system adjustments, promotional credits, account maintenance transactions.', TRUE);

-- Tags
INSERT INTO tags (tag_name, tag_description, tag_color, is_active) VALUES
('High Value', 'Transactions above 10,000 RWF', '#dc3545', TRUE),
('Recurring', 'Regularly occurring transactions', '#28a745', TRUE),
('Business', 'Business-related transactions', '#007bff', TRUE),
('Personal', 'Personal transactions', '#6c757d', TRUE),
('Urgent', 'Time-sensitive transactions', '#fd7e14', TRUE),
('Suspicious', 'Flagged for review', '#e83e8c', TRUE),
('Verified', 'Manually verified transactions', '#20c997', TRUE);

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
('TXN005', 1, 2, 2000.00, 0.00, 'RWF', '2024-05-11 18:48:42', 3, 'SUCCESS', '17818959211', 'Transfer to Samuel Carter', 'TxId: 17818959211. Your payment of 2,000 RWF to Samuel Carter 14965 has been completed at 2024-05-11 18:48:42. Your new balance: 38,400 RWF. Fee was 0 RWF.'),
('TXN006', 2, 1, 15000.00, 0.00, 'RWF', '2024-05-12 09:15:30', 3, 'SUCCESS', 'HIGH_VAL_001', 'High value transfer', 'High value transfer of 15,000 RWF completed successfully.'),
('TXN007', 3, 4, 500.00, 0.00, 'RWF', '2024-05-12 14:22:15', 4, 'SUCCESS', 'PAY_001', 'Payment for services', 'Payment for services completed.'),
('TXN008', 4, 5, 2500.00, 0.00, 'RWF', '2024-05-12 16:45:20', 3, 'SUCCESS', 'TRF_001', 'Regular transfer', 'Regular monthly transfer completed.');

-- Sample transaction tags (many-to-many relationship)
INSERT INTO transaction_tags (transaction_id, tag_id, assigned_by) VALUES
(1, 4, 1), -- Transaction 1 tagged as Personal
(1, 6, 1), -- Transaction 1 tagged as Verified
(2, 4, 1), -- Transaction 2 tagged as Personal
(3, 4, 1), -- Transaction 3 tagged as Personal
(4, 1, 1), -- Transaction 4 tagged as High Value
(4, 2, 1), -- Transaction 4 tagged as Recurring
(4, 6, 1), -- Transaction 4 tagged as Verified
(5, 4, 1), -- Transaction 5 tagged as Personal
(6, 1, 2), -- Transaction 6 tagged as High Value
(6, 3, 2), -- Transaction 6 tagged as Business
(7, 4, 3), -- Transaction 7 tagged as Personal
(8, 2, 4), -- Transaction 8 tagged as Recurring
(8, 4, 4); -- Transaction 8 tagged as Personal

-- Sample user preferences (many-to-many relationship)
INSERT INTO user_preferences (user_id, category_id, preference_type) VALUES
(1, 3, 'FAVORITE'), -- User 1 favorites Transfer category
(1, 1, 'FAVORITE'), -- User 1 favorites Deposit category
(1, 4, 'NOTIFICATION'), -- User 1 wants notifications for Payment category
(2, 3, 'FAVORITE'), -- User 2 favorites Transfer category
(2, 4, 'FAVORITE'), -- User 2 favorites Payment category
(3, 3, 'FAVORITE'), -- User 3 favorites Transfer category
(4, 2, 'FAVORITE'), -- User 4 favorites Withdrawal category
(5, 1, 'FAVORITE'); -- User 5 favorites Deposit category

-- System logs
INSERT INTO system_logs (process_name, log_level, message, records_processed, records_successful, records_failed, execution_time_seconds) VALUES
('xml_parser', 'INFO', 'Successfully parsed XML file', 1693, 1685, 8, 45.234),
('data_cleaner', 'INFO', 'Data cleaning completed', 1685, 1680, 5, 12.456),
('categorizer', 'INFO', 'Transaction categorization completed', 1680, 1675, 5, 8.789),
('database_loader', 'INFO', 'Transactions loaded to database', 1675, 1675, 0, 15.123),
('etl_pipeline', 'INFO', 'ETL pipeline execution completed', 1693, 1675, 18, 82.602);

-- Transaction statistics
INSERT INTO transaction_statistics (stat_type, stat_period, stat_date, category_id, user_id, tag_id, transaction_count, total_amount, average_amount, min_amount, max_amount, success_rate) VALUES
('daily', '2024-05-10', '2024-05-10', 3, 1, NULL, 3, 3600.00, 1200.00, 600.00, 2000.00, 100.00),
('daily', '2024-05-11', '2024-05-11', 1, 1, NULL, 1, 40000.00, 40000.00, 40000.00, 40000.00, 100.00),
('daily', '2024-05-11', '2024-05-11', 3, 1, NULL, 1, 2000.00, 2000.00, 2000.00, 2000.00, 100.00),
('monthly', '2024-05', '2024-05-01', 1, 1, NULL, 15, 250000.00, 16666.67, 5000.00, 50000.00, 100.00),
('monthly', '2024-05', '2024-05-01', 3, 1, NULL, 45, 125000.00, 2777.78, 500.00, 10000.00, 95.56),
('daily', '2024-05-12', '2024-05-12', NULL, NULL, 1, 2, 55000.00, 27500.00, 15000.00, 40000.00, 100.00), -- High Value tag stats
('daily', '2024-05-12', '2024-05-12', NULL, NULL, 2, 2, 29000.00, 14500.00, 2500.00, 40000.00, 100.00); -- Recurring tag stats

-- Create views for common queries

-- Transaction summary view with tags
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
    t.description,
    GROUP_CONCAT(tag.tag_name SEPARATOR ', ') as tags
FROM transactions t
LEFT JOIN users su ON t.sender_user_id = su.user_id
LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
LEFT JOIN transaction_tags tt ON t.transaction_id = tt.transaction_id
LEFT JOIN tags tag ON tt.tag_id = tag.tag_id
GROUP BY t.transaction_id, t.external_transaction_id, su.phone_number, su.display_name, 
         ru.phone_number, ru.display_name, t.amount, t.fee, t.currency, 
         t.transaction_date, tc.category_name, t.status, t.reference_number, t.description;

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

-- Tag statistics view
CREATE VIEW v_tag_statistics AS
SELECT 
    tag.tag_id,
    tag.tag_name,
    tag.tag_color,
    COUNT(tt.transaction_id) as transaction_count,
    SUM(t.amount) as total_amount,
    AVG(t.amount) as average_amount,
    MIN(t.amount) as min_amount,
    MAX(t.amount) as max_amount,
    COUNT(CASE WHEN t.status = 'SUCCESS' THEN 1 END) as successful_transactions,
    ROUND((COUNT(CASE WHEN t.status = 'SUCCESS' THEN 1 END) * 100.0 / COUNT(tt.transaction_id)), 2) as success_rate
FROM tags tag
LEFT JOIN transaction_tags tt ON tag.tag_id = tt.tag_id
LEFT JOIN transactions t ON tt.transaction_id = t.transaction_id
GROUP BY tag.tag_id, tag.tag_name, tag.tag_color;

-- Create triggers for data consistency

DELIMITER //

-- Trigger to update user statistics when transaction is inserted
CREATE TRIGGER tr_update_user_stats_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    -- Update sender statistics
    IF NEW.sender_user_id IS NOT NULL THEN
        UPDATE users 
        SET 
            total_transactions = total_transactions + 1,
            total_amount_sent = total_amount_sent + NEW.amount,
            last_transaction_date = NEW.transaction_date,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.sender_user_id;
    END IF;
    
    -- Update receiver statistics
    IF NEW.receiver_user_id IS NOT NULL THEN
        UPDATE users 
        SET 
            total_transactions = total_transactions + 1,
            total_amount_received = total_amount_received + NEW.amount,
            last_transaction_date = NEW.transaction_date,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.receiver_user_id;
    END IF;
END//

-- Trigger to update user statistics when transaction is updated
CREATE TRIGGER tr_update_user_stats_update
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    -- Handle sender changes
    IF OLD.sender_user_id != NEW.sender_user_id OR OLD.amount != NEW.amount THEN
        -- Remove old sender stats
        IF OLD.sender_user_id IS NOT NULL THEN
            UPDATE users 
            SET 
                total_transactions = total_transactions - 1,
                total_amount_sent = total_amount_sent - OLD.amount,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = OLD.sender_user_id;
        END IF;
        
        -- Add new sender stats
        IF NEW.sender_user_id IS NOT NULL THEN
            UPDATE users 
            SET 
                total_transactions = total_transactions + 1,
                total_amount_sent = total_amount_sent + NEW.amount,
                last_transaction_date = NEW.transaction_date,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.sender_user_id;
        END IF;
    END IF;
    
    -- Handle receiver changes
    IF OLD.receiver_user_id != NEW.receiver_user_id OR OLD.amount != NEW.amount THEN
        -- Remove old receiver stats
        IF OLD.receiver_user_id IS NOT NULL THEN
            UPDATE users 
            SET 
                total_transactions = total_transactions - 1,
                total_amount_received = total_amount_received - OLD.amount,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = OLD.receiver_user_id;
        END IF;
        
        -- Add new receiver stats
        IF NEW.receiver_user_id IS NOT NULL THEN
            UPDATE users 
            SET 
                total_transactions = total_transactions + 1,
                total_amount_received = total_amount_received + NEW.amount,
                last_transaction_date = NEW.transaction_date,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.receiver_user_id;
        END IF;
    END IF;
END//

DELIMITER ;

-- Create stored procedures

DELIMITER //

-- Procedure to get user transaction summary
CREATE PROCEDURE GetUserTransactionSummary(IN p_user_id INT)
BEGIN
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
    WHERE u.user_id = p_user_id
    GROUP BY u.user_id, u.phone_number, u.display_name, u.account_status, u.total_transactions, u.total_amount_sent, u.total_amount_received, u.last_transaction_date;
END//

-- Procedure to get daily statistics
CREATE PROCEDURE GetDailyStatistics(IN p_date DATE)
BEGIN
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
    WHERE DATE(transaction_date) = p_date
    GROUP BY DATE(transaction_date);
END//

-- Procedure to get transactions by tag
CREATE PROCEDURE GetTransactionsByTag(IN p_tag_id INT)
BEGIN
    SELECT 
        t.transaction_id,
        t.external_transaction_id,
        t.amount,
        t.transaction_date,
        t.status,
        t.description,
        su.display_name as sender_name,
        ru.display_name as receiver_name,
        tc.category_name
    FROM transactions t
    INNER JOIN transaction_tags tt ON t.transaction_id = tt.transaction_id
    LEFT JOIN users su ON t.sender_user_id = su.user_id
    LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
    LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
    WHERE tt.tag_id = p_tag_id
    ORDER BY t.transaction_date DESC;
END//

DELIMITER ;

-- Grant permissions

-- Create application user
CREATE USER IF NOT EXISTS 'momo_app'@'localhost' IDENTIFIED BY 'secure_password_123';
CREATE USER IF NOT EXISTS 'momo_readonly'@'localhost' IDENTIFIED BY 'readonly_password_123';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON momo_sms_processing.* TO 'momo_app'@'localhost';
GRANT SELECT ON momo_sms_processing.* TO 'momo_readonly'@'localhost';

-- Verification queries

-- Verify table creation
SELECT TABLE_NAME, TABLE_ROWS, CREATE_TIME 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'momo_sms_processing' 
ORDER BY TABLE_NAME;

-- Verify sample data
SELECT 'Users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'Transaction Categories', COUNT(*) FROM transaction_categories
UNION ALL
SELECT 'Tags', COUNT(*) FROM tags
UNION ALL
SELECT 'Transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'Transaction Tags', COUNT(*) FROM transaction_tags
UNION ALL
SELECT 'User Preferences', COUNT(*) FROM user_preferences
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

-- Verify many-to-many relationships
SELECT 
    'Transaction Tags' as relationship,
    COUNT(*) as total_relationships
FROM transaction_tags
UNION ALL
SELECT 
    'User Preferences',
    COUNT(*)
FROM user_preferences;

-- Test CRUD operations
-- CREATE: Insert a new user
INSERT INTO users (phone_number, display_name, account_status, registration_date) 
VALUES ('+250788123456', 'Test User', 'ACTIVE', NOW());

-- READ: Select user data
SELECT * FROM users WHERE phone_number = '+250788123456';

-- UPDATE: Update user data
UPDATE users SET display_name = 'Updated Test User' WHERE phone_number = '+250788123456';

-- DELETE: Delete test user
DELETE FROM users WHERE phone_number = '+250788123456';

-- Verify deletion
SELECT COUNT(*) as remaining_users FROM users WHERE phone_number = '+250788123456';

-- End of normalized MySQL database setup
