import dash
from dash import Dash, dcc, html, Input, Output, callback, State, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from server import server
import hashlib
import secrets
from urllib.parse import parse_qs, urlparse

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here
    'database': 'warehouse_db'
}

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/user_dashboard/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
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
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .main-container {
                display: flex;
                min-height: 100vh;
                background: #f8fafc;
            }
            
            .sidebar {
                width: 280px;
                background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
                box-shadow: 4px 0 20px rgba(0,0,0,0.1);
                position: fixed;
                height: 100vh;
                overflow-y: auto;
                z-index: 1000;
                transition: all 0.3s ease;
            }
            
            .sidebar-header {
                padding: 2rem 1.5rem;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                color: white;
                font-size: 1.5rem;
                font-weight: 700;
                text-decoration: none;
            }
            
            .logo i {
                color: #3b82f6;
                font-size: 1.8rem;
            }
            
            .sidebar-menu {
                padding: 1.5rem 0;
            }
            
            .menu-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem 1.5rem;
                color: rgba(255,255,255,0.8);
                text-decoration: none;
                border-radius: 0;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }
            
            .menu-item:hover {
                background: rgba(255,255,255,0.1);
                color: white;
                border-left-color: #3b82f6;
            }
            
            .menu-item.active {
                background: rgba(59,130,246,0.2);
                color: #3b82f6;
                border-left-color: #3b82f6;
            }
            
            .menu-item i {
                width: 20px;
                text-align: center;
            }
            
            .main-content {
                flex: 1;
                margin-left: 280px;
                background: #f8fafc;
                min-height: 100vh;
            }
            
            .header {
                background: white;
                padding: 1.5rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-bottom: 1px solid #e2e8f0;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .header-title {
                font-size: 1.8rem;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }
            
            .header-actions {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .notification-btn {
                position: relative;
                background: #f1f5f9;
                border: none;
                padding: 0.75rem;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                color: #64748b;
            }
            
            .notification-btn:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
            
            .notification-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ef4444;
                color: white;
                font-size: 0.7rem;
                padding: 2px 6px;
                border-radius: 10px;
                min-width: 18px;
                text-align: center;
            }
            
            .user-profile {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem 1rem;
                background: #f8fafc;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .user-profile:hover {
                background: #e2e8f0;
            }
            
            .user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
            }
            
            .user-info h4 {
                margin: 0;
                font-size: 0.9rem;
                color: #1e293b;
            }
            
            .user-info p {
                margin: 0;
                font-size: 0.8rem;
                color: #64748b;
            }
            
            .content-area {
                padding: 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .hero-banner {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                padding: 3rem 2rem;
                color: white;
                margin-bottom: 2rem;
                position: relative;
                overflow: hidden;
            }
            
            .hero-banner::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><polygon fill="rgba(255,255,255,0.1)" points="0,0 1000,300 1000,1000 0,700"/></svg>');
                background-size: cover;
            }
            
            .hero-content {
                position: relative;
                z-index: 1;
            }
            
            .hero-title {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 2rem;
            }
            
            .hero-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }
            
            .hero-stat {
                text-align: center;
                padding: 1rem;
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            
            .hero-stat-number {
                font-size: 2rem;
                font-weight: 700;
                display: block;
            }
            
            .hero-stat-label {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .stat-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--card-color);
            }
            
            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 30px rgba(0,0,0,0.15);
            }
            
            .stat-card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            }
            
            .stat-card-title {
                font-size: 0.9rem;
                color: #64748b;
                margin: 0;
                font-weight: 500;
            }
            
            .stat-card-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.2rem;
                background: var(--card-color);
            }
            
            .stat-card-value {
                font-size: 2.2rem;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }
            
            .stat-card-change {
                font-size: 0.8rem;
                margin-top: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            
            .stat-card-change.positive {
                color: #10b981;
            }
            
            .stat-card-change.negative {
                color: #ef4444;
            }
            
            .search-section {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
            }
            
            .search-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .search-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }
            
            .search-filters {
                display: grid;
                grid-template-columns: 2fr 1fr 1fr auto;
                gap: 1rem;
                align-items: end;
            }
            
            .search-input {
                position: relative;
            }
            
            .search-input input {
                width: 100%;
                padding: 0.75rem 1rem 0.75rem 2.5rem;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .search-input input:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
            }
            
            .search-input .search-icon {
                position: absolute;
                left: 0.75rem;
                top: 50%;
                transform: translateY(-50%);
                color: #64748b;
            }
            
            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .filter-label {
                font-size: 0.9rem;
                color: #64748b;
                font-weight: 500;
            }
            
            .filter-select {
                padding: 0.75rem 1rem;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 1rem;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .filter-select:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
            }
            
            .search-btn {
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .search-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 15px rgba(59,130,246,0.4);
            }
            
            .units-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .unit-card {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }
            
            .unit-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            }
            
            .unit-card-header {
                position: relative;
                height: 200px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 3rem;
                overflow: hidden;
            }
            
            .unit-card-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="20" cy="80" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="80" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
                background-size: 50px 50px;
                animation: float 20s infinite linear;
            }
            
            @keyframes float {
                0% { transform: translateX(0); }
                100% { transform: translateX(50px); }
            }
            
            .unit-status-badge {
                position: absolute;
                top: 1rem;
                right: 1rem;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                backdrop-filter: blur(10px);
            }
            
            .status-available {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .status-taken {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .status-maintenance {
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
                border: 1px solid rgba(245, 158, 11, 0.3);
            }
            
            .unit-card-body {
                padding: 1.5rem;
            }
            
            .unit-title {
                font-size: 1.3rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 0.5rem;
            }
            
            .unit-warehouse {
                color: #64748b;
                font-size: 0.9rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .unit-price {
                font-size: 1.8rem;
                font-weight: 700;
                color: #3b82f6;
                margin-bottom: 1rem;
            }
            
            .unit-price span {
                font-size: 0.9rem;
                color: #64748b;
                font-weight: 400;
            }
            
            .unit-actions {
                display: flex;
                gap: 0.75rem;
                margin-top: 1rem;
            }
            
            .btn-primary {
                flex: 1;
                padding: 0.75rem 1rem;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            
            .btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 15px rgba(59,130,246,0.4);
            }
            
            .btn-secondary {
                padding: 0.75rem;
                background: #f8fafc;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-secondary:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
            
            .quick-actions {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
            }
            
            .quick-actions-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 1.5rem;
            }
            
            .quick-actions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
            }
            
            .quick-action-card {
                padding: 1.5rem;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid #e2e8f0;
                text-decoration: none;
                color: inherit;
            }
            
            .quick-action-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                background: white;
            }
            
            .quick-action-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.2rem;
                margin-bottom: 1rem;
            }
            
            .quick-action-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 0.5rem;
            }
            
            .quick-action-desc {
                font-size: 0.9rem;
                color: #64748b;
                line-height: 1.4;
            }
            
            .loading {
                text-align: center;
                padding: 3rem;
                color: #64748b;
            }
            
            .loading i {
                font-size: 2rem;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .no-results {
                text-align: center;
                padding: 3rem;
                color: #64748b;
            }
            
            .no-results i {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: #cbd5e1;
            }
            
            .pagination {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 0.5rem;
                margin-top: 2rem;
            }
            
            .pagination button {
                padding: 0.5rem 1rem;
                border: 1px solid #e2e8f0;
                background: white;
                color: #64748b;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pagination button:hover {
                background: #f8fafc;
                color: #1e293b;
            }
            
            .pagination button.active {
                background: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
            
            .pagination button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            @media (max-width: 1024px) {
                .sidebar {
                    transform: translateX(-100%);
                }
                
                .main-content {
                    margin-left: 0;
                }
                
                .search-filters {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .hero-title {
                    font-size: 2rem;
                }
                
                .units-grid {
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                }
            }
            
            @media (max-width: 768px) {
                .content-area {
                    padding: 1rem;
                }
                
                .hero-banner {
                    padding: 2rem 1rem;
                }
                
                .hero-title {
                    font-size: 1.8rem;
                }
                
                .stats-grid {
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                }
                
                .units-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def validate_session_token(token):
    """
    Validate session token from URL parameter.
    Returns (user_dict, None) on success, or (None, error_message) on failure.
    """
    print(f"Validating session token: {token}")
    
    if not token:
        print("No token provided")
        return None, "No session token"

    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return None, "DB connection failed"

    try:
        cur = conn.cursor(dictionary=True)
        
        # Query session with token and join user data
        cur.execute("""
            SELECT s.*, u.email, u.first_name, u.last_name, u.company_name, u.user_type, u.status
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_token = %s
        """, (token,))
        
        result = cur.fetchone()
        print(f"Session query result: {result}")
        
        if not result:
            print("No session found with provided token")
            return None, "Invalid session token"
        
        # Check if session has expired
        if result['expires_at'] <= datetime.now():
            print(f"Session expired. Expires at: {result['expires_at']}, Current time: {datetime.now()}")
            # Clean up expired session
            cur.execute("DELETE FROM sessions WHERE session_token = %s", (token,))
            conn.commit()
            return None, "Session expired"
        
        # Check if user is active
        if result['status'] != 'active':
            print(f"User status is not active: {result['status']}")
            return None, "User account not active"
        
        # Update last activity
        cur.execute("""
            UPDATE sessions 
            SET last_activity = NOW() 
            WHERE session_token = %s
        """, (token,))
        conn.commit()
        
        # Return user data
        user_data = {
            'id': result['user_id'],
            'email': result['email'],
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'company_name': result['company_name'],
            'user_type': result['user_type'],
            'status': result['status'],
            'session_token': token
        }
        
        print(f"Session validation successful for user: {user_data['email']}")
        return user_data, None

    except mysql.connector.Error as err:
        print(f"Database error during session validation: {err}")
        return None, f"Database error: {err}"
    except Exception as e:
        print(f"Unexpected error during session validation: {e}")
        return None, f"Validation error: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def extract_token_from_url(pathname, search):
    """Extract token from URL parameters"""
    try:
        # Handle both query string formats
        if search:
            # Remove leading '?' if present
            query_string = search.lstrip('?')
            parsed = parse_qs(query_string)
            token = parsed.get('token', [None])[0]
            print(f"Token extracted from search: {token}")
            return token
        
        # Also check if token is embedded in pathname (fallback)
        if '?token=' in pathname:
            token = pathname.split('?token=')[1].split('&')[0]
            print(f"Token extracted from pathname: {token}")
            return token
            
        return None
    except Exception as e:
        print(f"Error extracting token: {e}")
        return None

def get_user_display_name(user_data):
    """Get display name for user"""
    if user_data['user_type'] == 'corporate' and user_data['company_name']:
        return user_data['company_name']
    else:
        first_name = user_data['first_name'] or ""
        last_name = user_data['last_name'] or ""
        return f"{first_name} {last_name}".strip() or user_data['email'].split('@')[0]

def get_user_initials(user_data):
    """Get user initials for avatar"""
    if user_data['user_type'] == 'corporate' and user_data['company_name']:
        # For corporate, use first letters of company name words
        words = user_data['company_name'].split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        else:
            return user_data['company_name'][:2].upper()
    else:
        # For individual, use first and last name initials
        first_name = user_data['first_name'] or ""
        last_name = user_data['last_name'] or ""
        
        if first_name and last_name:
            return f"{first_name[0]}{last_name[0]}".upper()
        elif first_name:
            return first_name[:2].upper()
        else:
            # Fallback to email
            email_part = user_data['email'].split('@')[0]
            return email_part[:2].upper()

def get_dashboard_stats():
    """Get dashboard statistics"""
    connection = get_db_connection()
    if not connection:
        return {
            'total_warehouses': 0,
            'available_units': 0,
            'total_bookings': 0,
            'active_bookings': 0
        }
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get total warehouses
        cursor.execute("SELECT COUNT(*) as count FROM warehouses WHERE status = 'active'")
        result = cursor.fetchone()
        total_warehouses = result['count'] if result else 0
        
        # Get available units
        cursor.execute("SELECT COUNT(*) as count FROM units WHERE status = 'active' AND availability = 'not taken'")
        result = cursor.fetchone()
        available_units = result['count'] if result else 0
        
        # Get total bookings (assuming bookings table exists)
        try:
            cursor.execute("SELECT COUNT(*) as count FROM bookings")
            result = cursor.fetchone()
            total_bookings = result['count'] if result else 0
        except:
            total_bookings = 0
        
        # Get active bookings (assuming bookings table exists)
        try:
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status IN ('pending', 'confirmed')")
            result = cursor.fetchone()
            active_bookings = result['count'] if result else 0
        except:
            active_bookings = 0
        
        return {
            'total_warehouses': total_warehouses,
            'available_units': available_units,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings
        }
    
    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
        return {
            'total_warehouses': 0,
            'available_units': 0,
            'total_bookings': 0,
            'active_bookings': 0
        }
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def clear_user_session(session_token):
    """Clear user session (for logout)"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        # Delete the specific session
        cursor.execute("DELETE FROM sessions WHERE session_token = %s", (session_token,))
        connection.commit()
        print(f"Session cleared for token: {session_token}")
        return True
    except mysql.connector.Error as err:
        print(f"Error clearing session: {err}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# App layout with session management
app.layout = html.Div([
    dcc.Store(id='validated-user-data', storage_type='memory'),
    dcc.Store(id='session-token-store', storage_type='memory'),
    dcc.Store(id='session-check-trigger', storage_type='memory', data={'check': 0}),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='session-check-interval', interval=30000, n_intervals=0),  # Check every 30 seconds
    
    html.Div(id='dashboard-content')
])

# Main callback to extract token and validate session
@app.callback(
    [Output('validated-user-data', 'data'),
     Output('session-token-store', 'data'),
     Output('dashboard-content', 'children')],
    [Input('url', 'pathname'),
     Input('url', 'search'),
     Input('session-check-trigger', 'data')]
)
def handle_authentication_and_display(pathname, search, check_trigger):
    """Extract token, validate session, and display content"""
    print(f"URL callback - Pathname: {pathname}, Search: {search}")
    
    # Extract token from URL
    token = extract_token_from_url(pathname, search)
    
    if not token:
        print("No token found in URL")
        return None, None, html.Div([
            dcc.Location(id='redirect-to-login', refresh=True, pathname='/login'),
            html.Div([
                html.H2("Session Required"),
                html.P("Please log in to access this page."),
                html.A("Go to Login", href="/login", className="btn btn-primary")
            ], style={
                'padding': '40px',
                'textAlign': 'center',
                'maxWidth': '400px',
                'margin': '100px auto',
                'border': '1px solid #ddd',
                'borderRadius': '8px'
            })
        ])
    
    # Validate token
    user_data, error = validate_session_token(token)
    
    if error or not user_data:
        print(f"Session validation failed: {error}")
        return None, None, html.Div([
            dcc.Location(id='redirect-to-login', refresh=True, pathname='/login'),
            html.Div([
                html.H2("Session Invalid"),
                html.P(f"Your session has expired or is invalid. Please log in again."),
                html.A("Go to Login", href="/login", className="btn btn-primary")
            ], style={
                'padding': '40px',
                'textAlign': 'center',
                'maxWidth': '400px',
                'margin': '100px auto',
                'border': '1px solid #ddd',
                'borderRadius': '8px'
            })
        ])
    
    print(f"Session validation successful, displaying dashboard for: {user_data['email']}")
    
    # Return the main dashboard layout
    dashboard_layout = html.Div([
        # Welcome Header
        html.Div([
            html.H1(f"Welcome, {get_user_display_name(user_data)}!", 
                   style={'color': '#1f2937', 'marginBottom': '10px'}),
            html.P(f"User ID: {user_data['id']} | Role: {user_data['user_type'].title()} | Status: {user_data['status'].title()}", 
                   style={'color': '#6b7280', 'fontSize': '14px'}),
        ], style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'padding': '30px',
            'borderRadius': '10px',
            'marginBottom': '30px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }),
        
        # User Profile Card
        html.Div([
            html.Div([
                html.Div(get_user_initials(user_data), style={
                    'width': '60px',
                    'height': '60px',
                    'borderRadius': '50%',
                    'backgroundColor': '#4f46e5',
                    'color': 'white',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'marginRight': '20px'
                }),
                html.Div([
                    html.H3(get_user_display_name(user_data), style={'margin': '0', 'color': '#1f2937'}),
                    html.P(user_data['email'], style={'margin': '5px 0', 'color': '#6b7280'}),
                    html.Span(
                        f"{'Corporate' if user_data['user_type'] == 'corporate' else 'Individual'} Account",
                        style={
                            'backgroundColor': '#10b981' if user_data['user_type'] == 'corporate' else '#3b82f6',
                            'color': 'white',
                            'padding': '4px 12px',
                            'borderRadius': '20px',
                            'fontSize': '12px',
                            'fontWeight': '500'
                        }
                    )
                ])
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Button([
                html.I(className="fas fa-sign-out-alt", style={'marginRight': '8px'}),
                "Logout"
            ], id="logout-btn", style={
                'backgroundColor': '#ef4444',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'fontSize': '14px',
                'fontWeight': '500'
            })
        ], style={
            'backgroundColor': 'white',
            'padding': '25px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'marginBottom': '30px',
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center'
        }),
        
        # Dashboard Stats
        html.Div([
            html.H2("Dashboard Overview", style={'color': '#1f2937', 'marginBottom': '20px'}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-warehouse", style={'fontSize': '24px', 'color': '#3b82f6', 'marginBottom': '10px'}),
                    html.H3(id="stat-total-warehouses", style={'margin': '0', 'color': '#1f2937', 'fontSize': '32px'}),
                    html.P("Total Warehouses", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'borderLeft': '4px solid #3b82f6'
                }),
                
                html.Div([
                    html.I(className="fas fa-box-open", style={'fontSize': '24px', 'color': '#10b981', 'marginBottom': '10px'}),
                    html.H3(id="stat-available-units", style={'margin': '0', 'color': '#1f2937', 'fontSize': '32px'}),
                    html.P("Available Units", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'borderLeft': '4px solid #10b981'
                }),
                
                html.Div([
                    html.I(className="fas fa-calendar-check", style={'fontSize': '24px', 'color': '#f59e0b', 'marginBottom': '10px'}),
                    html.H3(id="stat-total-bookings", style={'margin': '0', 'color': '#1f2937', 'fontSize': '32px'}),
                    html.P("Total Bookings", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'borderLeft': '4px solid #f59e0b'
                }),
                
                html.Div([
                    html.I(className="fas fa-clock", style={'fontSize': '24px', 'color': '#8b5cf6', 'marginBottom': '10px'}),
                    html.H3(id="stat-active-bookings", style={'margin': '0', 'color': '#1f2937', 'fontSize': '32px'}),
                    html.P("Active Bookings", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'borderLeft': '4px solid #8b5cf6'
                })
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '20px'
            })
        ], style={'marginBottom': '30px'}),
        
        # Quick Actions
        html.Div([
            html.H2("Quick Actions", style={'color': '#1f2937', 'marginBottom': '20px'}),
            html.Div([
                html.A([
                    html.I(className="fas fa-search", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Browse Units", style={'margin': '0', 'color': '#1f2937'}),
                    html.P("Find and book storage units", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], href=f"/browse?token={token}", style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'textDecoration': 'none',
                    'color': 'inherit',
                    'transition': 'all 0.3s ease',
                    'border': '2px solid transparent'
                }),
                
                html.A([
                    html.I(className="fas fa-box", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("My Bookings", style={'margin': '0', 'color': '#1f2937'}),
                    html.P("View your storage bookings", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], href=f"/bookings?token={token}", style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'textDecoration': 'none',
                    'color': 'inherit',
                    'transition': 'all 0.3s ease',
                    'border': '2px solid transparent'
                }),
                
                html.A([
                    html.I(className="fas fa-headset", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Support", style={'margin': '0', 'color': '#1f2937'}),
                    html.P("Get help and support", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], href=f"/support?token={token}", style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'textDecoration': 'none',
                    'color': 'inherit',
                    'transition': 'all 0.3s ease',
                    'border': '2px solid transparent'
                }),
                
                html.A([
                    html.I(className="fas fa-user-cog", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Settings", style={'margin': '0', 'color': '#1f2937'}),
                    html.P("Manage your account", style={'margin': '5px 0', 'color': '#6b7280', 'fontSize': '14px'})
                ], href=f"/settings?token={token}", style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'textAlign': 'center',
                    'textDecoration': 'none',
                    'color': 'inherit',
                    'transition': 'all 0.3s ease',
                    'border': '2px solid transparent'
                })
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '20px'
            })
        ])
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '20px',
        'backgroundColor': '#f9fafb',
        'minHeight': '100vh'
    })
    
    return user_data, token, dashboard_layout

# Session check callback
@app.callback(
    Output('session-check-trigger', 'data'),
    [Input('session-check-interval', 'n_intervals')],
    [State('session-token-store', 'data')]
)
def check_session_periodically(n_intervals, token):
    """Periodically check if session is still valid"""
    if n_intervals == 0 or not token:  # Skip initial call or if no token
        raise PreventUpdate
    
    user_data, error = validate_session_token(token)
    if error or not user_data:
        # Session is invalid, trigger page refresh
        return {'check': n_intervals, 'invalid': True}
    
    return {'check': n_intervals, 'valid': True}

# Logout callback
@app.callback(
    Output('url', 'pathname'),
    [Input('logout-btn', 'n_clicks')],
    [State('session-token-store', 'data')],
    prevent_initial_call=True
)
def logout_user(n_clicks, token):
    """Handle user logout"""
    if n_clicks and token:
        clear_user_session(token)
        return '/login'
    raise PreventUpdate

# Dashboard stats callback
@app.callback(
    [Output('stat-total-warehouses', 'children'),
     Output('stat-available-units', 'children'),
     Output('stat-total-bookings', 'children'),
     Output('stat-active-bookings', 'children')],
    [Input('validated-user-data', 'data')]
)
def update_dashboard_stats(user_data):
    """Update dashboard statistics"""
    if not user_data:
        raise PreventUpdate
    
    stats = get_dashboard_stats()
    
    return (
        str(stats['total_warehouses']),
        str(stats['available_units']),
        str(stats['total_bookings']),
        str(stats['active_bookings'])
    )

# if __name__ == '__main__':
#     app.run_server(debug=True)