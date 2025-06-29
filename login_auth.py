import streamlit as st
import sqlite3
import hashlib
import secrets
import re
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from pathlib import Path
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationSystem:
    """
    Comprehensive authentication system with login, OTP verification,
    email and phone validation, and technical features.
    """
    
    def __init__(self):
        """Initialize the authentication system"""
        self.db_path = Path("data/users.db")
        self.otp_storage_path = Path("data/otp_storage.json")
        self.init_database()
        self.init_otp_storage()
        
        # Email configuration (you'll need to set these)
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'your-email@gmail.com',  # Change this
            'sender_password': 'your-app-password'   # Change this
        }
    
    def init_database(self):
        """Initialize the SQLite database for user management"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'patient',
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    is_locked BOOLEAN DEFAULT FALSE,
                    lock_until TIMESTAMP,
                    profile_complete BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create login sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def init_otp_storage(self):
        """Initialize OTP storage file"""
        try:
            if not self.otp_storage_path.exists():
                with open(self.otp_storage_path, 'w') as f:
                    json.dump({}, f)
        except Exception as e:
            logger.error(f"OTP storage initialization error: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt using SHA-256"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine password and salt
        combined = password + salt
        # Hash using SHA-256
        hash_obj = hashlib.sha256(combined.encode())
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """Verify password against stored hash and salt"""
        password_hash, _ = self.hash_password(password, stored_salt)
        return password_hash == stored_hash
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        phone_clean = re.sub(r'\D', '', phone)
        # Check if it's a valid length (10-15 digits)
        return 10 <= len(phone_clean) <= 15
    
    def validate_password_strength(self, password: str) -> dict:
        """Validate password strength"""
        errors = []
        warnings = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            warnings.append("Consider adding special characters for better security")
        
        if len(password) < 12:
            warnings.append("Consider using a longer password (12+ characters)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': max(0, 10 - len(errors) * 2)
        }
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    def store_otp(self, identifier: str, otp: str, otp_type: str = 'email'):
        """Store OTP with expiration time"""
        try:
            with open(self.otp_storage_path, 'r') as f:
                otp_data = json.load(f)
            
            # Store OTP with 10-minute expiration
            expiration = datetime.now() + timedelta(minutes=10)
            otp_data[identifier] = {
                'otp': otp,
                'type': otp_type,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiration.isoformat(),
                'attempts': 0
            }
            
            with open(self.otp_storage_path, 'w') as f:
                json.dump(otp_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error storing OTP: {e}")
    
    def verify_otp(self, identifier: str, otp: str) -> bool:
        """Verify OTP and clean up if valid"""
        try:
            with open(self.otp_storage_path, 'r') as f:
                otp_data = json.load(f)
            
            if identifier not in otp_data:
                return False
            
            stored_data = otp_data[identifier]
            expiration = datetime.fromisoformat(stored_data['expires_at'])
            
            # Check if OTP is expired
            if datetime.now() > expiration:
                del otp_data[identifier]
                with open(self.otp_storage_path, 'w') as f:
                    json.dump(otp_data, f, indent=2)
                return False
            
            # Check if too many attempts
            if stored_data['attempts'] >= 3:
                del otp_data[identifier]
                with open(self.otp_storage_path, 'w') as f:
                    json.dump(otp_data, f, indent=2)
                return False
            
            # Increment attempts
            stored_data['attempts'] += 1
            
            # Check if OTP matches
            if stored_data['otp'] == otp:
                # Remove OTP after successful verification
                del otp_data[identifier]
                with open(self.otp_storage_path, 'w') as f:
                    json.dump(otp_data, f, indent=2)
                return True
            
            # Update attempts
            with open(self.otp_storage_path, 'w') as f:
                json.dump(otp_data, f, indent=2)
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return False
    
    def send_email_otp(self, email: str, otp: str) -> bool:
        """Send OTP via email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = email
            msg['Subject'] = "Heart Disease Detector - OTP Verification"
            
            # Email body
            body = f"""
            <html>
            <body>
                <h2>🔐 OTP Verification</h2>
                <p>Your verification code for Heart Disease Detector is:</p>
                <h1 style="color: #667eea; font-size: 2rem; text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px;">{otp}</h1>
                <p><strong>This code will expire in 10 minutes.</strong></p>
                <p>If you didn't request this code, please ignore this email.</p>
                <hr>
                <p style="color: #666; font-size: 0.9rem;">
                    Heart Disease Detector<br>
                    AI-Powered Cardiovascular Health Assessment
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"OTP email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email OTP: {e}")
            return False
    
    def send_sms_otp(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS (placeholder - integrate with SMS service)"""
        # This is a placeholder. In production, integrate with services like:
        # - Twilio
        # - AWS SNS
        # - MessageBird
        # - etc.
        
        logger.info(f"SMS OTP {otp} would be sent to {phone}")
        # For demo purposes, we'll simulate success
        return True
    
    def register_user(self, username: str, email: str, phone: str, password: str, role: str = 'patient') -> dict:
        """Register a new user"""
        try:
            # Validate inputs
            if not self.validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            
            if not self.validate_phone(phone):
                return {'success': False, 'message': 'Invalid phone number format'}
            
            password_validation = self.validate_password_strength(password)
            if not password_validation['is_valid']:
                return {'success': False, 'message': 'Password does not meet requirements', 'errors': password_validation['errors']}
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Store user in database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, email, phone, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, phone, password_hash, salt, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"User registered successfully: {username}")
            return {'success': True, 'message': 'Registration successful', 'user_id': user_id}
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                if 'username' in str(e):
                    return {'success': False, 'message': 'Username already exists'}
                elif 'email' in str(e):
                    return {'success': False, 'message': 'Email already registered'}
                elif 'phone' in str(e):
                    return {'success': False, 'message': 'Phone number already registered'}
            return {'success': False, 'message': 'Registration failed'}
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'message': 'Registration failed'}
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get user by username
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, is_verified, 
                       login_attempts, is_locked, lock_until
                FROM users WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'message': 'Invalid username or password'}
            
            user_id, username, email, stored_hash, stored_salt, role, is_verified, login_attempts, is_locked, lock_until = user
            
            # Check if account is locked
            if is_locked and lock_until:
                lock_time = datetime.fromisoformat(lock_until)
                if datetime.now() < lock_time:
                    remaining_time = lock_time - datetime.now()
                    return {'success': False, 'message': f'Account locked. Try again in {int(remaining_time.total_seconds() / 60)} minutes'}
                else:
                    # Unlock account
                    cursor.execute('''
                        UPDATE users SET is_locked = FALSE, login_attempts = 0, lock_until = NULL
                        WHERE id = ?
                    ''', (user_id,))
            
            # Verify password
            if not self.verify_password(password, stored_hash, stored_salt):
                # Increment login attempts
                new_attempts = login_attempts + 1
                if new_attempts >= 5:
                    # Lock account for 30 minutes
                    lock_until = datetime.now() + timedelta(minutes=30)
                    cursor.execute('''
                        UPDATE users SET login_attempts = ?, is_locked = TRUE, lock_until = ?
                        WHERE id = ?
                    ''', (new_attempts, lock_until.isoformat(), user_id))
                    conn.commit()
                    conn.close()
                    return {'success': False, 'message': 'Too many failed attempts. Account locked for 30 minutes'}
                else:
                    cursor.execute('''
                        UPDATE users SET login_attempts = ? WHERE id = ?
                    ''', (new_attempts, user_id))
                    conn.commit()
                    conn.close()
                    return {'success': False, 'message': f'Invalid password. {5 - new_attempts} attempts remaining'}
            
            # Reset login attempts on successful login
            cursor.execute('''
                UPDATE users SET login_attempts = 0, is_locked = FALSE, lock_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            self.create_session(user_id, session_token)
            
            logger.info(f"User authenticated successfully: {username}")
            return {
                'success': True,
                'message': 'Login successful',
                'user_id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'is_verified': is_verified,
                'session_token': session_token
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {'success': False, 'message': 'Authentication failed'}
    
    def create_session(self, user_id: int, session_token: str):
        """Create a new login session"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Set session to expire in 24 hours
            expires_at = datetime.now() + timedelta(hours=24)
            
            cursor.execute('''
                INSERT INTO login_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Session creation error: {e}")
    
    def verify_session(self, session_token: str) -> dict:
        """Verify if session is valid"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ls.user_id, ls.expires_at, u.username, u.email, u.role, u.is_verified
                FROM login_sessions ls
                JOIN users u ON ls.user_id = u.id
                WHERE ls.session_token = ?
            ''', (session_token,))
            
            session = cursor.fetchone()
            conn.close()
            
            if not session:
                return {'valid': False, 'message': 'Invalid session'}
            
            user_id, expires_at, username, email, role, is_verified = session
            expiration = datetime.fromisoformat(expires_at)
            
            if datetime.now() > expiration:
                return {'valid': False, 'message': 'Session expired'}
            
            return {
                'valid': True,
                'user_id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'is_verified': is_verified
            }
            
        except Exception as e:
            logger.error(f"Session verification error: {e}")
            return {'valid': False, 'message': 'Session verification failed'}
    
    def logout(self, session_token: str):
        """Logout user by removing session"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM login_sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            
            logger.info("User logged out successfully")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def log_audit_event(self, user_id: int, action: str, details: str = None):
        """Log audit events"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")

def render_login_page():
    """Render the login page with authentication"""
    
    # Initialize authentication system
    auth_system = AuthenticationSystem()
    
    # Initialize session state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'otp_identifier' not in st.session_state:
        st.session_state.otp_identifier = None
    if 'otp_type' not in st.session_state:
        st.session_state.otp_type = None
    
    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .auth-header h1 {
            color: #2c3e50;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .auth-header p {
            color: #7f8c8d;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2c3e50;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .auth-button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .auth-button:hover {
            transform: translateY(-2px);
        }
        .auth-link {
            text-align: center;
            margin-top: 1rem;
        }
        .auth-link a {
            color: #667eea;
            text-decoration: none;
        }
        .otp-container {
            text-align: center;
            margin: 2rem 0;
        }
        .otp-input {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        .otp-input input {
            width: 50px;
            height: 50px;
            text-align: center;
            font-size: 1.5rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Page header
    st.markdown("""
        <div class="auth-header">
            <h1>❤️ HeartCare Pro</h1>
            <p>Your AI-Powered Cardiovascular Health Companion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
    
    with tab1:
        render_login_tab(auth_system)
    
    with tab2:
        render_register_tab(auth_system)
    
    with tab3:
        render_forgot_password_tab(auth_system)

def render_login_tab(auth_system):
    """Render the login tab"""
    st.markdown("### 👤 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            st.markdown("")
            st.markdown("")
            if st.form_submit_button("🔑 Login", type="primary", use_container_width=True):
                if username and password:
                    result = auth_system.authenticate_user(username, password)
                    
                    if result['success']:
                        # Store user session
                        st.session_state.user_authenticated = True
                        st.session_state.user_data = {
                            'user_id': result['user_id'],
                            'username': result['username'],
                            'email': result['email'],
                            'role': result['role'],
                            'is_verified': result['is_verified'],
                            'session_token': result['session_token']
                        }
                        
                        # Log audit event
                        auth_system.log_audit_event(
                            result['user_id'], 
                            'LOGIN', 
                            f"User {result['username']} logged in successfully"
                        )
                        
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("Please fill in all fields")

def render_register_tab(auth_system):
    """Render the registration tab"""
    st.markdown("### 📝 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        phone = st.text_input("Phone Number", placeholder="Enter your phone number")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        role = st.selectbox("Role", ["Patient", "Doctor", "Researcher"])
        
        # Password strength indicator
        if password:
            strength = auth_system.validate_password_strength(password)
            if strength['errors']:
                for error in strength['errors']:
                    st.error(f"❌ {error}")
            if strength['warnings']:
                for warning in strength['warnings']:
                    st.warning(f"⚠️ {warning}")
            
            # Password strength bar
            st.progress(strength['score'] / 10)
            st.caption(f"Password Strength: {strength['score']}/10")
        
        if st.form_submit_button("📝 Register", type="primary", use_container_width=True):
            if username and email and phone and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    result = auth_system.register_user(username, email, phone, password, role.lower())
                    
                    if result['success']:
                        st.success("✅ Registration successful!")
                        st.info("Please verify your email and phone number to complete registration.")
                        
                        # Send verification OTPs
                        email_otp = auth_system.generate_otp()
                        phone_otp = auth_system.generate_otp()
                        
                        auth_system.store_otp(email, email_otp, 'email')
                        auth_system.store_otp(phone, phone_otp, 'phone')
                        
                        # Send OTPs (in production, these would actually send)
                        auth_system.send_email_otp(email, email_otp)
                        auth_system.send_sms_otp(phone, phone_otp)
                        
                        st.info(f"📧 Verification codes sent to {email} and {phone}")
                    else:
                        st.error(f"❌ {result['message']}")
            else:
                st.error("Please fill in all fields")

def render_forgot_password_tab(auth_system):
    """Render the forgot password tab"""
    st.markdown("### 🔄 Forgot Password")
    
    if not st.session_state.otp_sent:
        with st.form("forgot_password_form"):
            identifier = st.text_input("Email or Phone", placeholder="Enter your email or phone number")
            
            if st.form_submit_button("📤 Send Reset Code", type="primary", use_container_width=True):
                if identifier:
                    # Check if user exists
                    conn = sqlite3.connect(str(auth_system.db_path))
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT id, email, phone FROM users WHERE email = ? OR phone = ?', (identifier, identifier))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        user_id, email, phone = user
                        
                        # Generate and send OTP
                        otp = auth_system.generate_otp()
                        auth_system.store_otp(identifier, otp, 'reset')
                        
                        if '@' in identifier:
                            auth_system.send_email_otp(identifier, otp)
                        else:
                            auth_system.send_sms_otp(identifier, otp)
                        
                        st.session_state.otp_sent = True
                        st.session_state.otp_identifier = identifier
                        st.session_state.otp_type = 'reset'
                        
                        st.success(f"✅ Reset code sent to {identifier}")
                        st.rerun()
                    else:
                        st.error("❌ No account found with this email or phone number")
                else:
                    st.error("Please enter your email or phone number")
    else:
        # OTP verification
        st.markdown("### 🔐 Enter Reset Code")
        st.info(f"Enter the code sent to {st.session_state.otp_identifier}")
        
        with st.form("otp_verification_form"):
            otp = st.text_input("Reset Code", placeholder="Enter 6-digit code")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            if st.form_submit_button("🔄 Reset Password", type="primary", use_container_width=True):
                if otp and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        # Verify OTP
                        if auth_system.verify_otp(st.session_state.otp_identifier, otp):
                            # Update password
                            password_hash, salt = auth_system.hash_password(new_password)
                            
                            conn = sqlite3.connect(str(auth_system.db_path))
                            cursor = conn.cursor()
                            
                            cursor.execute('''
                                UPDATE users SET password_hash = ?, salt = ?
                                WHERE email = ? OR phone = ?
                            ''', (password_hash, salt, st.session_state.otp_identifier, st.session_state.otp_identifier))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success("✅ Password reset successful!")
                            
                            # Reset session state
                            st.session_state.otp_sent = False
                            st.session_state.otp_identifier = None
                            st.session_state.otp_type = None
                            
                            st.rerun()
                        else:
                            st.error("❌ Invalid or expired reset code")
                else:
                    st.error("Please fill in all fields")
        
        if st.button("← Back to Login"):
            st.session_state.otp_sent = False
            st.session_state.otp_identifier = None
            st.session_state.otp_type = None
            st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    if 'user_authenticated' in st.session_state and st.session_state.user_authenticated:
        return True
    return False

def get_user_data():
    """Get current user data"""
    if check_authentication():
        return st.session_state.user_data
    return None

def logout_user():
    """Logout current user"""
    if 'user_data' in st.session_state and 'session_token' in st.session_state.user_data:
        auth_system = AuthenticationSystem()
        auth_system.logout(st.session_state.user_data['session_token'])
    
    # Clear session state
    if 'user_authenticated' in st.session_state:
        del st.session_state.user_authenticated
    if 'user_data' in st.session_state:
        del st.session_state.user_data
    
    st.rerun()

def get_user_role():
    """Get the current user's role."""
    if 'user_data' in st.session_state:
        return st.session_state.user_data.get('role', 'patient')
    return 'patient'

def is_doctor():
    """Check if current user is a doctor."""
    return get_user_role() == 'doctor'

def is_patient():
    """Check if current user is a patient."""
    return get_user_role() == 'patient'
