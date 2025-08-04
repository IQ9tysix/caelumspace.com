import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import hashlib
import uuid
from server import server
import secrets
from flask import session


app = Dash(
    __name__,
    server=server,
    url_base_pathname="/admin/complaints/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ]
)
# Initialize Dash app
app.title = "Warehouse Admin - Complaint Management"

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL password
    'database': 'warehouse_db',
    'charset': 'utf8mb4'
}

# Email configuration (update with your SMTP settings)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'your_email@gmail.com',  # Update with your email
    'password': 'your_app_password'   # Update with your app password
}

class ComplaintManager:
    def __init__(self):
        self.db_config = DB_CONFIG
        
    def get_db_connection(self):
        return pymysql.connect(**self.db_config)
    
    def get_complaint_stats(self):
        """Get complaint statistics for dashboard"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get basic stats
            stats = {}
            stat_queries = {
                'total': "SELECT COUNT(*) FROM complaints",
                'pending': "SELECT COUNT(*) FROM complaints WHERE status IN ('received', 'assigned', 'in_progress')",
                'resolved': "SELECT COUNT(*) FROM complaints WHERE status = 'resolved'",
                'closed': "SELECT COUNT(*) FROM complaints WHERE status = 'closed'",
                'high_priority': "SELECT COUNT(*) FROM complaints WHERE priority IN ('high', 'urgent')",
                'today': "SELECT COUNT(*) FROM complaints WHERE DATE(created_at) = CURDATE()",
                'this_week': "SELECT COUNT(*) FROM complaints WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            }
            
            for key, query in stat_queries.items():
                cursor.execute(query)
                stats[key] = cursor.fetchone()[0]
            
            return stats
        finally:
            conn.close()
    
    def get_complaints_data(self, status_filter=None, priority_filter=None, category_filter=None):
        """Get complaints data with optional filters"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
            base_query = """
                SELECT 
                    c.id, c.complaint_number, c.customer_name, c.customer_email,
                    cc.category_name, c.subject, c.priority, c.status,
                    c.created_at, c.updated_at, c.resolved_at,
                    COALESCE(cso.cso_name, 'Unassigned') as assigned_to_name,
                    DATEDIFF(COALESCE(c.resolved_at, NOW()), c.created_at) as days_open
                FROM complaints c
                LEFT JOIN complaint_categories cc ON c.category_id = cc.id
                LEFT JOIN cso_officers cso ON c.assigned_to = cso.cso_id
                WHERE 1=1
            """
            
            params = []
            if status_filter:
                base_query += " AND c.status = %s"
                params.append(status_filter)
            if priority_filter:
                base_query += " AND c.priority = %s"
                params.append(priority_filter)
            if category_filter:
                base_query += " AND cc.category_name = %s"
                params.append(category_filter)
            
            base_query += " ORDER BY c.created_at DESC LIMIT 100"
            
            cursor.execute(base_query, params)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            df = pd.DataFrame(data, columns=columns)
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['updated_at'] = pd.to_datetime(df['updated_at'])
                if 'resolved_at' in df.columns:
                    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
            
            return df
        finally:
            conn.close()
    
    def get_complaint_details(self, complaint_id):
        """Get detailed complaint information"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get complaint details
            cursor.execute("""
                SELECT 
                    c.*, cc.category_name, cso.cso_name as assigned_to_name,
                    b.customer_name as booking_customer, p.amount as payment_amount
                FROM complaints c
                LEFT JOIN complaint_categories cc ON c.category_id = cc.id
                LEFT JOIN cso_officers cso ON c.assigned_to = cso.cso_id
                LEFT JOIN bookings b ON c.booking_id = b.id
                LEFT JOIN payments p ON c.payment_id = p.id
                WHERE c.id = %s
            """, (complaint_id,))
            
            complaint = cursor.fetchone()
            if complaint:
                columns = [desc[0] for desc in cursor.description]
                complaint_dict = dict(zip(columns, complaint))
                
                # Get complaint updates
                cursor.execute("""
                    SELECT * FROM complaint_updates 
                    WHERE complaint_id = %s 
                    ORDER BY created_at DESC
                """, (complaint_id,))
                
                updates = cursor.fetchall()
                update_columns = [desc[0] for desc in cursor.description]
                updates_list = [dict(zip(update_columns, update)) for update in updates]
                
                complaint_dict['updates'] = updates_list
                return complaint_dict
            
            return None
        finally:
            conn.close()
    
    def update_complaint_status(self, complaint_id, new_status, message, admin_id, admin_name):
        """Update complaint status"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CALL UpdateComplaintStatus(%s, %s, %s, %s, %s)
            """, (complaint_id, new_status, message, admin_id, admin_name))
            
            conn.commit()
            
            # Send email notification
            self.send_status_update_email(complaint_id, new_status, message)
            
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating complaint: {e}")
            return False
        finally:
            conn.close()
    
    def send_status_update_email(self, complaint_id, new_status, message):
        """Send email notification to customer"""
        complaint = self.get_complaint_details(complaint_id)
        if not complaint:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['email']
            msg['To'] = complaint['customer_email']
            msg['Subject'] = f"Complaint Update - {complaint['complaint_number']}"
            
            body = f"""
            Dear {complaint['customer_name']},
            
            Your complaint #{complaint['complaint_number']} has been updated.
            
            Subject: {complaint['subject']}
            New Status: {new_status.replace('_', ' ').title()}
            
            Update Message:
            {message}
            
            You can track your complaint status by logging into your account.
            
            Best regards,
            Warehouse Management Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['email'], complaint['customer_email'], text)
            server.quit()
            
            # Update email sent status
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE complaint_updates 
                SET email_sent = 1, email_sent_at = NOW() 
                WHERE complaint_id = %s 
                ORDER BY created_at DESC LIMIT 1
            """, (complaint_id,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def get_analytics_data(self):
        """Get complaint analytics data"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Complaints by category
            cursor.execute("""
                SELECT cc.category_name, COUNT(*) as count
                FROM complaints c
                JOIN complaint_categories cc ON c.category_id = cc.id
                GROUP BY cc.category_name
                ORDER BY count DESC
            """)
            category_data = cursor.fetchall()
            
            # Complaints by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM complaints
                GROUP BY status
            """)
            status_data = cursor.fetchall()
            
            # Complaints by priority
            cursor.execute("""
                SELECT priority, COUNT(*) as count
                FROM complaints
                GROUP BY priority
                ORDER BY FIELD(priority, 'urgent', 'high', 'medium', 'low')
            """)
            priority_data = cursor.fetchall()
            
            # Complaints over time
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM complaints
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            time_data = cursor.fetchall()
            
            # Resolution time analysis
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN DATEDIFF(resolved_at, created_at) <= 1 THEN '0-1 days'
                        WHEN DATEDIFF(resolved_at, created_at) <= 3 THEN '2-3 days'
                        WHEN DATEDIFF(resolved_at, created_at) <= 7 THEN '4-7 days'
                        WHEN DATEDIFF(resolved_at, created_at) <= 14 THEN '8-14 days'
                        ELSE '15+ days'
                    END as resolution_time,
                    COUNT(*) as count
                FROM complaints
                WHERE resolved_at IS NOT NULL
                GROUP BY resolution_time
                ORDER BY FIELD(resolution_time, '0-1 days', '2-3 days', '4-7 days', '8-14 days', '15+ days')
            """)
            resolution_data = cursor.fetchall()
            
            return {
                'category': category_data,
                'status': status_data,
                'priority': priority_data,
                'time': time_data,
                'resolution': resolution_data
            }
        finally:
            conn.close()
    
    def get_admins_list(self):
        """Get list of CSO officers for assignment"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cso_id, cso_name 
                FROM cso_officers 
                WHERE is_active = 1
                ORDER BY cso_name
            """)
            return cursor.fetchall()
        finally:
            conn.close()
    
    def assign_complaint(self, complaint_id, assigned_to, admin_id, admin_name):
        """Assign complaint to an admin"""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CALL AssignComplaint(%s, %s, %s, %s)
            """, (complaint_id, assigned_to, admin_id, admin_name))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error assigning complaint: {e}")
            return False
        finally:
            conn.close()

# Initialize complaint manager
complaint_manager = ComplaintManager()

# App layout
app.layout = html.Div([
    # Header
    html.Header([
        html.Div([
            html.H1("Warehouse Management System", className="header-title"),
            html.Div([
                html.Span("Admin Dashboard", className="header-subtitle"),
                # html.Button("Logout", id="logout-btn", className="logout-btn")
                dbc.Button("Sign Out", href="/logout/", color="outline-danger", external_link=True)
            ], className="header-right")
        ], className="header-content")
    ], className="header"),
    
    # Main container
    html.Div([
        # Sidebar
        html.Div([
            html.Div([
                html.H3("Navigation", className="sidebar-title"),
                html.Ul([
                    html.Li([
                        html.A("📊 Dashboard", href="#", className="nav-link active", id="nav-dashboard")
                    ]),
                    html.Li([
                        html.A("📝 Complaints", href="#", className="nav-link", id="nav-complaints")
                    ]),
                    html.Li([
                        html.A("📈 Analytics", href="#", className="nav-link", id="nav-analytics")
                    ]),
                    html.Li([
                        html.A("👥 Admin Performance", href="#", className="nav-link", id="nav-performance")
                    ]),
                    html.Li([
                        html.A("⚙️ Settings", href="#", className="nav-link", id="nav-settings")
                    ])
                ], className="nav-list")
            ], className="sidebar-content")
        ], className="sidebar"),
        
        # Main content
        html.Div([
            # Dashboard content
            html.Div(id="main-content", children=[
                # Stats cards
                html.Div([
                    html.Div([
                        html.H3("0", id="total-complaints"),
                        html.P("Total Complaints")
                    ], className="stat-card total"),
                    
                    html.Div([
                        html.H3("0", id="pending-complaints"),
                        html.P("Pending")
                    ], className="stat-card pending"),
                    
                    html.Div([
                        html.H3("0", id="resolved-complaints"),
                        html.P("Resolved")
                    ], className="stat-card resolved"),
                    
                    html.Div([
                        html.H3("0", id="high-priority-complaints"),
                        html.P("High Priority")
                    ], className="stat-card urgent"),
                    
                    html.Div([
                        html.H3("0", id="today-complaints"),
                        html.P("Today")
                    ], className="stat-card today"),
                    
                    html.Div([
                        html.H3("0", id="week-complaints"),
                        html.P("This Week")
                    ], className="stat-card week")
                ], className="stats-grid"),
                
                # Charts section
                html.Div([
                    html.Div([
                        html.H3("Complaints by Category"),
                        dcc.Graph(id="category-chart")
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Complaints Over Time"),
                        dcc.Graph(id="time-chart")
                    ], className="chart-container")
                ], className="charts-row"),
                
                # Recent complaints table
                html.Div([
                    html.H3("Recent Complaints"),
                    html.Div([
                        html.Div([
                            html.Label("Filter by Status:"),
                            dcc.Dropdown(
                                id="status-filter",
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'Received', 'value': 'received'},
                                    {'label': 'Assigned', 'value': 'assigned'},
                                    {'label': 'In Progress', 'value': 'in_progress'},
                                    {'label': 'Pending Customer', 'value': 'pending_customer'},
                                    {'label': 'Resolved', 'value': 'resolved'},
                                    {'label': 'Closed', 'value': 'closed'}
                                ],
                                value='all',
                                className="filter-dropdown"
                            )
                        ], className="filter-group"),
                        
                        html.Div([
                            html.Label("Filter by Priority:"),
                            dcc.Dropdown(
                                id="priority-filter",
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'Low', 'value': 'low'},
                                    {'label': 'Medium', 'value': 'medium'},
                                    {'label': 'High', 'value': 'high'},
                                    {'label': 'Urgent', 'value': 'urgent'}
                                ],
                                value='all',
                                className="filter-dropdown"
                            )
                        ], className="filter-group"),
                        
                        html.Button("Refresh", id="refresh-btn", className="refresh-btn")
                    ], className="filters-row"),
                    
                    dash_table.DataTable(
                        id="complaints-table",
                        columns=[
                            {"name": "ID", "id": "complaint_number", "type": "text"},
                            {"name": "Customer", "id": "customer_name", "type": "text"},
                            {"name": "Category", "id": "category_name", "type": "text"},
                            {"name": "Subject", "id": "subject", "type": "text"},
                            {"name": "Priority", "id": "priority", "type": "text"},
                            {"name": "Status", "id": "status", "type": "text"},
                            {"name": "Assigned To", "id": "assigned_to_name", "type": "text"},
                            {"name": "Days Open", "id": "days_open", "type": "numeric"},
                            {"name": "Created", "id": "created_at", "type": "datetime"}
                        ],
                        data=[],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px',
                            'fontFamily': 'Arial',
                            'fontSize': '14px'
                        },
                        style_header={
                            'backgroundColor': '#2c3e50',
                            'color': 'white',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{priority} = urgent'},
                                'backgroundColor': '#ffebee',
                                'color': '#c62828'
                            },
                            {
                                'if': {'filter_query': '{priority} = high'},
                                'backgroundColor': '#fff3e0',
                                'color': '#ef6c00'
                            },
                            {
                                'if': {'filter_query': '{status} = resolved'},
                                'backgroundColor': '#e8f5e8',
                                'color': '#2e7d32'
                            }
                        ],
                        row_selectable="single",
                        selected_rows=[],
                        page_size=10,
                        sort_action="native",
                        filter_action="native"
                    )
                ], className="table-container")
            ])
        ], className="main-content")
    ], className="main-container"),
    
    # Complaint details modal
    html.Div([
        html.Div([
            html.Div([
                html.H2("Complaint Details", className="modal-title"),
                html.Button("×", id="close-modal", className="close-btn")
            ], className="modal-header"),
            
            html.Div([
                html.Div(id="complaint-details-content")
            ], className="modal-body"),
            
            html.Div([
                html.Button("Close", id="close-modal-btn", className="btn-secondary"),
                html.Button("Update Status", id="update-status-btn", className="btn-primary"),
                html.Button("Assign", id="assign-btn", className="btn-success")
            ], className="modal-footer")
        ], className="modal-content")
    ], id="complaint-modal", className="modal", style={"display": "none"}),
    
    # Status update modal
    html.Div([
        html.Div([
            html.Div([
                html.H3("Update Complaint Status"),
                html.Button("×", id="close-status-modal", className="close-btn")
            ], className="modal-header"),
            
            html.Div([
                html.Div([
                    html.Label("New Status:"),
                    dcc.Dropdown(
                        id="new-status-dropdown",
                        options=[
                            {'label': 'Received', 'value': 'received'},
                            {'label': 'Assigned', 'value': 'assigned'},
                            {'label': 'In Progress', 'value': 'in_progress'},
                            {'label': 'Pending Customer', 'value': 'pending_customer'},
                            {'label': 'Resolved', 'value': 'resolved'},
                            {'label': 'Closed', 'value': 'closed'}
                        ],
                        placeholder="Select new status"
                    )
                ], className="form-group"),
                
                html.Div([
                    html.Label("Update Message:"),
                    dcc.Textarea(
                        id="update-message",
                        placeholder="Enter update message for customer...",
                        style={'width': '100%', 'height': '100px'}
                    )
                ], className="form-group")
            ], className="modal-body"),
            
            html.Div([
                html.Button("Cancel", id="cancel-status-update", className="btn-secondary"),
                html.Button("Update", id="confirm-status-update", className="btn-primary")
            ], className="modal-footer")
        ], className="modal-content")
    ], id="status-update-modal", className="modal", style={"display": "none"}),
    
    # Assignment modal
    html.Div([
        html.Div([
            html.Div([
                html.H3("Assign Complaint"),
                html.Button("×", id="close-assign-modal", className="close-btn")
            ], className="modal-header"),
            
            html.Div([
                html.Div([
                    html.Label("Assign To:"),
                    dcc.Dropdown(
                        id="assign-to-dropdown",
                        placeholder="Select admin to assign"
                    )
                ], className="form-group")
            ], className="modal-body"),
            
            html.Div([
                html.Button("Cancel", id="cancel-assignment", className="btn-secondary"),
                html.Button("Assign", id="confirm-assignment", className="btn-primary")
            ], className="modal-footer")
        ], className="modal-content")
    ], id="assignment-modal", className="modal", style={"display": "none"}),
    
    # Hidden div to store selected complaint ID
    html.Div(id="selected-complaint-id", style={"display": "none"}),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id="interval-component",
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    ),
    
    # Store components for data
    dcc.Store(id="complaints-data-store"),
    dcc.Store(id="analytics-data-store")
], className="app-container")



# Callbacks

@app.callback(
    [Output('total-complaints', 'children'),
     Output('pending-complaints', 'children'),
     Output('resolved-complaints', 'children'),
     Output('high-priority-complaints', 'children'),
     Output('today-complaints', 'children'),
     Output('week-complaints', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_stats(n):
    stats = complaint_manager.get_complaint_stats()
    return (
        stats['total'],
        stats['pending'],
        stats['resolved'],
        stats['high_priority'],
        stats['today'],
        stats['this_week']
    )

@app.callback(
    Output('complaints-data-store', 'data'),
    [Input('interval-component', 'n_intervals'),
     Input('refresh-btn', 'n_clicks'),
     Input('status-filter', 'value'),
     Input('priority-filter', 'value')]
)
def update_complaints_data(n, refresh_clicks, status_filter, priority_filter):
    status = None if status_filter == 'all' else status_filter
    priority = None if priority_filter == 'all' else priority_filter
    
    df = complaint_manager.get_complaints_data(status, priority)
    return df.to_dict('records')

@app.callback(
    Output('complaints-table', 'data'),
    [Input('complaints-data-store', 'data')]
)
def update_complaints_table(data):
    if not data:
        return []
    
    # Format data for display
    formatted_data = []
    for row in data:
        formatted_row = row.copy()
        if 'created_at' in formatted_row and formatted_row['created_at']:
            formatted_row['created_at'] = pd.to_datetime(formatted_row['created_at']).strftime('%Y-%m-%d %H:%M')
        formatted_data.append(formatted_row)
    
    return formatted_data

@app.callback(
    [Output('category-chart', 'figure'),
     Output('time-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_charts(n):
    analytics_data = complaint_manager.get_analytics_data()
    
    # Category chart
    if analytics_data['category']:
        category_df = pd.DataFrame(analytics_data['category'], columns=['category_name', 'count'])
        category_fig = px.pie(
            category_df,
            values='count',
            names='category_name',
            title="",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        category_fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
    else:
        category_fig = {}
    
    # Time chart
    if analytics_data['time']:
        time_df = pd.DataFrame(analytics_data['time'], columns=['date', 'count'])
        time_fig = px.line(
            time_df,
            x='date',
            y='count',
            title="",
            markers=True
        )
        time_fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Number of Complaints"
        )
    else:
        time_fig = {}
    
    return category_fig, time_fig

@app.callback(
    [Output('complaint-modal', 'style'),
     Output('complaint-details-content', 'children'),
     Output('selected-complaint-id', 'children')],
    [Input('complaints-table', 'selected_rows'),
     Input('close-modal', 'n_clicks'),
     Input('close-modal-btn', 'n_clicks')],
    [State('complaints-table', 'data'),
     State('complaint-modal', 'style')]
)
def handle_complaint_modal(selected_rows, close1, close2, table_data, modal_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "none"}, "", ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ['close-modal', 'close-modal-btn']:
        return {"display": "none"}, "", ""
    
    if trigger_id == 'complaints-table' and selected_rows:
        selected_row = table_data[selected_rows[0]]
        complaint_id = selected_row['id']
        
        # Get detailed complaint info
        complaint_details = complaint_manager.get_complaint_details(complaint_id)
        
        if complaint_details:
            details_content = html.Div([
                html.Div([
                    html.H4(f"Complaint #{complaint_details['complaint_number']}"),
                    html.P(f"Status: {complaint_details['status'].replace('_', ' ').title()}", className="status-badge"),
                    html.P(f"Priority: {complaint_details['priority'].title()}", className="priority-badge")
                ], className="complaint-header"),
                
                html.Div([
                    html.H5("Customer Information"),
                    html.P(f"Name: {complaint_details['customer_name']}"),
                    html.P(f"Email: {complaint_details['customer_email']}"),
                    html.P(f"Phone: {complaint_details.get('customer_phone', 'N/A')}")
                ], className="info-section"),
                
                html.Div([
                    html.H5("Complaint Details"),
                    html.P(f"Category: {complaint_details['category_name']}"),
                    html.P(f"Subject: {complaint_details['subject']}"),
                    html.P(f"Description: {complaint_details['description']}"),
                    html.P(f"Assigned To: {complaint_details.get('assigned_to_name', 'Unassigned')}")
                ], className="info-section"),
                
                html.Div([
                    html.H5("Timeline & Updates"),
                    html.Div([
                        html.Div([
                            html.Strong(f"{update['update_type'].replace('_', ' ').title()}"),
                            html.P(update['message'] if update['message'] else 'No message'),
                            html.Small(f"By: {update['created_by_name']} on {update['created_at']}")
                        ], className="update-item") for update in complaint_details.get('updates', [])
                    ], className="updates-list")
                ], className="info-section")
            ])
            
            return {"display": "flex"}, details_content, str(complaint_id)
    
    return {"display": "none"}, "", ""

@app.callback(
    Output('status-update-modal', 'style'),
    [Input('update-status-btn', 'n_clicks'),
     Input('close-status-modal', 'n_clicks'),
     Input('cancel-status-update', 'n_clicks'),
     Input('confirm-status-update', 'n_clicks')],
    [State('selected-complaint-id', 'children'),
     State('new-status-dropdown', 'value'),
     State('update-message', 'value')]
)
def handle_status_update_modal(open_btn, close1, close2, confirm_btn, complaint_id, new_status, message):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "none"}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'update-status-btn':
        return {"display": "flex"}
    
    if trigger_id in ['close-status-modal', 'cancel-status-update']:
        return {"display": "none"}
    
    if trigger_id == 'confirm-status-update' and complaint_id and new_status:
        # Update the complaint status
        success = complaint_manager.update_complaint_status(
            int(complaint_id), new_status, message or "Status updated", 1, "Admin"
        )
        
        if success:
            return {"display": "none"}
    
    return {"display": "none"}

@app.callback(
    [Output('assignment-modal', 'style'),
     Output('assign-to-dropdown', 'options')],
    [Input('assign-btn', 'n_clicks'),
     Input('close-assign-modal', 'n_clicks'),
     Input('cancel-assignment', 'n_clicks'),
     Input('confirm-assignment', 'n_clicks')],
    [State('selected-complaint-id', 'children'),
     State('assign-to-dropdown', 'value')]
)
def handle_assignment_modal(open_btn, close1, close2, confirm_btn, complaint_id, assigned_to):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "none"}, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Get admin options
    admins = complaint_manager.get_admins_list()
    admin_options = [{'label': admin[1], 'value': admin[0]} for admin in admins]
    
    if trigger_id == 'assign-btn':
        return {"display": "flex"}, admin_options
    
    if trigger_id in ['close-assign-modal', 'cancel-assignment']:
        return {"display": "none"}, admin_options
    
    if trigger_id == 'confirm-assignment' and complaint_id and assigned_to:
        # Assign the complaint
        success = complaint_manager.assign_complaint(
            int(complaint_id), assigned_to, 1, "Admin"
        )
        
        if success:
            return {"display": "none"}, admin_options
    
    return {"display": "none"}, admin_options

