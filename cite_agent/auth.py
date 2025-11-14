"""
Authentication System for Nocturnal Archive
Handles user login, registration, and session management
"""

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict
import requests
from datetime import datetime, timedelta

class AuthenticationError(Exception):
    """Authentication failed"""
    pass

class AuthManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".nocturnal_archive"
        self.config_dir.mkdir(exist_ok=True)
        
        self.session_file = self.config_dir / "session.json"
        self.api_base = os.getenv("NOCTURNAL_AUTH_API", "https://cite-agent-api-720dfadd602c.herokuapp.com")
        
    def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user with email and password
        Returns user session data including temp API key for local mode
        """
        try:
            # Call auth API - send plain password (backend hashes it)
            response = requests.post(
                f"{self.api_base}/api/auth/login",
                json={
                    "email": email,
                    "password": password  # Send plain password over HTTPS
                },
                timeout=10
            )
            
            if response.status_code == 200:
                session_data = response.json()
                self._save_session(session_data)
                return session_data
            elif response.status_code == 401:
                raise AuthenticationError("Invalid email or password")
            else:
                raise AuthenticationError(f"Login failed: {response.status_code}")
                
        except requests.RequestException as e:
            # Fallback: offline mode with local validation
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return self._offline_login(email, password_hash)
    
    def register(self, email: str, password: str) -> Dict:
        """
        Register new user with email and password only (no license key for beta)
        Returns user session data including temp API key for local mode
        """
        try:
            response = requests.post(
                f"{self.api_base}/api/auth/register",
                json={
                    "email": email,
                    "password": password  # Send plain password over HTTPS (backend will hash)
                },
                timeout=10
            )
            
            if response.status_code == 201:
                session_data = response.json()
                self._save_session(session_data)
                return session_data
            elif response.status_code == 409:
                raise AuthenticationError("Email already registered")
            else:
                raise AuthenticationError(f"Registration failed: {response.status_code}")
                
        except requests.RequestException as e:
            # Fallback: create local session (beta mode)
            return self._offline_register(email, password)
    
    def get_session(self) -> Optional[Dict]:
        """Get current session if valid"""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                session = json.load(f)
            
            # Check if session expired
            expires_at = datetime.fromisoformat(session.get('expires_at', '2000-01-01'))
            if datetime.now() > expires_at:
                self.logout()
                return None
            
            return session
            
        except (json.JSONDecodeError, KeyError):
            return None
    
    def logout(self):
        """Clear current session"""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def refresh_session(self) -> bool:
        """Refresh session token"""
        session = self.get_session()
        if not session:
            return False
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/refresh",
                headers={"Authorization": f"Bearer {session['token']}"},
                timeout=10
            )
            
            if response.status_code == 200:
                new_session = response.json()
                self._save_session(new_session)
                return True
                
        except requests.RequestException:
            pass
        
        return False
    
    def _save_session(self, session_data: Dict):
        """
        Save session to file with proper field mapping for agent compatibility
        Maps backend response fields to agent-expected fields
        """
        # Map backend response to agent-expected format
        mapped_session = {
            'email': session_data.get('email'),
            'auth_token': session_data.get('access_token'),  # Agent expects 'auth_token'
            'account_id': session_data.get('user_id'),  # Agent expects 'account_id'
            'daily_token_limit': session_data.get('daily_token_limit', 25000),
            'expires_at': session_data.get('expires_at'),
        }

        # Add temp API key fields if present (for local mode)
        if 'temp_api_key' in session_data and session_data['temp_api_key']:
            mapped_session['temp_api_key'] = session_data['temp_api_key']
            mapped_session['temp_key_expires'] = session_data.get('temp_key_expires')
            mapped_session['temp_key_provider'] = session_data.get('temp_key_provider', 'cerebras')

        # Add expiration if not present (30 days from now)
        if not mapped_session.get('expires_at'):
            expires_at = datetime.now() + timedelta(days=30)
            mapped_session['expires_at'] = expires_at.isoformat()

        with open(self.session_file, 'w') as f:
            json.dump(mapped_session, f, indent=2)

        # Secure permissions (owner only)
        os.chmod(self.session_file, 0o600)
    
    def _offline_login(self, email: str, password_hash: str) -> Dict:
        """Offline login fallback (beta mode)"""
        # Check if user exists in local cache
        users_file = self.config_dir / "users.json"
        
        if not users_file.exists():
            raise AuthenticationError("No internet connection and no local user found")
        
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        user = users.get(email)
        if not user or user['password_hash'] != password_hash:
            raise AuthenticationError("Invalid credentials")
        
        # Create offline session
        session = {
            "email": email,
            "user_id": user['user_id'],
            "access_token": "offline-" + hashlib.sha256(email.encode()).hexdigest()[:16],
            "daily_token_limit": user.get('daily_token_limit', 25000),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "offline_mode": True
        }
        
        self._save_session(session)
        return session
    
    def _offline_register(self, email: str, password: str) -> Dict:
        """Offline registration fallback (beta mode) - no license key needed"""
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Save user locally
        users_file = self.config_dir / "users.json"
        users = {}
        
        if users_file.exists():
            with open(users_file, 'r') as f:
                users = json.load(f)
        
        if email in users:
            raise AuthenticationError("Email already registered")
        
        user_id = hashlib.sha256(email.encode()).hexdigest()[:12]
        users[email] = {
            "user_id": user_id,
            "password_hash": password_hash,
            "daily_limit": 25,
            "created_at": datetime.now().isoformat()
        }
        
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        os.chmod(users_file, 0o600)
        
        # Create session
        session = {
            "email": email,
            "user_id": user_id,
            "access_token": "offline-" + hashlib.sha256(email.encode()).hexdigest()[:16],
            "daily_token_limit": 25000,
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "offline_mode": True
        }
        
        self._save_session(session)
        return session
    
    def _validate_license_format(self, license_key: str) -> bool:
        """Validate license key format: NA-BETA-{uid}-{expiry}-{checksum}"""
        parts = license_key.split("-")
        return (
            len(parts) == 5 and
            parts[0] == "NA" and
            parts[1] == "BETA" and
            len(parts[2]) == 8 and  # user_id
            len(parts[3]) == 8 and  # expiry date
            len(parts[4]) == 8      # checksum
        )
    
    def generate_license_key(self, email: str, days: int = 30) -> str:
        """
        Generate a license key for a user
        Format: NA-BETA-{user_id}-{expiry}-{checksum}
        """
        # Generate user ID from email
        user_id = hashlib.sha256(email.encode()).hexdigest()[:8]
        
        # Generate expiry date
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.strftime("%Y%m%d")
        
        # Generate checksum
        data = f"{email}{user_id}{expiry_str}"
        checksum = hashlib.sha256(data.encode()).hexdigest()[:8]
        
        # Construct license key
        license_key = f"NA-BETA-{user_id}-{expiry_str}-{checksum}"
        
        return license_key
    
    def _verify_license_offline(self, license_key: str, email: str) -> bool:
        """Verify license key offline"""
        try:
            parts = license_key.split("-")
            if len(parts) != 5:
                return False
            
            user_id_provided, expiry_str, checksum_provided = parts[2], parts[3], parts[4]
            
            # Verify user ID matches email
            user_id_expected = hashlib.sha256(email.encode()).hexdigest()[:8]
            if user_id_provided != user_id_expected:
                return False
            
            # Check expiry
            expiry_date = datetime.strptime(expiry_str, "%Y%m%d")
            if datetime.now() > expiry_date:
                return False
            
            # Verify checksum
            data = f"{email}{user_id_provided}{expiry_str}"
            checksum_expected = hashlib.sha256(data.encode()).hexdigest()[:8]
            
            return checksum_provided == checksum_expected
            
        except Exception:
            return False
