import streamlit as st
import hashlib
import secrets
from typing import Optional, Dict, Any, Tuple
from modules.db_connector import DBHandler

class AuthManager:
    def __init__(self):
        self.db = DBHandler()
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        """Securely hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${hashed.hex()}"
    
    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hashed = stored_password.split('$')
            new_hash = self.hash_password(provided_password, salt)
            return new_hash == stored_password
        except:
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return st.session_state.user if 'user' in st.session_state else None
    
    def get_user_id(self) -> Optional[int]:
        """Get current user ID"""
        user = self.get_current_user()
        return user.get('user_id') if user else None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.get_current_user() is not None
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Authenticate user with email and password"""
        if not email or not password:
            return False, "Email and password are required"
        
        user = self.db.get_user_by_email(email)
        if user and self.verify_password(user['password_hash'], password):
            st.session_state.user = {
                'user_id': user['user_id'],
                'email': user['email']
            }
            return True, "Login successful"
        return False, "Invalid email or password"
    
    def register_user(self, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """Register new user"""
        if not email or not password or not confirm_password:
            return False, "All fields are required"
        
        if password != confirm_password:
            return False, "Passwords don't match"
        
        if self.db.get_user_by_email(email):
            return False, "Email already registered"
        
        try:
            password_hash = self.hash_password(password)
            user_id = self.db.create_user(email, password_hash)
            st.session_state.user = {
                'user_id': user_id,
                'email': email
            }
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def logout_user(self):
        """Logout current user"""
        if 'user' in st.session_state:
            st.session_state.user = None