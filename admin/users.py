import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, ctx
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import io

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL password
    'database': 'warehouse_db',
    'port': 3306
}

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def execute_query(self, query, params=None, fetch=True):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_users(self):
        query = """
        SELECT 
            u.id,
            u.username,
            u.email,
            u.role,
            u.status,
            u.created_at,
            u.updated_at,
            COUNT(DISTINCT b.id) as total_bookings,
            COALESCE(SUM(b.total_amount), 0) as total_revenue,
            MAX(b.created_at) as last_booking_date
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        GROUP BY u.id, u.username, u.email, u.role, u.status, u.created_at, u.updated_at
        ORDER BY u.created_at DESC
        """
        return self.db.execute_query(query)
    
    def get_user_analytics(self):
        # User status distribution
        status_query = """
        SELECT status, COUNT(*) as count
        FROM users
        GROUP BY status
        """
        
        # User role distribution
        role_query = """
        SELECT role, COUNT(*) as count
        FROM users
        GROUP BY role
        """
        
        # Monthly user registration
        monthly_query = """
        SELECT 
            YEAR(created_at) as year,
            MONTH(created_at) as month,
            COUNT(*) as new_users
        FROM users
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        GROUP BY YEAR(created_at), MONTH(created_at)
        ORDER BY year, month
        """
        
        # Top revenue generating users
        revenue_query = """
        SELECT 
            u.username,
            u.email,
            COUNT(b.id) as total_bookings,
            SUM(b.total_amount) as total_revenue
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        WHERE b.status != 'cancelled'
        GROUP BY u.id, u.username, u.email
        HAVING total_revenue > 0
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        return {
            'status_dist': self.db.execute_query(status_query),
            'role_dist': self.db.execute_query(role_query),
            'monthly_users': self.db.execute_query(monthly_query),
            'top_revenue_users': self.db.execute_query(revenue_query)
        }
    
    def update_user_status(self, user_id, status):
        query = "UPDATE users SET status = %s, updated_at = NOW() WHERE id = %s"
        return self.db.execute_query(query, (status, user_id), fetch=False)
    
    def update_user_info(self, user_id, username, email, role):
        query = """
        UPDATE users 
        SET username = %s, email = %s, role = %s, updated_at = NOW() 
        WHERE id = %s
        """
        return self.db.execute_query(query, (username, email, role, user_id), fetch=False)

# Initialize managers
user_manager = UserManager()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
])

# Custom CSS styles
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1([
                html.I(className="fas fa-warehouse", style={'marginRight': '15px', 'color': '#3b82f6'}),
                "Warehouse Admin Dashboard"
            ], className="header-title"),
            html.Div([
                html.Span("Administrator", className="user-role"),
                html.Div([
                    html.I(className="fas fa-user-circle", style={'fontSize': '24px', 'color': '#6b7280'})
                ], className="user-avatar")
            ], className="user-info")
        ], className="header-content")
    ], className="header"),
    
    # Main Container
    html.Div([
        # Sidebar
        html.Div([
            html.Div([
                html.H3("Navigation", className="sidebar-title"),
                html.Div([
                    html.A([
                        html.I(className="fas fa-users"),
                        html.Span("User Management")
                    ], href="#", className="nav-item active"),
                    html.A([
                        html.I(className="fas fa-chart-bar"),
                        html.Span("Analytics")
                    ], href="#", className="nav-item"),
                    html.A([
                        html.I(className="fas fa-envelope"),
                        html.Span("Communications")
                    ], href="#", className="nav-item"),
                    html.A([
                        html.I(className="fas fa-cog"),
                        html.Span("Settings")
                    ], href="#", className="nav-item")
                ], className="nav-menu")
            ], className="sidebar-content")
        ], className="sidebar"),
        
        # Main Content
        html.Div([
            # Page Header
            html.Div([
                html.H2([
                    html.I(className="fas fa-users", style={'marginRight': '10px'}),
                    "User Management"
                ], className="page-title"),
                html.P("Manage and monitor all users in your warehouse system", className="page-subtitle")
            ], className="page-header"),
            
            # Analytics Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="card-icon"),
                        html.Div([
                            html.H3("0", id="total-users", className="card-number"),
                            html.P("Total Users", className="card-label")
                        ])
                    ], className="stats-card blue"),
                    html.Div([
                        html.I(className="card-icon"),
                        html.Div([
                            html.H3("0", id="active-users", className="card-number"),
                            html.P("Active Users", className="card-label")
                        ])
                    ], className="stats-card green"),
                    html.Div([
                        html.I(className="card-icon"),
                        html.Div([
                            html.H3("₦0", id="total-revenue", className="card-number"),
                            html.P("Total Revenue", className="card-label")
                        ])
                    ], className="stats-card purple"),
                    html.Div([
                        html.I(className="card-icon"),
                        html.Div([
                            html.H3("0", id="new-users", className="card-number"),
                            html.P("New This Month", className="card-label")
                        ])
                    ], className="stats-card orange")
                ], className="stats-grid")
            ], className="analytics-section"),
            
            # Charts Section
            html.Div([
                html.Div([
                    html.H4("User Analytics", className="section-title"),
                    html.Div([
                        html.Div([
                            dcc.Graph(id='user-status-chart')
                        ], className="chart-container"),
                        html.Div([
                            dcc.Graph(id='user-growth-chart')
                        ], className="chart-container")
                    ], className="charts-grid")
                ], className="charts-section")
            ]),
            
            # Action Buttons
            html.Div([
                html.Button([
                    html.I(className="fas fa-sync", style={'marginRight': '8px'}),
                    "Refresh Data"
                ], id="refresh-btn", className="btn btn-primary"),
                html.Button([
                    html.I(className="fas fa-envelope", style={'marginRight': '8px'}),
                    "Send Promotions"
                ], id="promotion-btn", className="btn btn-secondary"),
                html.Button([
                    html.I(className="fas fa-download", style={'marginRight': '8px'}),
                    "Export Users"
                ], id="export-btn", className="btn btn-success")
            ], className="action-buttons"),
            
            # User Table
            html.Div([
                html.H4("Users Directory", className="section-title"),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-search"),
                        dcc.Input(
                            id="search-input",
                            type="text",
                            placeholder="Search users...",
                            className="search-input"
                        )
                    ], className="search-box"),
                    html.Div([
                        html.Label("Filter by Status:", className="filter-label"),
                        dcc.Dropdown(
                            id="status-filter",
                            options=[
                                {'label': 'All Users', 'value': 'all'},
                                {'label': 'Active', 'value': 'active'},
                                {'label': 'Inactive', 'value': 'inactive'}
                            ],
                            value='all',
                            className="filter-dropdown"
                        )
                    ], className="filter-container")
                ], className="table-controls"),
                
                html.Div([
                    dash_table.DataTable(
                        id='users-table',
                        columns=[
                            {'name': 'ID', 'id': 'id', 'type': 'numeric', 'width': '60px'},
                            {'name': 'Username', 'id': 'username', 'type': 'text'},
                            {'name': 'Email', 'id': 'email', 'type': 'text'},
                            {'name': 'Role', 'id': 'role', 'type': 'text'},
                            {'name': 'Status', 'id': 'status', 'type': 'text'},
                            {'name': 'Bookings', 'id': 'total_bookings', 'type': 'numeric'},
                            {'name': 'Revenue', 'id': 'total_revenue', 'type': 'numeric', 'format': {'specifier': '₦,.2f'}},
                            {'name': 'Last Booking', 'id': 'last_booking_date', 'type': 'datetime'},
                            {'name': 'Actions', 'id': 'actions', 'presentation': 'markdown'}
                        ],
                        data=[],
                        style_cell={
                            'textAlign': 'left',
                            'fontFamily': 'Inter, sans-serif',
                            'fontSize': '14px',
                            'padding': '12px',
                            'backgroundColor': '#ffffff',
                            'border': '1px solid #e5e7eb'
                        },
                        style_header={
                            'backgroundColor': '#f8fafc',
                            'fontWeight': '600',
                            'color': '#374151',
                            'border': '1px solid #d1d5db'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f9fafb'
                            },
                            {
                                'if': {'filter_query': '{status} = inactive'},
                                'backgroundColor': '#fef2f2',
                                'color': '#991b1b'
                            },
                            {
                                'if': {'filter_query': '{status} = active'},
                                'backgroundColor': '#f0fdf4',
                                'color': '#166534'
                            }
                        ],
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
                        row_selectable="multi",
                        selected_rows=[],
                        page_action="native"
                    )
                ], className="table-container")
            ], className="users-table-section"),
            
            # User Details Modal
            html.Div([
                html.Div([
                    html.Div([
                        html.H4("User Details", className="modal-title"),
                        html.Button([
                            html.I(className="fas fa-times")
                        ], id="close-modal", className="modal-close")
                    ], className="modal-header"),
                    html.Div([
                        html.Div([
                            html.Label("Username:", className="form-label"),
                            dcc.Input(id="edit-username", type="text", className="form-input")
                        ], className="form-group"),
                        html.Div([
                            html.Label("Email:", className="form-label"),
                            dcc.Input(id="edit-email", type="email", className="form-input")
                        ], className="form-group"),
                        html.Div([
                            html.Label("Role:", className="form-label"),
                            dcc.Dropdown(
                                id="edit-role",
                                options=[
                                    {'label': 'Admin', 'value': 'admin'},
                                    {'label': 'Manager', 'value': 'manager'},
                                    {'label': 'Staff', 'value': 'staff'}
                                ],
                                className="form-dropdown"
                            )
                        ], className="form-group"),
                        html.Div([
                            html.Label("Status:", className="form-label"),
                            dcc.Dropdown(
                                id="edit-status",
                                options=[
                                    {'label': 'Active', 'value': 'active'},
                                    {'label': 'Inactive', 'value': 'inactive'}
                                ],
                                className="form-dropdown"
                            )
                        ], className="form-group")
                    ], className="modal-body"),
                    html.Div([
                        html.Button("Save Changes", id="save-user", className="btn btn-primary"),
                        html.Button("Cancel", id="cancel-edit", className="btn btn-secondary")
                    ], className="modal-footer")
                ], className="modal-content")
            ], id="user-modal", className="modal", style={'display': 'none'}),
            
            # Hidden div to store user data
            html.Div(id="selected-user-data", style={'display': 'none'})
            
        ], className="main-content")
    ], className="main-container"),
    
   
], style={'margin': 0, 'padding': 0})

# Callbacks
@app.callback(
    [Output('users-table', 'data'),
     Output('total-users', 'children'),
     Output('active-users', 'children'),
     Output('total-revenue', 'children'),
     Output('new-users', 'children'),
     Output('user-status-chart', 'figure'),
     Output('user-growth-chart', 'figure')],
    [Input('refresh-btn', 'n_clicks'),
     Input('search-input', 'value'),
     Input('status-filter', 'value')],
    prevent_initial_call=False
)
def update_dashboard(n_clicks, search_value, status_filter):
    # Get users data
    users_data = user_manager.get_all_users()
    analytics_data = user_manager.get_user_analytics()
    
    if not users_data:
        users_data = []
    
    # Filter users based on search and status
    filtered_users = users_data.copy()
    
    if search_value:
        filtered_users = [
            user for user in filtered_users 
            if search_value.lower() in user['username'].lower() or 
               search_value.lower() in user['email'].lower()
        ]
    
    if status_filter != 'all':
        filtered_users = [
            user for user in filtered_users 
            if user['status'] == status_filter
        ]
    
    # Prepare table data
    table_data = []
    for user in filtered_users:
        table_data.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'].title(),
            'status': user['status'].title(),
            'total_bookings': user['total_bookings'],
            'total_revenue': user['total_revenue'],
            'last_booking_date': user['last_booking_date'].strftime('%Y-%m-%d') if user['last_booking_date'] else 'Never',
            'actions': f'[Edit](#{user["id"]})'
        })
    
    # Calculate statistics
    total_users = len(users_data)
    active_users = len([u for u in users_data if u['status'] == 'active'])
    total_revenue = sum([u['total_revenue'] for u in users_data])
    
    # New users this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    new_users = len([
        u for u in users_data 
        if u['created_at'].month == current_month and u['created_at'].year == current_year
    ])
    
    # Create status distribution chart
    status_chart = go.Figure()
    if analytics_data['status_dist']:
        status_df = pd.DataFrame(analytics_data['status_dist'])
        status_chart = px.pie(
            status_df, 
            values='count', 
            names='status',
            title='User Status Distribution',
            color_discrete_map={'active': '#10b981', 'inactive': '#ef4444'}
        )
        status_chart.update_layout(
            font=dict(family="Inter, sans-serif"),
            title_font_size=16,
            title_font_color="#1f2937",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300
        )
    else:
        status_chart = go.Figure()
        status_chart.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        status_chart.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300
        )
    
    # Create user growth chart
    growth_chart = go.Figure()
    if analytics_data['monthly_users']:
        growth_df = pd.DataFrame(analytics_data['monthly_users'])
        growth_df['month_year'] = growth_df['year'].astype(str) + '-' + growth_df['month'].astype(str).str.zfill(2)
        
        growth_chart = px.line(
            growth_df,
            x='month_year',
            y='new_users',
            title='Monthly User Registration',
            markers=True
        )
        growth_chart.update_traces(
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8, color='#3b82f6')
        )
        growth_chart.update_layout(
            font=dict(family="Inter, sans-serif"),
            title_font_size=16,
            title_font_color="#1f2937",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            xaxis_title="Month",
            yaxis_title="New Users",
            xaxis=dict(gridcolor='#e5e7eb'),
            yaxis=dict(gridcolor='#e5e7eb')
        )
    else:
        growth_chart = go.Figure()
        growth_chart.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        growth_chart.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300
        )
    
    return (
        table_data,
        str(total_users),
        str(active_users),
        f"₦{total_revenue:,.2f}",
        str(new_users),
        status_chart,
        growth_chart
    )

@app.callback(
    [Output('user-modal', 'style'),
     Output('edit-username', 'value'),
     Output('edit-email', 'value'),
     Output('edit-role', 'value'),
     Output('edit-status', 'value'),
     Output('selected-user-data', 'children')],
    [Input('users-table', 'active_cell'),
     Input('close-modal', 'n_clicks'),
     Input('cancel-edit', 'n_clicks')],
    [State('users-table', 'data')],
    prevent_initial_call=True
)
def handle_user_modal(active_cell, close_clicks, cancel_clicks, table_data):
    triggered_id = ctx.triggered_id
    
    if triggered_id == 'close-modal' or triggered_id == 'cancel-edit':
        return {'display': 'none'}, '', '', '', '', ''
    
    if active_cell and active_cell['column_id'] == 'actions':
        row_index = active_cell['row']
        user_data = table_data[row_index]
        
        return (
            {'display': 'flex'},
            user_data['username'],
            user_data['email'],
            user_data['role'].lower(),
            user_data['status'].lower(),
            str(user_data['id'])
        )
    
    return {'display': 'none'}, '', '', '', '', ''

@app.callback(
    Output('users-table', 'data', allow_duplicate=True),
    [Input('save-user', 'n_clicks')],
    [State('selected-user-data', 'children'),
     State('edit-username', 'value'),
     State('edit-email', 'value'),
     State('edit-role', 'value'),
     State('edit-status', 'value'),
     State('users-table', 'data')],
    prevent_initial_call=True
)
def save_user_changes(n_clicks, user_id, username, email, role, status, current_data):
    if n_clicks and user_id:
        # Update user in database
        user_manager.update_user_info(int(user_id), username, email, role)
        user_manager.update_user_status(int(user_id), status)
        
        # Update the table data
        updated_data = current_data.copy()
        for i, row in enumerate(updated_data):
            if row['id'] == int(user_id):
                updated_data[i]['username'] = username
                updated_data[i]['email'] = email
                updated_data[i]['role'] = role.title()
                updated_data[i]['status'] = status.title()
                break
        
        return updated_data
    
    return current_data

@app.callback(
    Output('user-modal', 'style', allow_duplicate=True),
    Input('save-user', 'n_clicks'),
    prevent_initial_call=True
)
def close_modal_after_save(n_clicks):
    if n_clicks:
        return {'display': 'none'}
    return {'display': 'flex'}

class PromotionManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_active_users_for_promotion(self):
        query = """
        SELECT u.id, u.username, u.email, 
               COUNT(b.id) as booking_count,
               SUM(b.total_amount) as total_spent
        FROM users u
        LEFT JOIN bookings b ON u.id = b.user_id
        WHERE u.status = 'active'
        GROUP BY u.id, u.username, u.email
        ORDER BY total_spent DESC
        """
        return self.db.execute_query(query)
    
    def send_promotion_email(self, user_email, username, promotion_type):
        # Email configuration (you'll need to set up your SMTP settings)
        smtp_server = "smtp.gmail.com"  # Update with your SMTP server
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Update with your email
        sender_password = "your-app-password"  # Update with your app password
        
        # Create promotion content based on type
        promotion_content = {
            'discount': {
                'subject': 'Special Discount Just for You!',
                'body': f"""
                Dear {username},
                
                We're excited to offer you an exclusive 20% discount on your next storage booking!
                
                Use code: SAVE20 at checkout
                
                This offer is valid until the end of the month.
                
                Best regards,
                Warehouse Management Team
                """
            },
            'upgrade': {
                'subject': 'Upgrade Your Storage Experience',
                'body': f"""
                Dear {username},
                
                Based on your loyalty, we'd like to offer you a premium storage upgrade at no extra cost!
                
                Contact us to claim your upgrade.
                
                Best regards,
                Warehouse Management Team
                """
            },
            'welcome': {
                'subject': 'Welcome to Our Premium Storage Service',
                'body': f"""
                Dear {username},
                
                Welcome to our warehouse family! We're thrilled to have you on board.
                
                Enjoy your storage experience with us!
                
                Best regards,
                Warehouse Management Team
                """
            }
        }
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user_email
            msg['Subject'] = promotion_content[promotion_type]['subject']
            
            msg.attach(MIMEText(promotion_content[promotion_type]['body'], 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, user_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending error: {e}")
            return False

# Initialize promotion manager
promotion_manager = PromotionManager()

@app.callback(
    Output('promotion-btn', 'children'),
    Input('promotion-btn', 'n_clicks'),
    prevent_initial_call=True
)
def send_promotions(n_clicks):
    if n_clicks:
        # Get active users
        active_users = promotion_manager.get_active_users_for_promotion()
        
        success_count = 0
        for user in active_users:
            # Determine promotion type based on user behavior
            if user['total_spent'] > 1000:
                promotion_type = 'upgrade'
            elif user['booking_count'] > 5:
                promotion_type = 'discount'
            else:
                promotion_type = 'welcome'
            
            if promotion_manager.send_promotion_email(user['email'], user['username'], promotion_type):
                success_count += 1
        
        return [
            html.I(className="fas fa-check", style={'marginRight': '8px'}),
            f"Sent to {success_count} users"
        ]
    
    return [
        html.I(className="fas fa-envelope", style={'marginRight': '8px'}),
        "Send Promotions"
    ]

@app.callback(
    Output('export-btn', 'children'),
    Input('export-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_users(n_clicks):
    if n_clicks:
        # Get all users data
        users_data = user_manager.get_all_users()
        
        # Create DataFrame
        df = pd.DataFrame(users_data)
        
        # Generate CSV
        csv_string = df.to_csv(index=False)
        
        # You can save this to a file or return it as a download
        # For now, we'll just update the button text
        return [
            html.I(className="fas fa-check", style={'marginRight': '8px'}),
            "Export Complete"
        ]
    
    return [
        html.I(className="fas fa-download", style={'marginRight': '8px'}),
        "Export Users"
    ]

# Add interval component for auto-refresh
app.layout.children.append(
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    )
)

@app.callback(
    [Output('users-table', 'data', allow_duplicate=True),
     Output('total-users', 'children', allow_duplicate=True),
     Output('active-users', 'children', allow_duplicate=True),
     Output('total-revenue', 'children', allow_duplicate=True),
     Output('new-users', 'children', allow_duplicate=True)],
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def auto_refresh_data(n):
    # Get fresh data from database
    users_data = user_manager.get_all_users()
    
    if not users_data:
        return [], "0", "0", "₦0", "0"
    
    # Prepare table data
    table_data = []
    for user in users_data:
        table_data.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'].title(),
            'status': user['status'].title(),
            'total_bookings': user['total_bookings'],
            'total_revenue': user['total_revenue'],
            'last_booking_date': user['last_booking_date'].strftime('%Y-%m-%d') if user['last_booking_date'] else 'Never',
            'actions': f'[Edit](#{user["id"]})'
        })
    
    # Calculate statistics
    total_users = len(users_data)
    active_users = len([u for u in users_data if u['status'] == 'active'])
    total_revenue = sum([u['total_revenue'] for u in users_data])
    
    # New users this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    new_users = len([
        u for u in users_data 
        if u['created_at'].month == current_month and u['created_at'].year == current_year
    ])
    
    return (
        table_data,
        str(total_users),
        str(active_users),
        f"₦{total_revenue:,.2f}",
        str(new_users)
    )

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)