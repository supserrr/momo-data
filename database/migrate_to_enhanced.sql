-- Migration script to add enhanced parser fields to existing transactions table
-- Team 11 - Enterprise Web Development

USE momo_sms_processing;

-- Add new columns to transactions table
ALTER TABLE transactions 
ADD COLUMN financial_transaction_id VARCHAR(50) AFTER external_transaction_id,
ADD COLUMN transaction_type VARCHAR(50) NOT NULL DEFAULT '' AFTER category_id,
ADD COLUMN direction ENUM('credit', 'debit') NOT NULL DEFAULT 'credit' AFTER transaction_type,
ADD COLUMN sender_name VARCHAR(100) AFTER direction,
ADD COLUMN sender_phone VARCHAR(15) AFTER sender_name,
ADD COLUMN recipient_name VARCHAR(100) AFTER sender_phone,
ADD COLUMN recipient_phone VARCHAR(15) AFTER recipient_name,
ADD COLUMN momo_code VARCHAR(10) AFTER recipient_phone,
ADD COLUMN sender_momo_id VARCHAR(20) AFTER momo_code,
ADD COLUMN agent_momo_number VARCHAR(15) AFTER sender_momo_id,
ADD COLUMN business_name VARCHAR(100) AFTER agent_momo_number,
ADD COLUMN new_balance DECIMAL(15,2) AFTER business_name,
ADD COLUMN confidence_score DECIMAL(3,2) DEFAULT 0.00 AFTER new_balance,
ADD COLUMN original_message TEXT AFTER raw_sms_data;

-- Add new constraints
ALTER TABLE transactions 
ADD CONSTRAINT chk_confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1),
ADD CONSTRAINT chk_balance_non_negative CHECK (new_balance IS NULL OR new_balance >= 0);

-- Update transaction categories with new enhanced categories
INSERT IGNORE INTO transaction_categories (category_name, category_code, description, is_active) VALUES
('Transfer Incoming', 'TRANSFER_INCOMING', 'Money received from another person', TRUE),
('Transfer Outgoing', 'TRANSFER_OUTGOING', 'Money sent to another person', TRUE),
('Payment Personal', 'PAYMENT_PERSONAL', 'Payment to momo code registered to a person', TRUE),
('Payment Business', 'PAYMENT_BUSINESS', 'Payment to businesses', TRUE),
('Deposit Agent', 'DEPOSIT_AGENT', 'Deposit from momo agent or merchant', TRUE),
('Deposit Cash', 'DEPOSIT_CASH', 'Cash deposit from agent', TRUE),
('Deposit Bank Transfer', 'DEPOSIT_BANK_TRANSFER', 'Bank transfer deposit', TRUE),
('Deposit Other', 'DEPOSIT_OTHER', 'Other types of deposits', TRUE),
('Airtime', 'AIRTIME', 'Airtime purchase', TRUE),
('Data Bundle', 'DATA_BUNDLE', 'Data bundle purchase', TRUE);

-- Update existing transactions with default values
UPDATE transactions SET 
    transaction_type = CASE 
        WHEN description LIKE '%PAYMENT%' THEN 'PAYMENT'
        WHEN description LIKE '%TRANSFER%' THEN 'TRANSFER'
        WHEN description LIKE '%DEPOSIT%' THEN 'DEPOSIT'
        WHEN description LIKE '%WITHDRAWAL%' THEN 'WITHDRAWAL'
        WHEN description LIKE '%AIRTIME%' THEN 'AIRTIME'
        WHEN description LIKE '%DATA%' THEN 'DATA_BUNDLE'
        ELSE 'OTHER'
    END,
    direction = CASE 
        WHEN description LIKE '%RECEIVE%' OR description LIKE '%DEPOSIT%' THEN 'credit'
        ELSE 'debit'
    END,
    confidence_score = 0.8
WHERE transaction_type = '';

-- Copy raw_sms_data to original_message for existing records
UPDATE transactions SET original_message = raw_sms_data WHERE original_message IS NULL;

COMMIT;
