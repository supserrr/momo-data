-- Create missing tables for the ETL pipeline
-- Team 11 - Enterprise Web Development

USE momo_sms_processing;

-- Create system_logs table
CREATE TABLE IF NOT EXISTS system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    log_level ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG') NOT NULL,
    message TEXT NOT NULL,
    records_processed INT DEFAULT 0,
    execution_time_seconds DECIMAL(10,3) DEFAULT 0.000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_process_name (process_name),
    INDEX idx_log_level (log_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create transaction_tags table
CREATE TABLE IF NOT EXISTS transaction_tags (
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
    
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_tag_id (tag_id),
    INDEX idx_assigned_at (assigned_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_user_preference (user_id, preference_key),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_preference_key (preference_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create transaction_statistics table
CREATE TABLE IF NOT EXISTS transaction_statistics (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL,
    stat_type ENUM('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY') NOT NULL,
    category_id INT,
    tag_id INT,
    transaction_count INT DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    avg_amount DECIMAL(15,2) DEFAULT 0.00,
    min_amount DECIMAL(15,2) DEFAULT 0.00,
    max_amount DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_stat (stat_date, stat_type, category_id, tag_id),
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE SET NULL,
    
    INDEX idx_stat_date (stat_date),
    INDEX idx_stat_type (stat_type),
    INDEX idx_category_id (category_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

COMMIT;
