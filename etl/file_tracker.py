"""
File tracking utility for ETL process.
Tracks processed files to prevent reprocessing.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any
import mysql.connector
from api.db import MySQLDatabaseManager


class FileTracker:
    """Tracks processed files to prevent reprocessing."""
    
    def __init__(self):
        self.db = MySQLDatabaseManager()
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def is_file_processed(self, file_path: Path) -> bool:
        """Check if a file has already been processed."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Use absolute path for consistency
                abs_path = str(file_path.resolve())
                
                # Check by file name and path
                cursor.execute("""
                    SELECT id FROM processed_files 
                    WHERE file_name = %s AND file_path = %s
                """, (file_path.name, abs_path))
                
                result = cursor.fetchone()
                cursor.close()
                return result is not None
                
        except Exception as e:
            print(f"Error checking file processing status: {e}")
            return False
    
    def is_file_changed(self, file_path: Path) -> bool:
        """Check if a file has been modified since last processing."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Use absolute path for consistency
                abs_path = str(file_path.resolve())
                
                # Get file info from database
                cursor.execute("""
                    SELECT file_size, file_hash FROM processed_files 
                    WHERE file_name = %s AND file_path = %s
                """, (file_path.name, abs_path))
                
                result = cursor.fetchone()
                if not result:
                    return True  # File not in database, consider it changed
                
                stored_size, stored_hash = result
                current_size = file_path.stat().st_size
                current_hash = self.calculate_file_hash(file_path)
                
                cursor.close()
                
                # File changed if size or hash is different
                return current_size != stored_size or current_hash != stored_hash
                
        except Exception as e:
            print(f"Error checking file changes: {e}")
            return True  # Assume changed if error
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed."""
        if not file_path.exists():
            return False
        
        # Process if file hasn't been processed or has been modified
        return not self.is_file_processed(file_path) or self.is_file_changed(file_path)
    
    def mark_file_processed(self, file_path: Path, records_processed: int, 
                          status: str = 'SUCCESS', error_message: Optional[str] = None) -> bool:
        """Mark a file as processed."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                file_size = file_path.stat().st_size
                file_hash = self.calculate_file_hash(file_path)
                
                # Use absolute path for consistency
                abs_path = str(file_path.resolve())
                
                # Insert or update file record
                cursor.execute("""
                    INSERT INTO processed_files 
                    (file_name, file_path, file_size, file_hash, records_processed, processing_status, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    file_size = VALUES(file_size),
                    file_hash = VALUES(file_hash),
                    records_processed = VALUES(records_processed),
                    processing_status = VALUES(processing_status),
                    error_message = VALUES(error_message),
                    processed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                """, (
                    file_path.name,
                    abs_path,
                    file_size,
                    file_hash,
                    records_processed,
                    status,
                    error_message
                ))
                
                conn.commit()
                cursor.close()
                return True
                
        except Exception as e:
            print(f"Error marking file as processed: {e}")
            return False
    
    def get_processed_files(self) -> list:
        """Get list of all processed files."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT file_name, file_path, processed_at, records_processed, 
                           processing_status, error_message
                    FROM processed_files 
                    ORDER BY processed_at DESC
                """)
                
                files = cursor.fetchall()
                cursor.close()
                return files
                
        except Exception as e:
            print(f"Error getting processed files: {e}")
            return []
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get statistics about processed files."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total files processed
                cursor.execute("SELECT COUNT(*) FROM processed_files")
                total_files = cursor.fetchone()[0]
                
                # Successfully processed files
                cursor.execute("SELECT COUNT(*) FROM processed_files WHERE processing_status = 'SUCCESS'")
                success_files = cursor.fetchone()[0]
                
                # Failed files
                cursor.execute("SELECT COUNT(*) FROM processed_files WHERE processing_status = 'FAILED'")
                failed_files = cursor.fetchone()[0]
                
                # Total records processed
                cursor.execute("SELECT SUM(records_processed) FROM processed_files WHERE processing_status = 'SUCCESS'")
                total_records = cursor.fetchone()[0] or 0
                
                cursor.close()
                
                return {
                    'total_files': total_files,
                    'success_files': success_files,
                    'failed_files': failed_files,
                    'total_records': total_records
                }
                
        except Exception as e:
            print(f"Error getting file stats: {e}")
            return {
                'total_files': 0,
                'success_files': 0,
                'failed_files': 0,
                'total_records': 0
            }
