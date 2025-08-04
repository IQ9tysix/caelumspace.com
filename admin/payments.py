import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
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
import warnings
warnings.filterwarnings('ignore')

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'warehouse_db',
    'user': 'root',
    'password': ''  # Update with your MySQL password
}

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

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# Custom CSS styles
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#1e293b",
    "color": "white",
    "z-index": 1000
}

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "margin-top": "1rem",
    "padding": "2rem 1rem",
    "background-color": "#f8fafc"
}

HEADER_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": "20rem",
    "right": 0,
    "height": "4rem",
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "color": "white",
    "display": "flex",
    "align-items": "center",
    "padding": "0 2rem",
    "box-shadow": "0 2px 10px rgba(0,0,0,0.1)",
    "z-index": 999
}

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

def get_revenue_analytics():
    """Get revenue analytics data"""
    query = """
    SELECT 
        w.name as warehouse_name,
        DATE_FORMAT(b.start_date, '%Y-%m') as month_year,
        COUNT(b.id) as total_bookings,
        SUM(b.total_amount) as total_revenue,
        SUM(CASE WHEN b.payment_status = 'paid' THEN b.total_amount ELSE 0 END) as paid_revenue,
        SUM(CASE WHEN b.payment_status = 'pending' THEN b.total_amount ELSE 0 END) as pending_revenue
    FROM bookings b
    JOIN units u ON b.unit_id = u.id
    JOIN warehouses w ON u.warehouse_id = w.id
    WHERE b.status != 'cancelled'
    AND b.start_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY w.id, w.name, DATE_FORMAT(b.start_date, '%Y-%m')
    ORDER BY month_year DESC, warehouse_name
    """
    
    try:
        data = db_manager.execute_query(query)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching revenue analytics: {e}")
        return pd.DataFrame()

def create_sidebar():
    """Create the navigation sidebar"""
    return html.Div([
        html.Div([
            html.H3("🏢 Warehouse Admin", className="text-white mb-4"),
            html.Hr(style={"border-color": "#475569"}),
            
            dbc.Nav([
                dbc.NavLink([
                    html.I(className="fas fa-credit-card me-2"),
                    "Payment Management"
                ], href="#", active=True, className="text-white mb-2"),
                
                dbc.NavLink([
                    html.I(className="fas fa-chart-line me-2"),
                    "Analytics"
                ], href="#", className="text-white mb-2"),
                
                dbc.NavLink([
                    html.I(className="fas fa-warehouse me-2"),
                    "Warehouses"
                ], href="#", className="text-white mb-2"),
                
                dbc.NavLink([
                    html.I(className="fas fa-cube me-2"),
                    "Units"
                ], href="#", className="text-white mb-2"),
                
                dbc.NavLink([
                    html.I(className="fas fa-users me-2"),
                    "Customers"
                ], href="#", className="text-white mb-2"),
                
                dbc.NavLink([
                    html.I(className="fas fa-cog me-2"),
                    "Settings"
                ], href="#", className="text-white mb-2"),
            ], vertical=True, pills=True),
        ], style={"padding": "1rem"}),
        
        html.Div([
            html.Hr(style={"border-color": "#475569"}),
            html.P("© 2025 Warehouse Management System", 
                  className="text-muted small text-center mb-0")
        ], style={"position": "absolute", "bottom": "1rem", "left": "1rem", "right": "1rem"})
    ], style=SIDEBAR_STYLE)

def create_header():
    """Create the top header"""
    return html.Div([
        html.Div([
            html.H4("💳 Payment Management Dashboard", className="mb-0"),
            html.P(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                  className="mb-0 opacity-75 small")
        ]),
        
        html.Div([
            dbc.Button([
                html.I(className="fas fa-bell me-2"),
                html.Span("5", className="badge bg-danger rounded-pill ms-1")
            ], color="light", outline=True, className="me-2"),
            
            dbc.Button([
                html.I(className="fas fa-user-circle me-2"),
                "Admin"
            ], color="light", outline=True)
        ], className="d-flex align-items-center")
    ], style=HEADER_STYLE, className="d-flex justify-content-between align-items-center")

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
    
    cards = [
        dbc.Card([
            dbc.CardBody([
                html.H4(f"₦{total_revenue:,.2f}", className="text-primary mb-0"),
                html.P("Total Revenue", className="text-muted mb-0"),
                html.Small(f"From {total_bookings} bookings", className="text-muted")
            ])
        ], className="border-0 shadow-sm"),
        
        dbc.Card([
            dbc.CardBody([
                html.H4(f"₦{paid_revenue:,.2f}", className="text-success mb-0"),
                html.P("Paid Revenue", className="text-muted mb-0"),
                html.Small(f"{(paid_revenue/total_revenue*100):.1f}% collected" if total_revenue > 0 else "0% collected", 
                          className="text-success")
            ])
        ], className="border-0 shadow-sm"),
        
        dbc.Card([
            dbc.CardBody([
                html.H4(f"₦{pending_revenue:,.2f}", className="text-warning mb-0"),
                html.P("Pending Revenue", className="text-muted mb-0"),
                html.Small(f"{(pending_revenue/total_revenue*100):.1f}% pending" if total_revenue > 0 else "0% pending", 
                          className="text-warning")
            ])
        ], className="border-0 shadow-sm"),
        
        dbc.Card([
            dbc.CardBody([
                html.H4(f"{expiring_soon}", className="text-info mb-0"),
                html.P("Expiring Soon", className="text-muted mb-0"),
                html.Small("Within 7 days", className="text-info")
            ])
        ], className="border-0 shadow-sm"),
        
        dbc.Card([
            dbc.CardBody([
                html.H4(f"{overdue_payments}", className="text-danger mb-0"),
                html.P("Overdue Payments", className="text-muted mb-0"),
                html.Small("Requires attention", className="text-danger")
            ])
        ], className="border-0 shadow-sm"),
    ]
    
    return dbc.Row([
        dbc.Col(card, md=2, className="mb-3") for card in cards
    ], className="mb-4")

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

# App layout
app.layout = html.Div([
    create_sidebar(),
    create_header(),
    
    html.Div([
        # Main content area
        html.Div([
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # Update every 30 seconds
                n_intervals=0
            ),
            
            # KPI Cards
            html.Div(id='kpi-cards'),
            
            # Charts Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='payment-status-chart')
                        ])
                    ], className="shadow-sm border-0")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='expiry-alert-chart')
                        ])
                    ], className="shadow-sm border-0")
                ], md=6),
            ], className="mb-4"),
            
            # Revenue Trend
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id='revenue-trend-chart')
                        ])
                    ], className="shadow-sm border-0")
                ], md=12),
            ], className="mb-4"),
            
            # Payments Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📊 Payment Records", className="mb-0"),
                            html.Small("Real-time payment tracking and management", className="text-muted")
                        ]),
                        dbc.CardBody([
                            html.Div(id='payments-table-container')
                        ])
                    ], className="shadow-sm border-0")
                ], md=12),
            ], className="mb-4"),
            
        ], id="main-content")
    ], style=CONTENT_STYLE)
])

# Callbacks
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('payment-status-chart', 'children'),
     Output('expiry-alert-chart', 'children'),
     Output('revenue-trend-chart', 'children'),
     Output('payments-table-container', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update all dashboard components"""
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

if __name__ == '__main__':
    # Initialize database connection
    if db_manager.connect():
        print("✅ Database connected successfully!")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("❌ Failed to connect to database. Please check your configuration.")