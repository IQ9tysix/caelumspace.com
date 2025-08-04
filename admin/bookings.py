import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your password here
    'database': 'warehouse_db',
    'charset': 'utf8mb4'
}

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def get_connection(self):
        """Get database connection"""
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        conn = self.get_connection()
        if conn:
            try:
                df = pd.read_sql(query, conn, params=params)
                return df
            except Exception as e:
                print(f"Query execution error: {e}")
                return pd.DataFrame()
            finally:
                conn.close()
        return pd.DataFrame()
    
    def execute_procedure(self, procedure_name: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute stored procedure"""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc(procedure_name, params or ())
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                    columns = [desc[0] for desc in result.description]
                df = pd.DataFrame(results, columns=columns)
                return df
            except Exception as e:
                print(f"Procedure execution error: {e}")
                return pd.DataFrame()
            finally:
                conn.close()
        return pd.DataFrame()

# Initialize database manager
db_manager = DatabaseManager(DB_CONFIG)

# Custom CSS styles
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545',
    'light': '#F8F9FA',
    'dark': '#212529',
    'white': '#FFFFFF',
    'gray': '#6C757D',
    'light_gray': '#E9ECEF'
}

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
])

app.title = "Storage Warehouse Admin Dashboard"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .main-container {
                display: flex;
                height: 100vh;
            }
            .sidebar {
                width: 280px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 0;
                overflow-y: auto;
            }
            .main-content {
                flex: 1;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                overflow-y: auto;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 30px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            .content-area {
                padding: 30px;
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 25px;
                margin: 10px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }
            .chart-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .sidebar-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            .sidebar-menu {
                padding: 20px 0;
            }
            .menu-item {
                display: block;
                padding: 15px 25px;
                color: #333;
                text-decoration: none;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }
            .menu-item:hover {
                background: rgba(102, 126, 234, 0.1);
                border-left-color: #667eea;
                color: #667eea;
            }
            .menu-item.active {
                background: rgba(102, 126, 234, 0.15);
                border-left-color: #667eea;
                color: #667eea;
                font-weight: 600;
            }
            .data-table {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            .status-badge {
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }
            .status-pending {
                background: #FFF3CD;
                color: #856404;
            }
            .status-confirmed {
                background: #D4EDDA;
                color: #155724;
            }
            .status-cancelled {
                background: #F8D7DA;
                color: #721C24;
            }
            .status-completed {
                background: #CCE5FF;
                color: #004085;
            }
            .filter-container {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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

def get_booking_data():
    """Fetch booking data from database"""
    query = """
    SELECT 
        b.id,
        b.customer_name,
        b.customer_email,
        b.customer_phone,
        b.start_date,
        b.end_date,
        b.total_amount,
        b.status,
        b.payment_status,
        b.created_at,
        u.name as unit_name,
        w.name as warehouse_name,
        w.location as warehouse_location,
        DATEDIFF(b.end_date, b.start_date) as duration_days
    FROM bookings b
    JOIN units u ON b.unit_id = u.id
    JOIN warehouses w ON u.warehouse_id = w.id
    ORDER BY b.created_at DESC
    """
    return db_manager.execute_query(query)

def get_revenue_data():
    """Fetch revenue data"""
    query = """
    SELECT 
        w.name as warehouse_name,
        YEAR(b.start_date) as year,
        MONTH(b.start_date) as month,
        COUNT(b.id) as total_bookings,
        SUM(b.total_amount) as total_revenue,
        SUM(CASE WHEN b.payment_status = 'paid' THEN b.total_amount ELSE 0 END) as paid_revenue,
        SUM(CASE WHEN b.payment_status = 'pending' THEN b.total_amount ELSE 0 END) as pending_revenue
    FROM bookings b
    JOIN units u ON b.unit_id = u.id
    JOIN warehouses w ON u.warehouse_id = w.id
    WHERE b.status != 'cancelled'
    GROUP BY w.id, w.name, YEAR(b.start_date), MONTH(b.start_date)
    ORDER BY year DESC, month DESC
    """
    return db_manager.execute_query(query)

def get_warehouse_stats():
    """Fetch warehouse statistics"""
    query = """
    SELECT 
        w.id,
        w.name,
        w.location,
        w.capacity,
        COUNT(u.id) as total_units,
        COUNT(CASE WHEN u.availability = 'taken' THEN 1 END) as occupied_units,
        COUNT(CASE WHEN u.availability = 'not taken' AND u.status = 'active' THEN 1 END) as available_units,
        ROUND((COUNT(CASE WHEN u.availability = 'taken' THEN 1 END) / w.capacity) * 100, 2) as occupancy_rate
    FROM warehouses w
    LEFT JOIN units u ON w.id = u.warehouse_id
    WHERE w.status = 'active'
    GROUP BY w.id, w.name, w.location, w.capacity
    """
    return db_manager.execute_query(query)

def create_sidebar():
    """Create sidebar component"""
    return html.Div([
        html.Div([
            html.H3("📊 Warehouse Admin", className="text-center mb-0"),
            html.P("Management Dashboard", className="text-center text-sm opacity-75 mt-1")
        ], className="sidebar-header"),
        
        html.Div([
            html.A([
                html.I(className="fas fa-calendar-check mr-3"),
                "Bookings Management"
            ], href="#", className="menu-item active"),
            
            html.A([
                html.I(className="fas fa-warehouse mr-3"),
                "Warehouse Overview"
            ], href="#", className="menu-item"),
            
            html.A([
                html.I(className="fas fa-chart-line mr-3"),
                "Revenue Analytics"
            ], href="#", className="menu-item"),
            
            html.A([
                html.I(className="fas fa-users mr-3"),
                "Customer Management"
            ], href="#", className="menu-item"),
            
            html.A([
                html.I(className="fas fa-cog mr-3"),
                "Settings"
            ], href="#", className="menu-item"),
        ], className="sidebar-menu")
    ], className="sidebar")

def create_header():
    """Create header component"""
    return html.Div([
        html.Div([
            html.H1("🏢 Bookings Management Dashboard", className="text-2xl font-bold mb-2"),
            html.P("Monitor, analyze, and manage all warehouse bookings", className="opacity-75")
        ], className="flex-1"),
        
        html.Div([
            html.Div([
                html.I(className="fas fa-user-circle text-2xl mr-3"),
                html.Span("Admin User", className="font-medium")
            ], className="flex items-center")
        ])
    ], className="header flex items-center justify-between")

def create_metric_cards(df):
    """Create metric cards"""
    if df.empty:
        return html.Div("No data available", className="text-center text-gray-500")
    
    total_bookings = len(df)
    total_revenue = df['total_amount'].sum()
    pending_bookings = len(df[df['status'] == 'pending'])
    confirmed_bookings = len(df[df['status'] == 'confirmed'])
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-calendar-check text-3xl text-blue-500 mb-3"),
                html.H3(f"{total_bookings:,}", className="text-2xl font-bold text-gray-800"),
                html.P("Total Bookings", className="text-gray-600 font-medium")
            ], className="metric-card text-center"),
            
            html.Div([
                html.I(className="fas fa-money-bill-wave text-3xl text-green-500 mb-3"),
                html.H3(f"₦{total_revenue:,.2f}", className="text-2xl font-bold text-gray-800"),
                html.P("Total Revenue", className="text-gray-600 font-medium")
            ], className="metric-card text-center"),
            
            html.Div([
                html.I(className="fas fa-clock text-3xl text-yellow-500 mb-3"),
                html.H3(f"{pending_bookings:,}", className="text-2xl font-bold text-gray-800"),
                html.P("Pending Bookings", className="text-gray-600 font-medium")
            ], className="metric-card text-center"),
            
            html.Div([
                html.I(className="fas fa-check-circle text-3xl text-green-600 mb-3"),
                html.H3(f"{confirmed_bookings:,}", className="text-2xl font-bold text-gray-800"),
                html.P("Confirmed Bookings", className="text-gray-600 font-medium")
            ], className="metric-card text-center"),
        ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4")
    ])

def create_status_distribution_chart(df):
    """Create status distribution chart"""
    if df.empty:
        return html.Div("No data available")
    
    status_counts = df['status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Booking Status Distribution",
        color_discrete_map={
            'pending': '#FFC107',
            'confirmed': '#28A745',
            'cancelled': '#DC3545',
            'completed': '#17A2B8'
        }
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=14),
        title_font_size=18,
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig)

def create_revenue_trend_chart(df):
    """Create revenue trend chart"""
    if df.empty:
        return html.Div("No data available")
    
    # Group by date and calculate daily revenue
    df['date'] = pd.to_datetime(df['start_date'])
    daily_revenue = df.groupby('date')['total_amount'].sum().reset_index()
    
    fig = px.line(
        daily_revenue,
        x='date',
        y='total_amount',
        title="Daily Revenue Trend",
        labels={'total_amount': 'Revenue (₦)', 'date': 'Date'}
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=14),
        title_font_size=18,
        xaxis_title="Date",
        yaxis_title="Revenue (₦)",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(line=dict(color='#667eea', width=3))
    
    return dcc.Graph(figure=fig)

def create_warehouse_performance_chart(df):
    """Create warehouse performance chart"""
    if df.empty:
        return html.Div("No data available")
    
    warehouse_stats = df.groupby('warehouse_name').agg({
        'total_amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    warehouse_stats.columns = ['warehouse_name', 'total_revenue', 'total_bookings']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Revenue by Warehouse', 'Bookings by Warehouse'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=warehouse_stats['warehouse_name'],
            y=warehouse_stats['total_revenue'],
            name='Revenue',
            marker_color='#667eea'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=warehouse_stats['warehouse_name'],
            y=warehouse_stats['total_bookings'],
            name='Bookings',
            marker_color='#764ba2'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=14),
        title_text="Warehouse Performance Analysis",
        title_font_size=18,
        height=500,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig)

def create_booking_duration_analysis(df):
    """Create booking duration analysis"""
    if df.empty:
        return html.Div("No data available")
    
    fig = px.histogram(
        df,
        x='duration_days',
        nbins=20,
        title="Booking Duration Distribution",
        labels={'duration_days': 'Duration (Days)', 'count': 'Number of Bookings'}
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=14),
        title_font_size=18,
        xaxis_title="Duration (Days)",
        yaxis_title="Number of Bookings",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(marker_color='#F18F01')
    
    return dcc.Graph(figure=fig)

def create_bookings_table(df):
    """Create bookings data table"""
    if df.empty:
        return html.Div("No bookings data available", className="text-center text-gray-500")
    
    # Format data for display
    display_df = df.copy()
    display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"₦{x:,.2f}")
    display_df['start_date'] = pd.to_datetime(display_df['start_date']).dt.strftime('%Y-%m-%d')
    display_df['end_date'] = pd.to_datetime(display_df['end_date']).dt.strftime('%Y-%m-%d')
    
    columns = [
        {"name": "ID", "id": "id", "type": "numeric"},
        {"name": "Customer", "id": "customer_name", "type": "text"},
        {"name": "Email", "id": "customer_email", "type": "text"},
        {"name": "Phone", "id": "customer_phone", "type": "text"},
        {"name": "Unit", "id": "unit_name", "type": "text"},
        {"name": "Warehouse", "id": "warehouse_name", "type": "text"},
        {"name": "Start Date", "id": "start_date", "type": "datetime"},
        {"name": "End Date", "id": "end_date", "type": "datetime"},
        {"name": "Duration", "id": "duration_days", "type": "numeric"},
        {"name": "Amount", "id": "total_amount", "type": "text"},
        {"name": "Status", "id": "status", "type": "text"},
        {"name": "Payment", "id": "payment_status", "type": "text"}
    ]
    
    return dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=15,
        sort_action="native",
        filter_action="native",
        row_selectable="multi",
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Inter',
            'fontSize': '14px'
        },
        style_header={
            'backgroundColor': '#667eea',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{status} = pending'},
                'backgroundColor': '#FFF3CD',
                'color': '#856404'
            },
            {
                'if': {'filter_query': '{status} = confirmed'},
                'backgroundColor': '#D4EDDA',
                'color': '#155724'
            },
            {
                'if': {'filter_query': '{status} = cancelled'},
                'backgroundColor': '#F8D7DA',
                'color': '#721C24'
            },
            {
                'if': {'filter_query': '{status} = completed'},
                'backgroundColor': '#CCE5FF',
                'color': '#004085'
            }
        ],
        style_table={'overflowX': 'auto'},
        className="data-table"
    )

def create_filters():
    """Create filter components"""
    return html.Div([
        html.H4("📊 Analytics Filters", className="text-lg font-bold mb-4"),
        
        html.Div([
            html.Div([
                html.Label("Date Range:", className="block text-sm font-medium mb-2"),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=datetime.now(),
                    display_format='YYYY-MM-DD',
                    style={'width': '100%'}
                )
            ], className="flex-1 mr-4"),
            
            html.Div([
                html.Label("Status:", className="block text-sm font-medium mb-2"),
                dcc.Dropdown(
                    id='status-filter',
                    options=[
                        {'label': 'All Statuses', 'value': 'all'},
                        {'label': 'Pending', 'value': 'pending'},
                        {'label': 'Confirmed', 'value': 'confirmed'},
                        {'label': 'Cancelled', 'value': 'cancelled'},
                        {'label': 'Completed', 'value': 'completed'}
                    ],
                    value='all',
                    style={'width': '100%'}
                )
            ], className="flex-1 mr-4"),
            
            html.Div([
                html.Label("Warehouse:", className="block text-sm font-medium mb-2"),
                dcc.Dropdown(
                    id='warehouse-filter',
                    value='all',
                    style={'width': '100%'}
                )
            ], className="flex-1")
        ], className="flex flex-wrap items-end")
    ], className="filter-container")

# Layout
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    ),
    
    html.Div([
        create_sidebar(),
        
        html.Div([
            create_header(),
            
            html.Div([
                create_filters(),
                
                html.Div(id="metric-cards-container"),
                
                html.Div([
                    html.Div([
                        html.Div(id="status-chart-container", className="chart-container")
                    ], className="w-full lg:w-1/2 px-2"),
                    
                    html.Div([
                        html.Div(id="revenue-chart-container", className="chart-container")
                    ], className="w-full lg:w-1/2 px-2")
                ], className="flex flex-wrap -mx-2"),
                
                html.Div([
                    html.Div(id="warehouse-performance-container", className="chart-container")
                ]),
                
                html.Div([
                    html.Div(id="duration-analysis-container", className="chart-container")
                ]),
                
                html.Div([
                    html.H3("📋 Detailed Bookings Table", className="text-xl font-bold mb-4"),
                    html.Div(id="bookings-table-container")
                ], className="chart-container")
                
            ], className="content-area")
        ], className="main-content")
    ], className="main-container")
])

# Callbacks
@app.callback(
    [Output('warehouse-filter', 'options'),
     Output('metric-cards-container', 'children'),
     Output('status-chart-container', 'children'),
     Output('revenue-chart-container', 'children'),
     Output('warehouse-performance-container', 'children'),
     Output('duration-analysis-container', 'children'),
     Output('bookings-table-container', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('status-filter', 'value'),
     Input('warehouse-filter', 'value')]
)
def update_dashboard(n_intervals, start_date, end_date, status_filter, warehouse_filter):
    """Update dashboard components"""
    # Get booking data
    df = get_booking_data()
    
    if df.empty:
        empty_msg = html.Div("No data available", className="text-center text-gray-500")
        return (
            [{'label': 'No warehouses', 'value': 'none'}],
            empty_msg, empty_msg, empty_msg, empty_msg, empty_msg, empty_msg
        )
    
    # Get warehouse options
    warehouse_options = [{'label': 'All Warehouses', 'value': 'all'}]
    warehouse_options.extend([
        {'label': name, 'value': name} 
        for name in df['warehouse_name'].unique()
    ])
    
    # Apply filters
    filtered_df = df.copy()
    
    if start_date and end_date:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['start_date']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(filtered_df['start_date']) <= pd.to_datetime(end_date))
        ]
    
    if status_filter != 'all':
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    if warehouse_filter != 'all':
        filtered_df = filtered_df[filtered_df['warehouse_name'] == warehouse_filter]
    
    # Create components
    metric_cards = create_metric_cards(filtered_df)
    status_chart = create_status_distribution_chart(filtered_df)
    revenue_chart = create_revenue_trend_chart(filtered_df)
    warehouse_chart = create_warehouse_performance_chart(filtered_df)
    duration_chart = create_booking_duration_analysis(filtered_df)
    bookings_table = create_bookings_table(filtered_df)
    
    return (
        warehouse_options,
        metric_cards,
        status_chart,
        revenue_chart,
        warehouse_chart,
        duration_chart,
        bookings_table
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)