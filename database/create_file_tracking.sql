-- Create file tracking table to prevent reprocessing of files
CREATE TABLE IF NOT EXISTS processed_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_processed INT DEFAULT 0,
    processing_status ENUM('SUCCESS', 'FAILED', 'PARTIAL') DEFAULT 'SUCCESS',
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX idx_processed_files_name ON processed_files(file_name);
CREATE INDEX idx_processed_files_hash ON processed_files(file_hash);
CREATE INDEX idx_processed_files_processed_at ON processed_files(processed_at);
