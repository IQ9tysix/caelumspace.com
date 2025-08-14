import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json
import hashlib
import uuid
from server import server
import secrets
from flask import session, request


# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'warehouse_db',
    'user': 'root',
    'password': ''  # Update with your MySQL password
}

# Initialize the Dash app
app = Dash(
    __name__,
    server=server,
    url_base_pathname="/admin/payments/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)

app.title = "CaelumSpaces - Payment Management"

# Custom CSS and HTML template
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
         /* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #f8fafc;
    color: #334155;
    line-height: 1.6;
    overflow-x: hidden;
}

/* Dashboard Container */
.dashboard-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header Styles */
.dashboard-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    height: 70px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    height: 100%;
    max-width: 100%;
}

.dashboard-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #fbbf24;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    letter-spacing: -0.025em;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.user-info, .last-updated {
    font-size: 0.875rem;
    color: #e2e8f0;
    font-weight: 500;
}

.user-info {
    padding: 0.5rem 1rem;
    background: rgba(251, 191, 36, 0.1);
    border-radius: 6px;
    border: 1px solid rgba(251, 191, 36, 0.2);
}

/* Dashboard Body */
.dashboard-body {
    display: flex;
    margin-top: 70px;
    min-height: calc(100vh - 70px);
}

/* Sidebar Styles */
.sidebar {
    width: 280px;
    background: white;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
    position: fixed;
    left: 0;
    top: 70px;
    bottom: 0;
    overflow-y: auto;
    z-index: 900;
    border-right: 1px solid #e2e8f0;
}

.sidebar-content {
    padding: 2rem 0;
}

.sidebar-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0 1.5rem;
    margin-bottom: 1.5rem;
}

.nav-menu {
    list-style: none;
}

.nav-menu li {
    margin: 0;
}

.nav-link {
    display: flex;
    align-items: center;
    padding: 1rem 1.5rem;
    color: #64748b;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.925rem;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
    position: relative;
}

.nav-link:hover {
    background: linear-gradient(90deg, rgba(251, 191, 36, 0.08) 0%, rgba(251, 191, 36, 0.02) 100%);
    color: #1e293b;
    border-left-color: #fbbf24;
    transform: translateX(2px);
}

.nav-link.active {
    background: linear-gradient(90deg, rgba(251, 191, 36, 0.12) 0%, rgba(251, 191, 36, 0.04) 100%);
    color: #1e293b;
    border-left-color: #fbbf24;
    font-weight: 600;
}

.nav-link.active::after {
    content: '';
    position: absolute;
    right: 1.5rem;
    width: 6px;
    height: 6px;
    background: #fbbf24;
    border-radius: 50%;
}

.logout-link {
    margin-top: 2rem !important;
    border-top: 1px solid #e2e8f0 !important;
    padding-top: 1.5rem !important;
    color: #ef4444 !important;
}

.logout-link:hover {
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.02) 100%);
    border-left-color: #ef4444;
    color: #dc2626 !important;
}

/* Main Content */
.main-content {
    flex: 1;
    margin-left: 280px;
    padding: 2rem;
    background: #f8fafc;
    min-height: calc(100vh - 140px);
}

/* Metrics Section */
.metrics-section {
    margin-bottom: 3rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    position: relative;
    padding-bottom: 0.5rem;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
    border-radius: 2px;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border-color: #fbbf24;
}

.kpi-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

/* KPI Content */
.kpi-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.5rem;
    line-height: 1;
}

.kpi-label {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
}

/* Specialized KPI Card Styles */
.warehouse-card .kpi-icon { color: #3b82f6; }
.warehouse-card::before { background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); }

.units-card .kpi-icon { color: #8b5cf6; }
.units-card::before { background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%); }

.occupied-card .kpi-icon { color: #10b981; }
.occupied-card::before { background: linear-gradient(90deg, #10b981 0%, #059669 100%); }

.occupancy-card .kpi-icon { color: #f59e0b; }
.occupancy-card::before { background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); }

.revenue-card .kpi-icon { color: #ef4444; }
.revenue-card::before { background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); }

/* Charts Section */
.charts-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.chart-container {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
    overflow: hidden;
    transition: all 0.3s ease;
}

.chart-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.chart-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: #1e293b;
    padding: 1.5rem 1.5rem 0;
    margin-bottom: 1rem;
    position: relative;
}

.chart-wrapper {
    padding: 0 1.5rem 1.5rem;
}

/* Footer */
.dashboard-footer {
    background: white;
    border-top: 1px solid #e2e8f0;
    padding: 1.5rem 2rem;
    margin-left: 280px;
    margin-top: auto;
}

.footer-text {
    color: #64748b;
    font-size: 0.875rem;
    text-align: center;
    margin: 0;
}

/* Loading States */
.loading-message {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: #64748b;
    font-size: 1.125rem;
    background: white;
    border-radius: 16px;
    border: 2px dashed #e2e8f0;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .charts-row {
        grid-template-columns: 1fr;
    }
    
    .kpi-container {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }
}

@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
    
    .main-content {
        margin-left: 0;
        padding: 1rem;
    }
    
    .dashboard-footer {
        margin-left: 0;
    }
    
    .header-content {
        padding: 0 1rem;
    }
    
    .dashboard-title {
        font-size: 1.5rem;
    }
    
    .header-right {
        gap: 1rem;
    }
    
    .user-info, .last-updated {
        display: none;
    }
    
    .kpi-container {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }
    
    .kpi-card {
        padding: 1.5rem;
    }
    
    .kpi-value {
        font-size: 1.875rem;
    }
    
    .charts-row {
        gap: 1rem;
    }
    
    .section-title {
        font-size: 1.25rem;
    }
}

@media (max-width: 480px) {
    .kpi-container {
        grid-template-columns: 1fr;
    }
    
    .main-content {
        padding: 0.75rem;
    }
    
    .kpi-card {
        padding: 1.25rem;
    }
    
    .chart-title {
        font-size: 1rem;
        padding: 1rem 1rem 0;
    }
    
    .chart-wrapper {
        padding: 0 1rem 1rem;
    }
}

/* Mobile Menu Toggle (for future implementation) */
.mobile-menu-toggle {
    display: none;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
}

@media (max-width: 768px) {
    .mobile-menu-toggle {
        display: block;
    }
}

/* Custom Scrollbar */
.sidebar::-webkit-scrollbar {
    width: 6px;
}

.sidebar::-webkit-scrollbar-track {
    background: #f1f5f9;
}

.sidebar::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* Animation Classes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.kpi-card, .chart-container {
    animation: fadeInUp 0.6s ease-out;
}

.kpi-card:nth-child(1) { animation-delay: 0.1s; }
.kpi-card:nth-child(2) { animation-delay: 0.2s; }
.kpi-card:nth-child(3) { animation-delay: 0.3s; }
.kpi-card:nth-child(4) { animation-delay: 0.4s; }
.kpi-card:nth-child(5) { animation-delay: 0.5s; }

/* Focus States for Accessibility */
.nav-link:focus {
    outline: 2px solid #fbbf24;
    outline-offset: 2px;
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
    .kpi-card {
        border-width: 2px;
    }
    
    .nav-link.active {
        background: #fbbf24;
        color: #1e293b;
    }
}

/* Print Styles */
@media print {
    .sidebar, .dashboard-header, .dashboard-footer {
        display: none;
    }
    
    .main-content {
        margin-left: 0;
        padding: 0;
    }
    
    .chart-container {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #000;
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
# CONSOLIDATED AUTHENTICATION SYSTEM
class AuthManager:
    """Centralized authentication and authorization manager"""
    
    @staticmethod
    def get_current_user():
        """Get current user from session with all required information"""
        if 'user_id' not in session or 'user_type' not in session:
            return None
            
        return {
            'id': session.get('user_id'),
            'type': session.get('user_type'),
            'email': session.get('user_email'),
            'name': session.get('user_name'),
            'cso_name': session.get('cso_name'),
            'function_name': session.get('function_name'),
            'function_role': session.get('function_role')
        }
    
    @staticmethod
    def has_payments_access():
        """Check if current user has access to payments - consolidated logic"""
        current_user = AuthManager.get_current_user()
        
        if not current_user:
            return False, "not_logged_in"
        
        # Admin users have full access
        if current_user['type'] == 'admin':
            return True, "admin"
        
        # CSO users need specific function role
        if current_user['type'] == 'cso':
            if current_user.get('function_role') == 'access_payments':
                return True, "cso_authorized"
            else:
                return False, "cso_unauthorized"
        
        return False, "unknown_user_type"
    
    @staticmethod
    def get_user_display_name():
        """Get display name for current user"""
        current_user = AuthManager.get_current_user()
        if not current_user:
            return "Unknown User"
        
        if current_user['type'] == 'admin':
            return f"Admin: {current_user['email']}"
        elif current_user['type'] == 'cso':
            return f"{current_user['cso_name']} - {current_user['function_name']}"
        else:
            return current_user['email']
    
    @staticmethod
    def get_access_denied_message():
        """Get appropriate access denied message based on user type"""
        current_user = AuthManager.get_current_user()
        
        if not current_user:
            return "Please log in to access this page."
        
        if current_user['type'] == 'cso':
            return f"Access denied. Your function '{current_user['function_name']}' does not include payment management permissions."
        
        return "You do not have permission to access the Payment Management page."


class DatabaseManager:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Query execution error: {e}")
            return []
    
    def execute_procedure(self, procedure_name, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc(procedure_name, params)
            result = []
            for res in cursor.stored_results():
                result.extend(res.fetchall())
            cursor.close()
            return result
        except Error as e:
            print(f"Procedure execution error: {e}")
            return []


# Initialize database manager
db_manager = DatabaseManager()


def get_payment_data():
    """Fetch comprehensive payment data"""
    query = """
    SELECT 
        b.id as booking_id,
        b.customer_name,
        b.customer_email,
        b.customer_phone,
        u.name as unit_name,
        w.name as warehouse_name,
        b.start_date,
        b.end_date,
        b.total_amount,
        b.status as booking_status,
        b.payment_status,
        b.created_at,
        b.updated_at,
        DATEDIFF(b.end_date, CURDATE()) as days_until_end,
        DATEDIFF(b.end_date, b.start_date) as total_duration,
        DATEDIFF(CURDATE(), b.start_date) as days_elapsed,
        COALESCE(SUM(p.amount), 0) as total_paid,
        (b.total_amount - COALESCE(SUM(p.amount), 0)) as balance_due
    FROM bookings b
    JOIN units u ON b.unit_id = u.id
    JOIN warehouses w ON u.warehouse_id = w.id
    LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
    WHERE b.status != 'cancelled'
    GROUP BY b.id
    ORDER BY b.created_at DESC
    """
    
    try:
        data = db_manager.execute_query(query)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching payment data: {e}")
        return pd.DataFrame()


def create_authorized_layout():
    """Create the main layout for authorized users"""
    return html.Div([
        # Header
        html.Header([
            html.Div([
                html.H1("CaelumSpaces", className="dashboard-title"),
                html.Div([
                    html.Span(f"Welcome {AuthManager.get_user_display_name()}", 
                             className="user-info"),
                    html.Span(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                             className="last-updated")
                ], className="header-right")
            ], className="header-content")
        ], className="dashboard-header"),
        
        # Main Content
        html.Div([
            # Sidebar
            html.Div([
                html.Div([
                    html.H3("Navigation", className="sidebar-title"),
                    html.Ul([
                        html.Li([html.A("📊 Analytics", href="/admin/analytics/", 
                                       className="nav-link", id="analytics-link")]),
                        html.Li([html.A("📦 Warehouses", href="/admin/units_creation", 
                                       className="nav-link", id="warehouses-link")]),
                        html.Li([html.A("📋 Bookings", href="/bookings", 
                                       className="nav-link", id="bookings-link")]),
                        html.Li([html.A("💰 Payments", href="/admin/payments/", 
                                       className="nav-link active")]),
                        html.Li([html.A("📈 Reports", href="/reports", 
                                       className="nav-link", id="reports-link")]),
                        html.Li([html.A("⚙️ Settings", href="/settings", 
                                       className="nav-link", id="settings-link")]),
                        html.Li([
                            html.A("🚪 Logout", href="/logout", className="nav-link logout-link", 
                                  style={"color": "#f5576c", "border-top": "1px solid #eee", 
                                        "margin-top": "20px", "padding-top": "15px"})
                        ])
                    ], className="nav-menu")
                ], className="sidebar-content")
            ], className="sidebar"),
            
            # Main content area
            html.Div([
                html.Div([
                    # Page Title
                    html.Div([
                        html.H2("💳 Payment Management Dashboard", className="page-title"),
                        html.P("Monitor and manage payment status across all bookings", className="page-subtitle")
                    ], className="page-header"),
                    
                    # Auto-refresh interval
                    dcc.Interval(
                        id='interval-component',
                        interval=30*1000,  # Update every 30 seconds
                        n_intervals=0
                    ),
                    
                    # KPI Cards
                    html.Div(id='kpi-cards'),
                    
                    # Charts Row
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div(id='payment-status-chart')
                                ], className="card-body")
                            ], className="card")
                        ], className="col-md-6"),
                        
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div(id='expiry-alert-chart')
                                ], className="card-body")
                            ], className="card")
                        ], className="col-md-6"),
                    ], className="row mb-4"),
                    
                    # Revenue Trend
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div(id='revenue-trend-chart')
                                ], className="card-body")
                            ], className="card")
                        ], className="col-12"),
                    ], className="row mb-4"),
                    
                    # Payments Table
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H5("📊 Payment Records", className="card-title"),
                                    html.P("Real-time payment tracking and management", className="card-text text-muted")
                                ], className="card-header"),
                                html.Div([
                                    html.Div(id='payments-table-container')
                                ], className="card-body")
                            ], className="card")
                        ], className="col-12"),
                    ], className="row mb-4"),
                    
                ], className="main-content dashboard-body")
            ], className="content-area"),
        ], className="dashboard-container"),
        
        # Footer
        html.Footer([
            html.P("© 2025 CaelumSpaces Warehouse Management System. All rights reserved.", 
                   className="footer-text")
        ], className="dashboard-footer"),
        
        # Navigation modal for CSO users
        html.Div(id='navigation-modal')
    ])


def create_access_denied_layout(reason):
    """Create access denied layout based on specific reason"""
    current_user = AuthManager.get_current_user()
    
    if reason == "not_logged_in":
        return html.Div([
            html.Div([
                html.H1("Please Log In", style={"color": "#667eea", "text-align": "center", "margin-top": "100px"}),
                html.P("You need to be logged in to access the Payment Management page.", 
                       style={"text-align": "center", "margin": "20px", "font-size": "18px"}),
                html.Div([
                    html.A("Login", href="/login", className="btn btn-primary", 
                           style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                                  "background-color": "#667eea", "color": "white", "border-radius": "5px"})
                ], style={"text-align": "center", "margin-top": "30px"})
            ])
        ])
    
    # For unauthorized users (CSO without proper role or other cases)
    user_info = AuthManager.get_user_display_name()
    access_message = AuthManager.get_access_denied_message()
    
    return html.Div([
        html.Div([
            html.H1("Access Denied", style={"color": "#f5576c", "text-align": "center", "margin-top": "100px"}),
            html.P(access_message, 
                   style={"text-align": "center", "margin": "20px", "font-size": "18px"}),
            html.P(f"Current User: {user_info}", 
                   style={"text-align": "center", "margin": "10px", "font-size": "14px", "color": "#666"}),
            html.P("Only administrators and CSO officers with 'access_payments' function can view this page.", 
                   style={"text-align": "center", "margin": "20px", "font-size": "16px", "color": "#888"}),
            html.Div([
                html.A("Go to Dashboard", href="/", className="btn btn-primary", 
                       style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                              "background-color": "#667eea", "color": "white", "border-radius": "5px"}),
                html.A("Go to Login", href="/login", className="btn btn-secondary",
                       style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                              "background-color": "#6c757d", "color": "white", "border-radius": "5px"})
            ], style={"text-align": "center", "margin-top": "30px"})
        ])
    ])


def create_kpi_cards(df):
    """Create KPI summary cards"""
    if df.empty:
        return html.Div("No data available", className="text-muted")
    
    total_bookings = len(df)
    total_revenue = df['total_amount'].sum()
    paid_revenue = df[df['payment_status'] == 'paid']['total_amount'].sum()
    pending_revenue = df[df['payment_status'] == 'pending']['total_amount'].sum()
    
    # Calculate expiring soon (within 7 days)
    expiring_soon = len(df[df['days_until_end'].between(0, 7)])
    
    # Calculate overdue payments
    overdue_payments = len(df[(df['days_until_end'] < 0) & (df['payment_status'] != 'paid')])
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"₦{total_revenue:,.2f}", className="kpi-value text-primary"),
                    html.P("Total Revenue", className="kpi-label"),
                    html.Small(f"From {total_bookings} bookings", className="kpi-detail")
                ], className="card-body text-center")
            ], className="card kpi-card")
        ], className="col-md-2 col-sm-6 mb-3"),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"₦{paid_revenue:,.2f}", className="kpi-value text-success"),
                    html.P("Paid Revenue", className="kpi-label"),
                    html.Small(f"{(paid_revenue/total_revenue*100):.1f}% collected" if total_revenue > 0 else "0% collected", 
                              className="kpi-detail text-success")
                ], className="card-body text-center")
            ], className="card kpi-card")
        ], className="col-md-2 col-sm-6 mb-3"),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"₦{pending_revenue:,.2f}", className="kpi-value text-warning"),
                    html.P("Pending Revenue", className="kpi-label"),
                    html.Small(f"{(pending_revenue/total_revenue*100):.1f}% pending" if total_revenue > 0 else "0% pending", 
                              className="kpi-detail text-warning")
                ], className="card-body text-center")
            ], className="card kpi-card")
        ], className="col-md-2 col-sm-6 mb-3"),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"{expiring_soon}", className="kpi-value text-info"),
                    html.P("Expiring Soon", className="kpi-label"),
                    html.Small("Within 7 days", className="kpi-detail text-info")
                ], className="card-body text-center")
            ], className="card kpi-card")
        ], className="col-md-2 col-sm-6 mb-3"),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"{overdue_payments}", className="kpi-value text-danger"),
                    html.P("Overdue Payments", className="kpi-label"),
                    html.Small("Requires attention", className="kpi-detail text-danger")
                ], className="card-body text-center")
            ], className="card kpi-card")
        ], className="col-md-2 col-sm-6 mb-3"),
    ], className="row mb-4")


def create_payment_status_chart(df):
    """Create payment status visualization"""
    if df.empty:
        return dcc.Graph(figure=go.Figure())
    
    # Payment status distribution
    payment_counts = df['payment_status'].value_counts()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=payment_counts.index,
            values=payment_counts.values,
            hole=0.4,
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444', '#6b7280'])
        )
    ])
    
    fig.update_layout(
        title="Payment Status Distribution",
        showlegend=True,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return dcc.Graph(figure=fig)


def create_revenue_trend_chart(df):
    """Create revenue trend visualization"""
    if df.empty:
        return dcc.Graph(figure=go.Figure())
    
    # Group by month
    df['month'] = pd.to_datetime(df['start_date']).dt.to_period('M')
    monthly_revenue = df.groupby('month').agg({
        'total_amount': 'sum',
        'booking_id': 'count'
    }).reset_index()
    
    monthly_revenue['month'] = monthly_revenue['month'].astype(str)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Revenue', 'Monthly Bookings'),
        vertical_spacing=0.1
    )
    
    # Revenue trend
    fig.add_trace(
        go.Scatter(
            x=monthly_revenue['month'],
            y=monthly_revenue['total_amount'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Bookings trend
    fig.add_trace(
        go.Bar(
            x=monthly_revenue['month'],
            y=monthly_revenue['booking_id'],
            name='Bookings',
            marker=dict(color='#10b981')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        title_text="Revenue & Booking Trends"
    )
    
    return dcc.Graph(figure=fig)


def create_expiry_alert_chart(df):
    """Create expiry alert visualization"""
    if df.empty:
        return dcc.Graph(figure=go.Figure())
    
    # Categorize by expiry status
    def get_expiry_category(days):
        if days < 0:
            return "Expired"
        elif days <= 7:
            return "Expiring Soon (≤7 days)"
        elif days <= 30:
            return "Expiring This Month"
        else:
            return "Long Term"
    
    df['expiry_category'] = df['days_until_end'].apply(get_expiry_category)
    expiry_counts = df['expiry_category'].value_counts()
    
    colors = {
        'Expired': '#ef4444',
        'Expiring Soon (≤7 days)': '#f59e0b',
        'Expiring This Month': '#3b82f6',
        'Long Term': '#10b981'
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=expiry_counts.index,
            y=expiry_counts.values,
            marker=dict(color=[colors.get(cat, '#6b7280') for cat in expiry_counts.index])
        )
    ])
    
    fig.update_layout(
        title="Booking Expiry Status",
        xaxis_title="Category",
        yaxis_title="Number of Bookings",
        height=400
    )
    
    return dcc.Graph(figure=fig)


def create_payments_table(df):
    """Create interactive payments table"""
    if df.empty:
        return html.Div("No payment data available")
    
    # Prepare data for table
    table_data = df.copy()
    table_data['days_until_end'] = table_data['days_until_end'].fillna(0).astype(int)
    
    # Add status indicators
    def get_status_indicator(row):
        if row['payment_status'] == 'paid':
            return "✅ Paid"
        elif row['days_until_end'] < 0:
            return "⚠️ Overdue"
        elif row['days_until_end'] <= 7:
            return "🔴 Expiring Soon"
        else:
            return "🟡 Pending"
    
    table_data['status_indicator'] = table_data.apply(get_status_indicator, axis=1)
    
    columns = [
        {"name": "Booking ID", "id": "booking_id", "type": "numeric"},
        {"name": "Customer", "id": "customer_name"},
        {"name": "Unit", "id": "unit_name"},
        {"name": "Warehouse", "id": "warehouse_name"},
        {"name": "Start Date", "id": "start_date", "type": "datetime"},
        {"name": "End Date", "id": "end_date", "type": "datetime"},
        {"name": "Amount", "id": "total_amount", "type": "numeric", "format": {"specifier": ",.2f"}},
        {"name": "Payment Status", "id": "payment_status"},
        {"name": "Days Until End", "id": "days_until_end", "type": "numeric"},
        {"name": "Status", "id": "status_indicator"},
    ]
    
    return dash_table.DataTable(
        id='payments-table',
        columns=columns,
        data=table_data.to_dict('records'),
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=20,
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Arial',
            'fontSize': '14px'
        },
        style_header={
            'backgroundColor': '#f8fafc',
            'fontWeight': 'bold',
            'border': '1px solid #e2e8f0'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{payment_status} = paid'},
                'backgroundColor': '#f0fdf4',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{days_until_end} < 0'},
                'backgroundColor': '#fef2f2',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{days_until_end} >= 0 && {days_until_end} <= 7'},
                'backgroundColor': '#fffbeb',
                'color': 'black',
            }
        ],
        style_table={'overflowX': 'auto'},
        css=[{
            'selector': '.dash-table-pagination .current-page',
            'rule': 'color: #3b82f6 !important;'
        }]
    )


# CONSOLIDATED LAYOUT FUNCTION
def serve_layout():
    """Serve layout based on consolidated authentication check"""
    has_access, reason = AuthManager.has_payments_access()
    
    if has_access:
        return create_authorized_layout()
    else:
        return create_access_denied_layout(reason)


# Set the app layout to use the consolidated layout function
app.layout = serve_layout


# Navigation access callback for CSO users (simplified)
@app.callback(
    Output('navigation-modal', 'children'),
    [Input('analytics-link', 'n_clicks'),
     Input('warehouses-link', 'n_clicks'),
     Input('bookings-link', 'n_clicks'),
     Input('reports-link', 'n_clicks'),
     Input('settings-link', 'n_clicks')],
    prevent_initial_call=True
)
def handle_navigation_access(analytics_clicks, warehouses_clicks, bookings_clicks, 
                           reports_clicks, settings_clicks):
    """Handle navigation access for CSO users"""
    current_user = AuthManager.get_current_user()
    
    # Only show modal for CSO users (admins have full access)
    if not current_user or current_user['type'] != 'cso':
        raise PreventUpdate
    
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Show access denied modal for CSO trying to access other pages
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Access Restricted", className="modal-title text-danger"),
                    html.Button("×", className="close", **{"data-dismiss": "modal"})
                ], className="modal-header"),
                html.Div([
                    html.P("Access denied. You are authorized only for Payment Management functions."),
                    html.P(f"Your role: {current_user['function_name']}")
                ], className="modal-body"),
                html.Div([
                    html.Button("OK", className="btn btn-secondary", **{"data-dismiss": "modal"})
                ], className="modal-footer")
            ], className="modal-content")
        ], className="modal-dialog")
    ], className="modal fade show", style={"display": "block"})


# Main dashboard update callback (simplified authentication check)
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('payment-status-chart', 'children'),
     Output('expiry-alert-chart', 'children'),
     Output('revenue-trend-chart', 'children'),
     Output('payments-table-container', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update all dashboard components with consolidated auth check"""
    has_access, _ = AuthManager.has_payments_access()
    
    if not has_access:
        raise PreventUpdate
    
    df = get_payment_data()
    
    if df.empty:
        empty_msg = html.Div([
            html.H4("No Data Available", className="text-muted text-center"),
            html.P("Please check your database connection and ensure there are booking records.", 
                  className="text-muted text-center")
        ], className="p-5")
        
        return empty_msg, empty_msg, empty_msg, empty_msg, empty_msg
    
    return (
        create_kpi_cards(df),
        create_payment_status_chart(df),
        create_expiry_alert_chart(df),
        create_revenue_trend_chart(df),
        create_payments_table(df)
    )