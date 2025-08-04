import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import pymysql
import mysql.connector
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from server import server
from flask import session, request, redirect, url_for
import urllib.parse

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'warehouse_db'
}

# Initialize the Dash app
app = Dash(
    __name__,
    server=server,
    url_base_pathname="/admin/analytics/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)

app.title = "CaelumSpaces - Analytics"


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


# Create SQLAlchemy engine for pandas compatibility
def create_db_engine():
    """Create SQLAlchemy engine for database connection"""
    password_encoded = urllib.parse.quote_plus(DB_CONFIG['password']) if DB_CONFIG['password'] else ''
    connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{password_encoded}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    return create_engine(connection_string)

# Session management functions
def get_current_user():
    """Get current user from session"""
    if 'user_id' in session and 'user_type' in session:
        return {
            'id': session.get('user_id'),
            'type': session.get('user_type'),
            'email': session.get('user_email'),
            'name': session.get('user_name'),
            'cso_name': session.get('cso_name'),
            'function_name': session.get('function_name')
        }
    return None

def is_admin():
    """Check if current user is admin"""
    current_user = get_current_user()
    return current_user and current_user['type'] == 'admin'

def require_admin():
    """Decorator-like function to check admin access"""
    if not is_admin():
        return False
    return True


class DataService:
    """Handle all database operations"""
    
    @staticmethod
    def get_db_engine():
        """Get SQLAlchemy engine"""
        return create_db_engine()
    
    @staticmethod
    def fetch_data(query):
        """Execute query and return DataFrame using SQLAlchemy"""
        try:
            engine = DataService.get_db_engine()
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        except Exception as e:
            print(f"Database error: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_warehouse_stats():
        """Get warehouse statistics - Fixed to match your schema"""
        query = """
        SELECT 
            w.id,
            w.name,
            w.location,
            w.capacity,
            COUNT(u.id) as total_units,
            COUNT(CASE WHEN u.availability = 'taken' THEN 1 END) as occupied_units,
            COUNT(CASE WHEN u.availability = 'not taken' THEN 1 END) as available_units,
            ROUND((COUNT(CASE WHEN u.availability = 'taken' THEN 1 END) / NULLIF(COUNT(u.id), 0)) * 100, 2) as occupancy_rate
        FROM warehouses w
        LEFT JOIN units u ON w.id = u.warehouse_id AND u.status = 'active'
        WHERE w.status = 'active'
        GROUP BY w.id, w.name, w.location, w.capacity
        """
        return DataService.fetch_data(query)
    
    @staticmethod
    def get_booking_summary():
        """Get booking summary data - Fixed to match your schema"""
        query = """
        SELECT 
            b.id,
            b.customer_name,
            b.customer_email,
            b.customer_phone,
            u.name as unit_name,
            w.name as warehouse_name,
            b.start_date,
            b.end_date,
            b.total_amount,
            b.status,
            b.payment_status,
            DATEDIFF(b.end_date, b.start_date) as duration_days
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE b.start_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ORDER BY b.start_date DESC
        """
        return DataService.fetch_data(query)
    
    @staticmethod
    def get_revenue_data():
        """Get revenue summary data - Fixed date formatting"""
        query = """
        SELECT 
            YEAR(b.start_date) as year,
            MONTH(b.start_date) as month,
            w.name as warehouse_name,
            COUNT(b.id) as total_bookings,
            SUM(b.total_amount) as total_revenue,
            AVG(b.total_amount) as avg_booking_value
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE b.status != 'cancelled'
        GROUP BY YEAR(b.start_date), MONTH(b.start_date), w.name
        ORDER BY year DESC, month DESC
        """
        return DataService.fetch_data(query)
    
    @staticmethod
    def get_monthly_trends():
        """Get monthly booking trends - Fixed date formatting"""
        query = """
        SELECT 
            CONCAT(YEAR(start_date), '-', LPAD(MONTH(start_date), 2, '0')) as month,
            COUNT(*) as total_bookings,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_booking_value
        FROM bookings 
        WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        AND status != 'cancelled'
        GROUP BY YEAR(start_date), MONTH(start_date)
        ORDER BY YEAR(start_date), MONTH(start_date)
        """
        return DataService.fetch_data(query)
    
    @staticmethod
    def get_payment_status_data():
        """Get payment status distribution"""
        query = """
        SELECT 
            payment_status,
            COUNT(*) as count,
            SUM(total_amount) as total_amount
        FROM bookings 
        WHERE status != 'cancelled'
        GROUP BY payment_status
        """
        return DataService.fetch_data(query)
    
    @staticmethod
    def get_unit_availability_data():
        """Get unit availability data"""
        query = """
        SELECT 
            availability,
            COUNT(*) as count
        FROM units 
        WHERE status = 'active'
        GROUP BY availability
        """
        return DataService.fetch_data(query)

class ChartFactory:
    """Factory class for creating charts with consistent styling"""
    
    # Color palette
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent1': '#f093fb',
        'accent2': '#f5576c',
        'success': '#43e97b',
        'warning': '#fa709a',
        'info': '#4facfe'
    }
    
    # Common layout settings
    LAYOUT_CONFIG = {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': dict(size=12, family="'Poppins', sans-serif"),
        'margin': dict(l=50, r=50, t=50, b=50),
        'height': 400,
        'hoverlabel': dict(
            bgcolor="white",
            font_size=12,
            font_family="'Segoe UI', sans-serif"
        )
    }
    
    @classmethod
    def create_utilization_chart(cls, warehouse_stats):
        """Create warehouse utilization chart"""
        if warehouse_stats.empty:
            return cls._create_empty_chart("No warehouse data available")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Available Units',
            x=warehouse_stats['name'],
            y=warehouse_stats['available_units'],
            marker_color=cls.COLORS['info'],
            hovertemplate='<b>%{x}</b><br>Available: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name='Occupied Units',
            x=warehouse_stats['name'],
            y=warehouse_stats['occupied_units'],
            marker_color=cls.COLORS['primary'],
            hovertemplate='<b>%{x}</b><br>Occupied: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            barmode='stack',
            title="Warehouse Unit Utilization",
            xaxis_title="Warehouse",
            yaxis_title="Number of Units",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    @classmethod
    def create_revenue_trend_chart(cls, monthly_trends):
        """Create revenue trend chart"""
        if monthly_trends.empty:
            return cls._create_empty_chart("No revenue data available")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_trends['month'],
            y=monthly_trends['total_revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color=cls.COLORS['success'], width=3),
            marker=dict(size=8, color=cls.COLORS['success']),
            hovertemplate='<b>%{x}</b><br>Revenue: ₦%{y:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            title="Monthly Revenue Trend",
            xaxis_title="Month",
            yaxis_title="Revenue (₦)",
            showlegend=False
        )
        
        return fig
    
    @classmethod
    def create_payment_status_chart(cls, payment_status):
        """Create payment status pie chart"""
        if payment_status.empty:
            return cls._create_empty_chart("No payment data available")
        
        colors = [cls.COLORS['primary'], cls.COLORS['success'], cls.COLORS['warning'], cls.COLORS['accent2']]
        
        fig = go.Figure(data=[go.Pie(
            labels=payment_status['payment_status'],
            values=payment_status['count'],
            hole=0.4,
            marker=dict(colors=colors[:len(payment_status)]),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            title="Payment Status Distribution"
        )
        
        return fig
    
    @classmethod
    def create_occupancy_chart(cls, warehouse_stats):
        """Create occupancy rate chart"""
        if warehouse_stats.empty:
            return cls._create_empty_chart("No occupancy data available")
        
        # Handle None values in occupancy_rate
        occupancy_rates = warehouse_stats['occupancy_rate'].fillna(0)
        
        fig = go.Figure([go.Bar(
            x=warehouse_stats['name'],
            y=occupancy_rates,
            marker_color=cls.COLORS['accent1'],
            text=[f'{rate:.1f}%' if pd.notna(rate) else '0.0%' for rate in occupancy_rates],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Occupancy: %{y:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            title="Occupancy Rate by Warehouse",
            xaxis_title="Warehouse",
            yaxis_title="Occupancy Rate (%)",
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    @classmethod
    def create_booking_status_chart(cls, booking_data):
        """Create booking status chart"""
        if booking_data.empty:
            return cls._create_empty_chart("No booking data available")
        
        status_counts = booking_data['status'].value_counts()
        colors = [cls.COLORS['primary'], cls.COLORS['success'], cls.COLORS['warning'], cls.COLORS['accent2']]
        
        fig = go.Figure([go.Bar(
            x=status_counts.index,
            y=status_counts.values,
            marker_color=colors[:len(status_counts)],
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            title="Booking Status Overview",
            xaxis_title="Status",
            yaxis_title="Number of Bookings",
            showlegend=False
        )
        
        return fig
    
    @classmethod
    def create_warehouse_revenue_chart(cls, revenue_data):
        """Create warehouse revenue chart"""
        if revenue_data.empty:
            return cls._create_empty_chart("No revenue data available")
        
        warehouse_revenue = revenue_data.groupby('warehouse_name')['total_revenue'].sum().reset_index()
        
        fig = go.Figure([go.Bar(
            x=warehouse_revenue['warehouse_name'],
            y=warehouse_revenue['total_revenue'],
            marker_color=cls.COLORS['warning'],
            text=[f'₦{val:,.2f}' for val in warehouse_revenue['total_revenue']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Revenue: ₦%{y:,.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            **cls.LAYOUT_CONFIG,
            title="Total Revenue by Warehouse",
            xaxis_title="Warehouse",
            yaxis_title="Revenue (₦)",
            showlegend=False
        )
        
        return fig
    
    @classmethod
    def _create_empty_chart(cls, message="No data available"):
        """Create an empty chart with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(**cls.LAYOUT_CONFIG, title="")
        return fig

class ComponentFactory:
    """Factory for creating dashboard components"""
    
    @staticmethod
    def create_kpi_cards(warehouse_stats, booking_data, revenue_data):
        """Create KPI cards"""
        if warehouse_stats.empty:
            return html.Div("Loading KPI data...", className="loading-message")
        
        total_warehouses = len(warehouse_stats)
        total_units = warehouse_stats['total_units'].sum()
        occupied_units = warehouse_stats['occupied_units'].sum()
        avg_occupancy = warehouse_stats['occupancy_rate'].fillna(0).mean()
        total_revenue = revenue_data['total_revenue'].sum() if not revenue_data.empty else 0
        
        return html.Div([
            html.Div([
                html.I(className="kpi-icon fas fa-warehouse"),
                html.H3(f"{total_warehouses}", className="kpi-value"),
                html.P("Total Warehouses", className="kpi-label")
            ], className="kpi-card warehouse-card"),
            
            html.Div([
                html.I(className="kpi-icon fas fa-boxes"),
                html.H3(f"{total_units}", className="kpi-value"),
                html.P("Total Units", className="kpi-label")
            ], className="kpi-card units-card"),
            
            html.Div([
                html.I(className="kpi-icon fas fa-check-circle"),
                html.H3(f"{occupied_units}", className="kpi-value"),
                html.P("Occupied Units", className="kpi-label")
            ], className="kpi-card occupied-card"),
            
            html.Div([
                html.I(className="kpi-icon fas fa-chart-line"),
                html.H3(f"{avg_occupancy:.1f}%", className="kpi-value"),
                html.P("Average Occupancy", className="kpi-label")
            ], className="kpi-card occupancy-card"),
            
            html.Div([
                html.I(className="kpi-icon fa-solid fa-naira-sign"),
                html.H3(f"₦{total_revenue:,.2f}", className="kpi-value"),
                html.P("Total Revenue", className="kpi-label")
            ], className="kpi-card revenue-card")
        ], className="kpi-grid")

def create_layout():
    """Create the main layout - only called if user is admin"""
    current_user = get_current_user()
    
    return html.Div([
        # Header
        html.Header([
            html.Div([
                html.H1("CaelumSpaces", className="dashboard-title"),
                html.Div([
                    html.Span(f"Welcome Admin: {current_user['email'] if current_user else 'Unknown'}", 
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
                        html.Li([html.A("📊 Analytics", href="/admin/analytics/", className="nav-link active")]),
                        html.Li([html.A("📦 Warehouses", href="/admin/units_creation", className="nav-link")]),
                        html.Li([html.A("📋 Bookings", href="/bookings", className="nav-link")]),
                        html.Li([html.A("💰 Revenue", href="/revenue", className="nav-link")]),
                        html.Li([html.A("📈 Reports", href="/reports", className="nav-link")]),
                        html.Li([html.A("⚙️ Settings", href="/settings", className="nav-link")]),
                        html.Li([
                            html.A("🚪 Logout", href="/logout", className="nav-link logout-link", 
                                  style={"color": "#f5576c", "border-top": "1px solid #eee", "margin-top": "20px", "padding-top": "15px"})
                        ])
                    ], className="nav-menu")
                ], className="sidebar-content")
            ], className="sidebar"),
            
            # Main Dashboard Content
            html.Div([
                # Key Metrics Cards
                html.Div([
                    html.H2("Key Performance Indicators", className="section-title"),
                    html.Div(id="kpi-cards", className="kpi-container")
                ], className="metrics-section"),
                
                # Charts Row 1
                html.Div([
                    html.Div([
                        html.H3("Warehouse Utilization", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="warehouse-utilization-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Monthly Revenue Trend", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="revenue-trend-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container")
                ], className="charts-row"),
                
                # Charts Row 2
                html.Div([
                    html.Div([
                        html.H3("Payment Status Distribution", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="payment-status-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Occupancy Rate by Warehouse", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="occupancy-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container")
                ], className="charts-row"),
                
                # Charts Row 3
                html.Div([
                    html.Div([
                        html.H3("Booking Status Overview", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="booking-status-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Revenue by Warehouse", className="chart-title"),
                        html.Div([
                            dcc.Graph(id="warehouse-revenue-chart", config={'displayModeBar': False})
                        ], className="chart-wrapper")
                    ], className="chart-container")
                ], className="charts-row"),
                
                # Auto-refresh interval
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
                )
            ], className="main-content")
        ], className="dashboard-body"),
        
        # Footer
        html.Footer([
            html.P("© 2025 CaelumSpaces Warehouse Management System. All rights reserved.", 
                   className="footer-text")
        ], className="dashboard-footer")
    ], className="dashboard-container")

def create_access_denied_layout():
    """Create access denied layout for non-admin users"""
    return html.Div([
        html.Div([
            html.H1("Access Denied", style={"color": "#f5576c", "text-align": "center", "margin-top": "100px"}),
            html.P("You do not have permission to access this page. Only administrators can view the analytics dashboard.", 
                   style={"text-align": "center", "margin": "20px", "font-size": "18px"}),
            html.Div([
                html.A("Go to Login", href="/login", className="btn btn-primary", 
                       style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                              "background-color": "#667eea", "color": "white", "border-radius": "5px"}),
                html.A("Go to Home", href="/", className="btn btn-secondary",
                       style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                              "background-color": "#6c757d", "color": "white", "border-radius": "5px"})
            ], style={"text-align": "center", "margin-top": "30px"})
        ])
    ])

def create_not_logged_in_layout():
    """Create layout for users who are not logged in"""
    return html.Div([
        html.Div([
            html.H1("Please Log In", style={"color": "#667eea", "text-align": "center", "margin-top": "100px"}),
            html.P("You need to be logged in to access this page.", 
                   style={"text-align": "center", "margin": "20px", "font-size": "18px"}),
            html.Div([
                html.A("Login", href="/login", className="btn btn-primary", 
                       style={"margin": "10px", "padding": "10px 20px", "text-decoration": "none", 
                              "background-color": "#667eea", "color": "white", "border-radius": "5px"})
            ], style={"text-align": "center", "margin-top": "30px"})
        ])
    ])

# Dynamic layout based on user authentication and role
def serve_layout():
    """Serve layout based on user authentication and role"""
    current_user = get_current_user()
    
    if not current_user:
        return create_not_logged_in_layout()
    
    if current_user['type'] != 'admin':
        return create_access_denied_layout()
    
    return create_layout()

# Set the app layout to use the dynamic layout function
app.layout = serve_layout

# Callbacks - only executed if user has access
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('warehouse-utilization-chart', 'figure'),
     Output('revenue-trend-chart', 'figure'),
     Output('payment-status-chart', 'figure'),
     Output('occupancy-chart', 'figure'),
     Output('booking-status-chart', 'figure'),
     Output('warehouse-revenue-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update all dashboard components - only for admin users"""
    # Double-check admin access in callback
    if not is_admin():
        # Return empty figures if not admin
        empty_fig = go.Figure()
        return ("Access Denied", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)
    
    # Get data
    warehouse_stats = DataService.get_warehouse_stats()
    booking_data = DataService.get_booking_summary()
    revenue_data = DataService.get_revenue_data()
    monthly_trends = DataService.get_monthly_trends()
    payment_status = DataService.get_payment_status_data()
    
    # Create components
    kpi_cards = ComponentFactory.create_kpi_cards(warehouse_stats, booking_data, revenue_data)
    
    # Create charts
    utilization_fig = ChartFactory.create_utilization_chart(warehouse_stats)
    revenue_trend_fig = ChartFactory.create_revenue_trend_chart(monthly_trends)
    payment_status_fig = ChartFactory.create_payment_status_chart(payment_status)
    occupancy_fig = ChartFactory.create_occupancy_chart(warehouse_stats)
    booking_status_fig = ChartFactory.create_booking_status_chart(booking_data)
    warehouse_revenue_fig = ChartFactory.create_warehouse_revenue_chart(revenue_data)
    
    return (kpi_cards, utilization_fig, revenue_trend_fig, 
           payment_status_fig, occupancy_fig, booking_status_fig, 
           warehouse_revenue_fig)