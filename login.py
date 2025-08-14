import dash
from dash import Dash, dcc, html, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime
import hashlib
import secrets
import re
import bcrypt
from flask import session, request
import logging

import mysql.connector
from mysql.connector import Error

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/login/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ]
)
app.index_string = '''
<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
      /* Global Styles */
      :root {
        --primary-yellow: #FFC107; /* Consistent yellow accent */
        --light-yellow-outline: rgba(255, 193, 7, 0.3); /* Soft yellow for outlines */
        --primary-white: #ffffff;
        --dark-text: #343a40;
        --medium-text: #6c757d;
        --light-grey-bg: #f8f9fa;
        --border-color: #e9ecef;
        --hover-border: #adb5bd;
        --button-dark: #212529; /* Classy dark button background */
        --button-dark-hover: #343a40;
        --success-color: #28a745;
        --error-color: #dc3545;
        --card-shadow-light: 0 6px 20px rgba(0, 0, 0, 0.08);
        --card-shadow-dark: 0 10px 30px rgba(0, 0, 0, 0.2);
        --transition-speed: 0.3s ease-in-out;
      }

      /* Reset & Base Styles */
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: 'Poppins', sans-serif; /* All fonts Poppins */
        background-color: var(--primary-white); /* White background */
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        position: relative;
        overflow: hidden;
        color: var(--dark-text);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      /* Animated Background Elements */
      .bg-gradient-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 20% 80%, rgba(255, 193, 7, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 193, 7, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
      }

      /* Floating Icons Background */
      .floating-icons {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 2;
      }

      .floating-icon {
        position: absolute;
        font-size: 28px; /* Slightly larger icons */
        color: rgba(0, 0, 0, 0.05); /* Very subtle black icons */
        animation: float 20s infinite linear;
      }

      @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 0.5; }
        90% { opacity: 0.5; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
      }

      /* Main Container */
      .auth-container {
        display: grid;
        grid-template-columns: 5fr 8fr;
        max-width: 1100px; /* Optimal size for the form */
        width: 100%;
        background: var(--primary-white);
        border-radius: 20px; /* Smoother border-radius */
        overflow: hidden;
        box-shadow: var(--card-shadow-light);
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
        z-index: 10;
        transition: transform var(--transition-speed), box-shadow var(--transition-speed);
      }

      .auth-container:hover {
        transform: translateY(-5px);
        box-shadow: var(--card-shadow-dark);
      }

      /* Left Panel - Hero Section */
      .auth-left {
        background: linear-gradient(145deg, #1A1A1A 0%, #343434 100%); /* Graded, professional look */
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 50px 30px;
        position: relative;
        overflow: hidden;
      }

      .auth-left::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 30% 40%, rgba(255, 193, 7, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 70% 80%, rgba(255, 193, 7, 0.08) 0%, transparent 50%);
        pointer-events: none;
      }

      .auth-left-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 380px;
      }

      .auth-left .logo {
        width: 90px;
        height: 90px;
        background-color: var(--primary-yellow);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 2.5rem;
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.3);
        font-size: 40px;
        color: var(--dark-text);
        transition: transform 0.3s ease;
      }

      .auth-left .logo:hover {
          transform: scale(1.05);
      }

      .auth-left h2 {
        font-size: 2.3rem; /* Adjusted for better proportion */
        font-weight: 700;
        margin-bottom: 1.2rem;
        letter-spacing: -0.03em;
        color: var(--primary-yellow); /* Direct yellow for clarity */
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
      }

      .auth-left .tagline {
        font-size: 1.05rem;
        line-height: 1.5;
        margin-bottom: 2rem;
        opacity: 0.9;
        font-weight: 400;
      }

      .feature-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
      }

      .feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.95rem;
        font-weight: 500;
        opacity: 0.9;
      }

      .feature-icon {
        width: 28px;
        height: 28px;
        background: var(--primary-yellow);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--dark-text);
        font-size: 14px;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
      }

      .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 2rem;
      }

      .stat-item {
        text-align: center;
      }

      .stat-number {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--primary-yellow);
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
      }

      .stat-label {
        font-size: 0.85rem;
        opacity: 0.7;
        font-weight: 500;
      }

      /* Right Panel - Form Section */
      .auth-right {
        background: var(--primary-white);
        padding: 60px 50px; /* Adjusted padding */
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .auth-form {
        width: 100%;
        max-width: 450px; /* Max-width for the form content */
      }

      .form-header {
        text-align: center;
        margin-bottom: 3rem;
      }

      .form-header h3 {
        color: var(--dark-text);
        font-size: 2rem; /* Consistent with Poppins sizing */
        font-weight: 700;
        margin-bottom: 0.8rem;
        letter-spacing: -0.02em;
      }

      .form-header p {
        color: var(--medium-text);
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.6;
      }

      /* Form Inputs */
      .form-group {
        margin-bottom: 1.8rem; /* More vertical spacing */
      }

      .form-label {
        display: block;
        margin-bottom: 0.8rem;
        font-weight: 600;
        color: var(--dark-text);
        font-size: 0.9rem;
        letter-spacing: 0.01em;
      }

      .input-group {
        position: relative;
      }

      .form-control {
        width: 100%;
        padding: 14px 18px 14px 50px; /* Adjust padding for icon */
        border: 1px solid var(--border-color); /* Lighter border */
        border-radius: 10px; /* Softer edges */
        font-size: 0.95rem;
        font-weight: 400;
        transition: border-color var(--transition-speed), box-shadow var(--transition-speed), transform 0.1s ease;
        background: var(--light-grey-bg); /* Slightly off-white background */
        color: var(--dark-text);
      }

      .form-control:focus {
        outline: none;
        border-color: var(--primary-yellow); /* Light yellow outline on focus */
        box-shadow: 0 0 0 3px var(--light-yellow-outline); /* Soft glow */
        background: var(--primary-white);
        transform: translateY(-1px); /* Subtle lift */
      }

      # .form-control:hover {
      #   border-color: var(--hover-border);
      # }

      /* Remove red highlighting by default */
      .form-control:not(:focus):not(:placeholder-shown):invalid {
        border-color: var(--border-color); /* Keep normal border */
        box-shadow: none; /* No shadow */
      }


      .input-icon {
        position: absolute;
        left: 18px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--medium-text);
        font-size: 1rem;
        z-index: 2;
      }

      .password-toggle {
        position: absolute;
        right: 18px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: var(--medium-text);
        font-size: 1.05rem;
        z-index: 2;
        transition: color 0.2s ease;
      }

      .password-toggle:hover {
        color: var(--primary-yellow);
      }

      /* Remember & Forgot Section */
      .remember-forgot {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2.5rem;
        font-size: 0.9rem;
      }

      .remember-forgot a {
        color: var(--dark-text); /* Black text for links */
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s ease;

      }

      .remember-forgot a:hover {
        color: var(--primary-yellow); /* Yellow on hover */
      }

      /* Custom Checkbox */
      .checkbox-container {
          display: block;
          position: relative;
          padding-left: 28px;
          cursor: pointer;
          font-size: 0.9rem;
          color: var(--medium-text);
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;

      }

      .checkbox-container input {
          position: absolute;
          opacity: 0;
          cursor: pointer;
          height: 0;
          width: 0;
      }

      .checkmark {
          position: absolute;
          top: 0;
          left: 0;
          height: 20px;
          width: 20px;
          background-color: var(--light-grey-bg);
          border: 1px solid var(--border-color);
          border-radius: 5px;
          transition: all var(--transition-speed);

      }

      .checkbox-container:hover input ~ .checkmark {
          background-color: #e0e0e0;
      }

      .checkbox-container input:checked ~ .checkmark {
          background-color: var(--primary-yellow);
          border-color: var(--primary-yellow);
      }

      .checkmark:after {
          content: "";
          position: absolute;
          display: none;
      }

      .checkbox-container input:checked ~ .checkmark:after {
          display: block;

      }

      .checkbox-container .checkmark:after {
          left: 7px;
          top: 3px;
          width: 5px;
          height: 10px;
          border: solid var(--dark-text); /* Checkmark color */
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
      }


      /* Submit Button */
      .btn-primary {
        width: 100%;
        padding: 16px;
        background: var(--button-dark); /* Classy dark background */
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1.05rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        cursor: pointer;
        transition: all var(--transition-speed);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
      }

      .btn-primary::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent); /* Subtle shine */
        transition: left 0.5s ease;
      }

      .btn-primary:hover::before {
        left: 100%;
      }

      .btn-primary:hover {
        background: var(--button-dark-hover);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
      }

      .btn-primary:active {
        transform: translateY(0);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      }

      .btn-primary:disabled {
        background: #cccccc;
        cursor: not-allowed;
        box-shadow: none;
        transform: none;
      }

      /* Alerts */
      .alert {
        margin-bottom: 1.5rem;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 500;
        border-left: 4px solid;
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .alert-success {
        background: rgba(40, 167, 69, 0.1); /* Light green tint */
        color: var(--success-color);
        border-left-color: var(--success-color);
      }

      .alert-danger {
        background: rgba(220, 53, 69, 0.1); /* Light red tint */
        color: var(--error-color);
        border-left-color: var(--error-color);
      }

      /* Form Footer */
      .form-footer {
        text-align: center;
        margin-top: 2.5rem;
        font-size: 0.95rem;
        color: var(--medium-text);
      }

      .form-footer a {
        color: var(--button-dark); /* Dark link color for contrast */
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s ease;
      }

      .form-footer a:hover {
        color: var(--primary-yellow);
      }

      /* Responsive Design */
      @media (max-width: 1024px) {
        .auth-container {
          grid-template-columns: 1fr;
          max-width: 550px; /* Adjust for single column layout */
          margin: 0 auto;
        }
        
        .auth-left {
          display: none; /* Hide left panel on smaller screens */
        }
        
        .auth-right {
          padding: 50px 40px;
        }
      }

      @media (max-width: 768px) {
        body {
          padding: 10px;
        }
        
        .auth-container {
          border-radius: 16px;
        }
        
        .auth-right {
          padding: 40px 30px;
        }
        
        .form-header h3 {
          font-size: 1.8rem;
        }
        
        .form-control {
          padding: 12px 16px 12px 45px;
        }
        
        .btn-primary {
          padding: 14px;
          font-size: 1rem;
        }
      }

      /* Loading Animation */
      .loading-spinner {
        display: inline-block;
        width: 18px;
        height: 18px;
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    </style>
  </head>
  <body>
    <div class="floating-icons">
      <i class="floating-icon fas fa-warehouse" style="left: 10%; animation-delay: 0s;"></i>
      <i class="floating-icon fas fa-boxes" style="left: 20%; animation-delay: 2s;"></i>
      <i class="floating-icon fas fa-truck" style="left: 30%; animation-delay: 4s;"></i>
      <i class="floating-icon fas fa-barcode" style="left: 40%; animation-delay: 6s;"></i>
      <i class="floating-icon fas fa-clipboard-list" style="left: 50%; animation-delay: 8s;"></i>
      <i class="floating-icon fas fa-chart-line" style="left: 60%; animation-delay: 10s;"></i>
      <i class="floating-icon fas fa-cogs" style="left: 70%; animation-delay: 12s;"></i>
      <i class="floating-icon fas fa-shipping-fast" style="left: 80%; animation-delay: 14s;"></i>
      <i class="floating-icon fas fa-dolly" style="left: 90%; animation-delay: 16s;"></i>
    </div>

    <div class="bg-gradient-overlay"></div>

    {%app_entry%}
    <footer>
      {%config%} {%scripts%} {%renderer%}
    </footer>
  </body>
</html>
'''
# Set Flask secret key for sessions
if not app.server.secret_key:
    app.server.secret_key = secrets.token_hex(32)
    logger = logging.getLogger(__name__)
    logger.info("Flask secret key generated for session management")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',           
    'database': 'warehouse_db',
    'charset': 'utf8mb4',
    'raise_on_warnings': True
}

# Admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Theadministrator"

# CSO role to page mapping
CSO_ROLE_PAGES = {
    'access_units': '/admin/units',
    'access_payments': '/admin/payments', 
    'access_analytics': '/admin/analytics',
    'access_complaints': '/admin/complaints',
    'general_functions': '/admin/bookings'
}

def get_db_connection():
    """Get MySQL database connection via mysql.connector."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            raise_on_warnings=DB_CONFIG['raise_on_warnings']
        )
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password_bcrypt(password):
    """Hash password using bcrypt for CSO officers"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password_bcrypt(password, hashed):
    """Verify bcrypt password for CSO officers"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"BCrypt password verification error: {e}")
        return False

def hash_password_pbkdf2(password):
    """Hash password using PBKDF2 with salt for regular users."""
    import os
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + pwdhash

def verify_password_pbkdf2(password, stored_hash):
    """Verify PBKDF2 password for regular users."""
    try:
        if len(stored_hash) < 32:
            return False
        salt = stored_hash[:32]
        stored_pwdhash = stored_hash[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash == stored_pwdhash
    except Exception as e:
        logger.error(f"PBKDF2 password verification error: {e}")
        return False

def hash_password_simple(password):
    """Simple SHA-256 hash for admin password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_admin_credentials(email, password):
    """Verify admin credentials."""
    return (email.lower() == ADMIN_EMAIL.lower() and 
            password == ADMIN_PASSWORD)

def verify_cso_credentials(email, password):
    """Verify CSO officer credentials."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            c.cso_id,
            c.cso_name,
            c.email,
            c.password_hash,
            c.is_active,
            f.function_role,
            f.function_name
        FROM cso_officers c
        JOIN functions f ON c.function_id = f.function_id
        WHERE c.email = %s AND c.is_active = 1 AND f.is_active = 1
        """
        cursor.execute(query, (email.strip().lower(),))
        cso = cursor.fetchone()
        
        if not cso:
            logger.warning(f"No active CSO found for email: {email}")
            return False, "Invalid credentials"
        
        # Verify password using bcrypt
        if not verify_password_bcrypt(password, cso['password_hash']):
            logger.warning(f"Password mismatch for CSO: {email}")
            return False, "Invalid credentials"
        
        # Update last_login
        try:
            cursor.execute(
                "UPDATE cso_officers SET last_login = %s WHERE cso_id = %s",
                (datetime.now(), cso['cso_id'])
            )
            conn.commit()
        except Error as e:
            logger.error(f"Failed to update CSO last_login: {e}")
        
        return True, {
            'cso_id': cso['cso_id'],
            'cso_name': cso['cso_name'],
            'email': cso['email'],
            'function_role': cso['function_role'],
            'function_name': cso['function_name']
        }
        
    except Error as e:
        logger.error(f"CSO verification error: {e}")
        return False, "Authentication failed"
    finally:
        if conn:
            conn.close()

def verify_user_credentials(email, password):
    """Verify regular user credentials."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
          id,
          email,
          password_hash,
          status,
          IFNULL(is_verified, 0) AS is_verified,
          role AS user_type
        FROM users
        WHERE email = %s
        """
        cursor.execute(query, (email.strip().lower(),))
        user = cursor.fetchone()
        
        if not user:
            return False, "Invalid email or password"
            
        # Check account status
        if user['status'] == 'pending':
            return False, {
                'error': 'account_pending',
                'message': 'Your account is pending approval. Please check your email for verification instructions.',
                'redirect': '/activate_account'
            }
            
        if user['status'] != 'active':
            return False, "Account is not active. Please contact support."
            
        if not user['is_verified']:
            return False, {
                'error': 'account_not_verified',
                'message': 'Account not verified. Please check your email for verification link.',
                'redirect': '/activate_account'
            }
        
        # Verify password
        stored_hash = user['password_hash']
        if isinstance(stored_hash, str):
            try:
                stored_hash = bytes.fromhex(stored_hash)
            except ValueError:
                return False, "Authentication failed"
        
        if not verify_password_pbkdf2(password, stored_hash):
            return False, "Invalid email or password"
        
        # Update last_login
        try:
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(), user['id'])
            )
            conn.commit()
        except Error as e:
            logger.error(f"Failed to update last_login: {e}")
        
        return True, {
            'user_id': user['id'],
            'email': user['email'],
            'user_type': user['user_type'],
            'status': user['status']
        }
        
    except Error as e:
        logger.error(f"User verification error: {e}")
        return False, "Authentication failed"
    finally:
        if conn:
            conn.close()

def create_session(user_data, user_type):
    """Create Flask session for authenticated user."""
    try:
        session.clear()
        session['authenticated'] = True
        session['user_type'] = user_type
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        
        if user_type == 'admin':
            session['user_id'] = 'admin'
            session['email'] = user_data.get('email', ADMIN_EMAIL)
            session['is_admin'] = True
            
        elif user_type == 'cso':
            session['cso_id'] = user_data['cso_id']
            session['cso_name'] = user_data['cso_name']
            session['email'] = user_data['email']
            session['function_role'] = user_data['function_role']
            session['function_name'] = user_data['function_name']
            
        elif user_type == 'user':
            session['user_id'] = user_data['user_id']
            session['email'] = user_data['email']
            session['status'] = user_data['status']
        
        logger.info(f"Session created for {user_type}: {user_data.get('email', 'N/A')}")
        return True
        
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        return False

def get_redirect_url(user_type, function_role=None, next_url=None):
    """Get appropriate redirect URL based on user type."""
    if user_type == 'admin':
        return "/admin/analytics"
    elif user_type == 'cso':
        return CSO_ROLE_PAGES.get(function_role, '/dashboard')
    elif user_type == 'user':
        # Return to previous URL or default dashboard
        return next_url if next_url else "/units"
    else:
        return "/login"

# Layout remains the same as original
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='session-store', storage_type='session'),
    
    html.Div([
        html.Div([
            # Left side - Hero section
            html.Div([
                html.Div([
                    html.Img(
                        src=app.get_asset_url('images/logo.png'),
                        alt="Logo",
                        style={
                            'maxWidth': '120px',
                            'position': 'absolute',
                            'top': '30px',
                            'left': '30px',
                            'zIndex': '2'
                        }
                    ),
                ], style={
                    'position': 'relative',
                    'height': '100%',
                    'width': '100%',
                })
            ], className="auth-left", style={
                'flexBasis': '50%',
                'minWidth': '70vh',
                'backgroundImage': 'url("https://images.unsplash.com/photo-1553413077-190dd305871c?fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8d2FyZWhvdXNlfGVufDB8fDB8fHww&ixlib=rb-4.1.0&q=60&w=3000")',
                'backgroundSize': 'cover',
                'backgroundPosition': 'center',
                'backgroundRepeat': 'no-repeat',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'position': 'relative',
            }),
            
            # Right side - Sign in form
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Welcome Back"),
                        html.P("Sign in to access your warehouse dashboard")
                    ], className="form-header"),
                    
                    # Message container
                    html.Div(id="message-container", className="mb-3"),
                    
                    # Sign in form
                    html.Div([
                        html.Div([
                            html.Label("Email Address", className="form-label"),
                            html.Div([
                                html.I(className="fas fa-envelope input-icon"),
                                dcc.Input(
                                    id="email-input",
                                    type="email",
                                    placeholder="Enter your email address",
                                    className="form-control",
                                    required=False
                                )
                            ], className="input-group")
                        ], className="form-group"),
                        
                        html.Div([
                            html.Label("Password", className="form-label"),
                            html.Div([
                                html.I(className="fas fa-lock input-icon"),
                                dcc.Input(
                                    id="password-input",
                                    type="password",
                                    placeholder="Enter your password",
                                    className="form-control",
                                    required=False
                                ),
                                html.I(id="password-toggle", className="fas fa-eye password-toggle", n_clicks=0, style={"cursor": "pointer"})
                            ], className="input-group")
                        ], className="form-group"),
                        
                        html.Div([
                            html.Div([
                                dcc.Checklist(
                                    id="remember-me",
                                    options=[{"label": "Remember me", "value": "remember"}],
                                    value=[],
                                    className="checkbox-group"
                                )
                            ]),
                            html.A("Forgot Password?", href="#", className="forgot-link")
                        ], className="remember-forgot"),
                        
                        html.Button(
                            id="signin-btn",
                            children="Sign In to Dashboard",
                            type="button",
                            className="btn-primary",
                            n_clicks=0
                        )
                    ], id="signin-form"),
                    
                    html.Div([
                        html.P([
                            "Don't have an account? ",
                            html.A("Request access here", href="/signup")
                        ])
                    ], className="form-footer")
                ], className="auth-form")
            ], className="auth-right")
        ], className="auth-container")
    ], className="vh-100 d-flex align-items-center justify-content-center")
], fluid=True, className="p-0")

# Clientside callback for password toggle
clientside_callback(
    """
    function(n_clicks) {
        const passwordInput = document.getElementById('password-input');
        const toggleIcon = document.getElementById('password-toggle');

        if (passwordInput && toggleIcon) {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.className = 'fas fa-eye-slash password-toggle';
            } else {
                passwordInput.type = 'password';
                toggleIcon.className = 'fas fa-eye password-toggle';
            }
        }
        return '';
    }
    """,
    Output('dummy-output', 'children'),
    Input('password-toggle', 'n_clicks')
)

# Main sign in callback
@app.callback(
    [Output('message-container', 'children'),
     Output('url', 'href'),
     Output('session-store', 'data'),
     Output('signin-btn', 'children'),
     Output('signin-btn', 'disabled')],
    [Input('signin-btn', 'n_clicks')],
    [State('email-input', 'value'),
     State('password-input', 'value'),
     State('remember-me', 'value'),
     State('url', 'search')]  # Get query parameters for next URL
)
def handle_signin(n_clicks, email, password, remember, search_params):
    if n_clicks == 0:
        return "", dash.no_update, {}, "Sign In to Dashboard", False
    
    # Validation
    if not email or not password:
        return dbc.Alert("Please enter both email and password", color="danger"), dash.no_update, {}, "Sign In to Dashboard", False
    
    email = email.strip().lower()
    
    if not validate_email(email):
        return dbc.Alert("Please enter a valid email address", color="danger"), dash.no_update, {}, "Sign In to Dashboard", False
    
    # Extract next URL from query parameters
    next_url = None
    if search_params:
        from urllib.parse import parse_qs
        params = parse_qs(search_params.lstrip('?'))
        next_url = params.get('next', [None])[0]
    
    logger.info(f"Login attempt for email: {email}")
    
    # Try admin login first
    if verify_admin_credentials(email, password):
        if create_session({'email': email}, 'admin'):
            logger.info(f"Admin login successful: {email}")
            return (
                dbc.Alert("Welcome Admin! Redirecting...", color="success"),
                "/admin/analytics",
                {'authenticated': True, 'user_type': 'admin'},
                "Sign In to Dashboard",
                False
            )
        else:
            return dbc.Alert("Login failed. Please try again.", color="danger"), dash.no_update, {}, "Sign In to Dashboard", False
    
    # Try CSO login
    cso_success, cso_result = verify_cso_credentials(email, password)
    if cso_success:
        if create_session(cso_result, 'cso'):
            redirect_url = get_redirect_url('cso', cso_result['function_role'])
            logger.info(f"CSO login successful: {email} -> {redirect_url}")
            return (
                dbc.Alert(f"Welcome {cso_result['cso_name']}! Redirecting...", color="success"),
                redirect_url,
                {'authenticated': True, 'user_type': 'cso'},
                "Sign In to Dashboard",
                False
            )
        else:
            return dbc.Alert("Login failed. Please try again.", color="danger"), dash.no_update, {}, "Sign In to Dashboard", False
    
    # Try regular user login
    user_success, user_result = verify_user_credentials(email, password)
    if user_success:
        if create_session(user_result, 'user'):
            redirect_url = get_redirect_url('user', next_url=next_url)
            logger.info(f"User login successful: {email} -> {redirect_url}")
            return (
                dbc.Alert("Sign in successful! Redirecting...", color="success"),
                redirect_url,
                {'authenticated': True, 'user_type': 'user'},
                "Sign In to Dashboard",
                False
            )
        else:
            return dbc.Alert("Login failed. Please try again.", color="danger"), dash.no_update, {}, "Sign In to Dashboard", False
    else:
        # Handle special error cases for users
        if isinstance(user_result, dict) and 'error' in user_result:
            if user_result['error'] == 'account_pending':
                return (
                    dbc.Alert([
                        html.Strong("Account Pending: "),
                        user_result['message'],
                        html.Br(),
                        html.A("Go to Account Activation", href="/activate_account", className="alert-link")
                    ], color="warning"),
                    dash.no_update, {}, "Sign In to Dashboard", False
                )
            elif user_result['error'] == 'account_not_verified':
                return (
                    dbc.Alert([
                        html.Strong("Account Not Verified: "),
                        user_result['message'],
                        html.Br(),
                        html.A("Go to Account Activation", href="/activate_account", className="alert-link")
                    ], color="warning"),
                    dash.no_update, {}, "Sign In to Dashboard", False
                )
    
    # If all login attempts failed
    logger.warning(f"All login attempts failed for email: {email}")
    return (
        dbc.Alert("Invalid email or password", color="danger"),
        dash.no_update, {}, "Sign In to Dashboard", False
    )

# Session validation function for other parts of the app
def is_authenticated():
    """Check if current session is authenticated."""
    return session.get('authenticated', False)

def get_current_user():
    """Get current user data from session."""
    if not is_authenticated():
        return None
    
    user_type = session.get('user_type')
    if user_type == 'admin':
        return {
            'type': 'admin',
            'email': session.get('email'),
            'is_admin': True
        }
    elif user_type == 'cso':
        return {
            'type': 'cso',
            'cso_id': session.get('cso_id'),
            'cso_name': session.get('cso_name'),
            'email': session.get('email'),
            'function_role': session.get('function_role'),
            'function_name': session.get('function_name')
        }
    elif user_type == 'user':
        return {
            'type': 'user',
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'status': session.get('status')
        }
    return None

def logout_user():
    """Clear user session."""
    session.clear()
    logger.info("User logged out - session cleared")

