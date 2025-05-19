import sqlite3
import os
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DBHandler:
    def __init__(self):
        self.db_path = Path("autoclean.db")
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self._initialize_db()
            logger.info("SQLite connection established")
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            raise
    
    def _initialize_db(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # File history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_shape TEXT NOT NULL,
            cleaned_shape TEXT NOT NULL,
            cleaning_instructions TEXT NOT NULL,
            cleaned_file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
        
        self.conn.commit()
    
    def execute_query(self, query: str, params=(), fetch: bool = False, commit: bool = False):
        """Generic query execution method"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            if commit:
                self.conn.commit()
            
            if fetch:
                return cursor.fetchall()
            return None
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        try:
            result = self.execute_query(query, (email,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def create_user(self, email: str, password_hash: str) -> int:
        """Create new user"""
        query = "INSERT INTO users (email, password_hash) VALUES (?, ?)"
        try:
            self.execute_query(query, (email, password_hash), commit=True)
            return self.conn.cursor().lastrowid
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def save_cleaning_history(
        self,
        user_id: int,
        original_shape: str,
        cleaned_shape: str,
        cleaning_notes: str,
        cleaned_file_path: str
    ) -> bool:
        """Save cleaning history"""
        query = """
        INSERT INTO file_history 
        (user_id, original_shape, cleaned_shape, cleaning_instructions, cleaned_file_path)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self.execute_query(
                query,
                (user_id, original_shape, cleaned_shape, cleaning_notes, cleaned_file_path),
                commit=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving cleaning history: {e}")
            return False
    
    def get_user_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's cleaning history"""
        query = """
        SELECT 
            id,
            user_id,
            original_shape,
            cleaned_shape,
            cleaning_instructions as cleaning_notes,
            cleaned_file_path as file_path,
            created_at as timestamp
        FROM file_history 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """
        try:
            result = self.execute_query(query, (user_id,), fetch=True)
            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []
    
    def __del__(self):
        """Clean up connection when object is destroyed"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")