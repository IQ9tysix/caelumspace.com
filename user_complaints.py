import dash
from dash import Dash, dcc, html, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta
import hashlib
import secrets
import re
import os
from flask import session
import logging
import urllib.parse
from flask import session as flask_session
import mysql.connector
from mysql.connector import Error
import json

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/user_complaints/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
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
            /* Sidebar Styles */
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                height: 100vh;
                width: 250px;
                background: #2c3e50;
                color: white;
                transition: transform 0.3s ease;
                z-index: 1000;
                overflow-y: auto;
            }
            .sidebar.hidden {
                transform: translateX(-100%);
            }
            .sidebar-header {
                padding: 20px;
                background: #34495e;
                border-bottom: 1px solid #3498db;
            }
            .sidebar-menu {
                padding: 0;
                list-style: none;
            }
            .sidebar-menu li {
                border-bottom: 1px solid #34495e;
            }
            .sidebar-menu li a {
                display: block;
                padding: 15px 20px;
                color: white;
                text-decoration: none;
                transition: background 0.3s;
            }
            .sidebar-menu li a:hover, .sidebar-menu li a.active {
                background: #3498db;
                color: white;
            }
            
            /* Main Content */
            .main-content {
                margin-left: 250px;
                transition: margin-left 0.3s ease;
                min-height: 100vh;
            }
            .main-content.expanded {
                margin-left: 0;
            }
            
            /* Header */
            .header {
                background: white;
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header-left {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .header-right {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .profile-section {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .profile-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #3498db;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }
            .profile-info {
                display: flex;
                flex-direction: column;
            }
            .profile-name {
                font-weight: 600;
                font-size: 14px;
            }
            .profile-type {
                font-size: 12px;
                color: #666;
            }
            
            /* Notification dropdown */
            .notification-dropdown {
                max-height: 300px;
                overflow-y: auto;
            }
            
            /* Summary Cards */
            .summary-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .summary-card h4 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .summary-card .value {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
            
            /* Complaint Cards */
            .complaint-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 15px;
                border-left: 4px solid #3498db;
            }
            .complaint-card.high-priority {
                border-left-color: #e74c3c;
            }
            .complaint-card.urgent-priority {
                border-left-color: #c0392b;
            }
            
            /* Status badges */
            .status-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .status-received { background: #f39c12; color: white; }
            .status-assigned { background: #3498db; color: white; }
            .status-in_progress { background: #9b59b6; color: white; }
            .status-pending_customer { background: #e67e22; color: white; }
            .status-resolved { background: #27ae60; color: white; }
            .status-closed { background: #95a5a6; color: white; }
            
            /* Priority badges */
            .priority-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .priority-low { background: #bdc3c7; color: #2c3e50; }
            .priority-medium { background: #f39c12; color: white; }
            .priority-high { background: #e74c3c; color: white; }
            .priority-urgent { background: #c0392b; color: white; }
            
            /* Fixed complaint button */
            .fixed-complaint-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 999;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .sidebar {
                    transform: translateX(-100%);
                }
                .main-content {
                    margin-left: 0;
                }
                .profile-info {
                    display: none;
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

app.title = "User Complaints Dashboard"

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='warehouse_db',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Generate complaint number
def generate_complaint_number():
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()
    return f"CMP-{timestamp}-{random_part}"

# Get user bookings
def get_user_bookings(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT id, booking_reference, unit_id, start_date, end_date, 
               status, total_amount
        FROM bookings 
        WHERE user_id = %s AND status IN ('active', 'confirmed', 'pending')
        ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        bookings = cursor.fetchall()
        return bookings
    except Error as e:
        logging.error(f"Error fetching bookings: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get user complaints
def get_user_complaints(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT c.*, cc.category_name,
               COALESCE(b.booking_reference, 'N/A') as booking_reference,
               COALESCE(p.payment_reference, 'N/A') as payment_reference,
               DATEDIFF(COALESCE(c.resolved_at, NOW()), c.created_at) as days_open
        FROM complaints c
        LEFT JOIN complaint_categories cc ON c.category_id = cc.id
        LEFT JOIN bookings b ON c.booking_id = b.id
        LEFT JOIN payments p ON c.payment_id = p.id
        WHERE c.user_id = %s
        ORDER BY c.created_at DESC
        """
        cursor.execute(query, (user_id,))
        complaints = cursor.fetchall()
        return complaints
    except Error as e:
        logging.error(f"Error fetching complaints: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get complaint categories
def get_complaint_categories():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, category_name FROM complaint_categories WHERE is_active = 1"
        cursor.execute(query)
        categories = cursor.fetchall()
        return categories
    except Error as e:
        logging.error(f"Error fetching categories: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Create complaint
def create_complaint(user_id, customer_name, customer_email, customer_phone, 
                    category_id, subject, description, priority, booking_id=None):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        complaint_number = generate_complaint_number()
        
        query = """
        INSERT INTO complaints (complaint_number, user_id, customer_name, 
                              customer_email, customer_phone, category_id, 
                              subject, description, priority, booking_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (complaint_number, user_id, customer_name, 
                             customer_email, customer_phone, category_id, 
                             subject, description, priority, booking_id))
        
        complaint_id = cursor.lastrowid
        
        # Add initial update record
        update_query = """
        INSERT INTO complaint_updates (complaint_id, update_type, new_status, 
                                     message, created_by_name)
        VALUES (%s, 'system_update', 'received', 'Complaint submitted by customer', %s)
        """
        cursor.execute(update_query, (complaint_id, customer_name))
        
        conn.commit()
        return True, complaint_number
    except Error as e:
        logging.error(f"Error creating complaint: {e}")
        return False, str(e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Main layout
def create_layout(user_data):
    # Get user's first and last name initials
    name_parts = user_data.get('full_name', 'U U').split()
    initials = ''.join([part[0].upper() for part in name_parts[:2]]) if len(name_parts) >= 2 else name_parts[0][0].upper() if name_parts else 'U'
    
    return html.Div([
        # Sidebar
        html.Div([
            html.Div([
                html.H4("Storage Dashboard", className="mb-0"),
                html.Small("User Panel", className="text-muted")
            ], className="sidebar-header"),
            
            html.Ul([
                html.Li([html.A([html.I(className="fas fa-home me-2"), "Home"], href="#", className="")]),
                html.Li([html.A([html.I(className="fas fa-calendar me-2"), "Book Unit"], href="#")]),
                html.Li([html.A([html.I(className="fas fa-list me-2"), "Manage Bookings"], href="#")]),
                html.Li([html.A([html.I(className="fas fa-exclamation-triangle me-2"), "Complaints"], href="#", className="active")]),
                html.Li([html.A([html.I(className="fas fa-credit-card me-2"), "Payment & Invoice"], href="#")]),
                html.Li([html.A([html.I(className="fas fa-cog me-2"), "Settings"], href="#")]),
                html.Li([html.A([html.I(className="fas fa-user me-2"), "Profile"], href="#")]),
                html.Li([html.A([html.I(className="fas fa-sign-out-alt me-2"), "Logout"], href="#")]),
            ], className="sidebar-menu")
        ], id="sidebar", className="sidebar"),
        
        # Main content
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.Button([
                        html.I(className="fas fa-bars")
                    ], id="sidebar-toggle", className="btn btn-light me-3"),
                    html.H5("Complaints & Disputes", className="mb-0")
                ], className="header-left"),
                
                html.Div([
                    # Notifications
                    dbc.DropdownMenu([
                        dbc.DropdownMenuItem("No new notifications", disabled=True),
                    ], label=html.I(className="fas fa-bell"), 
                       color="light", className="me-2"),
                    
                    # Profile section
                    html.Div([
                        html.Div(initials, className="profile-avatar"),
                        html.Div([
                            html.Div(user_data.get('full_name', 'Unknown User'), className="profile-name"),
                            html.Div(user_data.get('user_type', 'individual').title(), className="profile-type")
                        ], className="profile-info"),
                    ], className="profile-section me-3"),
                    
                    # Settings
                    html.Button([
                        html.I(className="fas fa-cog")
                    ], className="btn btn-light me-2"),
                    
                    # Logout
                    html.Button([
                        html.I(className="fas fa-sign-out-alt")
                    ], className="btn btn-outline-danger"),
                    
                ], className="header-right")
            ], className="header"),
            
            # Page content
            html.Div([
                # Summary cards or fixed button will be loaded here
                html.Div(id="complaint-summary-section"),
                
                # Complaints list
                html.Div(id="complaints-list"),
                
                # Fixed complaint button (shown when no bookings)
                html.Div(id="fixed-complaint-button"),
                
            ], className="p-4"),
            
        ], id="main-content", className="main-content"),
        
        # Complaint Modal
        dbc.Modal([
            dbc.ModalHeader("Submit New Complaint"),
            dbc.ModalBody([
                dbc.Form([
                    # Category
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Category *"),
                            dcc.Dropdown(
                                id="complaint-category",
                                placeholder="Select complaint category...",
                                className="mb-3"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Priority *"),
                            dcc.Dropdown(
                                id="complaint-priority",
                                options=[
                                    {"label": "Low", "value": "low"},
                                    {"label": "Medium", "value": "medium"},
                                    {"label": "High", "value": "high"},
                                    {"label": "Urgent", "value": "urgent"}
                                ],
                                value="medium",
                                className="mb-3"
                            )
                        ], width=6)
                    ]),
                    
                    # Subject
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Subject *"),
                            dbc.Input(
                                id="complaint-subject",
                                placeholder="Brief description of the issue...",
                                className="mb-3"
                            )
                        ])
                    ]),
                    
                    # Link to booking
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Link to Booking (Optional)"),
                            dcc.Dropdown(
                                id="complaint-booking",
                                placeholder="Select a booking to link (optional)...",
                                className="mb-3"
                            )
                        ])
                    ]),
                    
                    # Description
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Detailed Description *"),
                            dbc.Textarea(
                                id="complaint-description",
                                placeholder="Please provide detailed information about your complaint...",
                                style={"minHeight": "120px"},
                                className="mb-3"
                            )
                        ])
                    ]),
                    
                    # Contact info
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Phone Number (Optional)"),
                            dbc.Input(
                                id="complaint-phone",
                                placeholder="Your phone number...",
                                className="mb-3"
                            )
                        ])
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-complaint", className="me-2", color="secondary"),
                dbc.Button("Submit Complaint", id="submit-complaint", color="primary")
            ])
        ], id="complaint-modal", size="lg"),
        
        # Complaint Detail Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.Div(id="complaint-detail-header")
            ]),
            dbc.ModalBody([
                html.Div(id="complaint-detail-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-detail-modal", color="secondary")
            ])
        ], id="complaint-detail-modal", size="xl"),
        
        # Store user data and other states
        dcc.Store(id="user-data", data=user_data),
        dcc.Store(id="user-bookings", data=[]),
        dcc.Store(id="complaint-categories", data=[]),
        dcc.Store(id="user-complaints", data=[]),
        
        # Interval for auto-refresh
        dcc.Interval(id="refresh-interval", interval=30000, n_intervals=0),
        
        # Alert for notifications
        html.Div(id="alert-container", className="position-fixed", 
                style={"top": "20px", "right": "20px", "zIndex": "9999"})
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='content')
])

# Sidebar toggle callback
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('main-content');
            
            if (sidebar.classList.contains('hidden')) {
                sidebar.classList.remove('hidden');
                mainContent.classList.remove('expanded');
            } else {
                sidebar.classList.add('hidden');
                mainContent.classList.add('expanded');
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('sidebar', 'className'),
    Input('sidebar-toggle', 'n_clicks'),
    prevent_initial_call=True
)

@app.callback(
    Output('content', 'children'),
    Input('url', 'href')
)
def render_content(href):
    if not href:
        return html.Div("Invalid access. No token.")
    
    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)
    token = params.get('token', [None])[0]
    
    if not token:
        return html.Div("Missing token. Please log in.")
    
    # Validate token
    ok, data = verify_session_token(token)
    if not ok:
        return html.Div("Session expired or invalid. Please log in.")
    
    return create_layout(data)

# Load initial data
@app.callback(
    [Output('user-bookings', 'data'),
     Output('complaint-categories', 'data'),
     Output('user-complaints', 'data')],
    Input('url', 'href'),
    State('user-data', 'data')
)
def load_initial_data(href, user_data):
    if not user_data:
        return [], [], []
    
    user_id = user_data.get('user_id')
    if not user_id:
        return [], [], []
    
    bookings = get_user_bookings(user_id)
    categories = get_complaint_categories()
    complaints = get_user_complaints(user_id)
    
    return bookings, categories, complaints

# Update dropdown options
@app.callback(
    [Output('complaint-category', 'options'),
     Output('complaint-booking', 'options')],
    [Input('complaint-categories', 'data'),
     Input('user-bookings', 'data')]
)
def update_dropdown_options(categories, bookings):
    category_options = [
        {"label": cat['category_name'], "value": cat['id']} 
        for cat in categories
    ]
    
    booking_options = [
        {"label": f"Booking #{booking['booking_reference']} - Unit {booking['unit_id']}", 
         "value": booking['id']} 
        for booking in bookings
    ]
    
    return category_options, booking_options

# Render summary section
@app.callback(
    Output('complaint-summary-section', 'children'),
    [Input('user-bookings', 'data'),
     Input('user-complaints', 'data')]
)
def render_summary_section(bookings, complaints):
    if not bookings:
        return html.Div()  # Will show fixed button instead
    
    # Calculate summary statistics
    total_complaints = len(complaints)
    open_complaints = len([c for c in complaints if c['status'] not in ['resolved', 'closed']])
    urgent_complaints = len([c for c in complaints if c['priority'] == 'urgent'])
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Total Complaints"),
                html.Div(str(total_complaints), className="value")
            ], className="summary-card")
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4("Open Complaints"),
                html.Div(str(open_complaints), className="value")
            ], className="summary-card")
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4("Urgent Issues"),
                html.Div(str(urgent_complaints), className="value")
            ], className="summary-card")
        ], width=3),
        dbc.Col([
            html.Div([
                html.H4("Active Bookings"),
                html.Div(str(len(bookings)), className="value")
            ], className="summary-card")
        ], width=3)
    ], className="mb-4")

# Render fixed complaint button
@app.callback(
    Output('fixed-complaint-button', 'children'),
    Input('user-bookings', 'data')
)
def render_fixed_button(bookings):
    if bookings:
        return html.Div()  # No fixed button if user has bookings
    
    return html.Button([
        html.I(className="fas fa-plus me-2"),
        "Open Dispute"
    ], id="open-dispute-btn", className="btn btn-primary btn-lg fixed-complaint-btn")

# Render complaints list
@app.callback(
    Output('complaints-list', 'children'),
    [Input('user-complaints', 'data'),
     Input('user-bookings', 'data')]
)
def render_complaints_list(complaints, bookings):
    if not complaints:
        return html.Div([
            html.Div([
                html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
                html.H4("No Complaints Yet", className="text-muted"),
                html.P("You haven't submitted any complaints or disputes.", className="text-muted mb-3"),
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Submit Your First Complaint"
                ], id="first-complaint-btn", color="primary", size="lg")
            ], className="text-center py-5")
        ])
    
    complaint_cards = []
    for complaint in complaints:
        status_class = f"status-{complaint['status']}"
        priority_class = f"priority-{complaint['priority']}"
        card_class = "complaint-card"
        
        if complaint['priority'] in ['high', 'urgent']:
            card_class += f" {complaint['priority']}-priority"
        
        complaint_cards.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.H5([
                            complaint['subject'],
                            html.Span(complaint['complaint_number'], 
                                    className="text-muted ms-2", style={"fontSize": "14px"})
                        ]),
                        html.Div([
                            html.Span(complaint['status'].replace('_', ' ').title(), 
                                    className=f"status-badge {status_class} me-2"),
                            html.Span(complaint['priority'].title(), 
                                    className=f"priority-badge {priority_class}")
                        ], className="mb-2"),
                        html.P(complaint['description'][:150] + "..." if len(complaint['description']) > 150 else complaint['description'],
                               className="text-muted mb-2"),
                        html.Div([
                            html.Small([
                                html.Strong("Category: "), complaint['category_name']
                            ], className="me-3"),
                            html.Small([
                                html.Strong("Created: "), 
                                complaint['created_at'].strftime("%Y-%m-%d %H:%M") if complaint['created_at'] else "Unknown"
                            ], className="me-3"),
                            html.Small([
                                html.Strong("Days Open: "), str(complaint.get('days_open', 0))
                            ])
                        ])
                    ], style={"flex": "1"}),
                    html.Div([
                        dbc.Button("View Details", 
                                 id={"type": "view-complaint", "index": complaint['id']},
                                 color="primary", size="sm", className="me-2"),
                        dbc.Button("Update", 
                                 id={"type": "update-complaint", "index": complaint['id']},
                                 color="outline-secondary", size="sm")
                    ], style={"alignSelf": "flex-start"})
                ], style={"display": "flex", "justifyContent": "space-between"})
            ], className=card_class, id=f"complaint-{complaint['id']}")
        )
    
    return html.Div([
        html.Div([
            html.H4("Your Complaints & Disputes"),
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "New Complaint"
            ], id="new-complaint-btn", color="primary", className="mb-3")
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),
        html.Div(complaint_cards)
    ])

# Modal control callbacks
@app.callback(
    Output('complaint-modal', 'is_open'),
    [Input('open-dispute-btn', 'n_clicks'),
     Input('first-complaint-btn', 'n_clicks'),
     Input('new-complaint-btn', 'n_clicks'),
     Input('cancel-complaint', 'n_clicks'),
     Input('submit-complaint', 'n_clicks')],
    State('complaint-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_complaint_modal(dispute_btn, first_btn, new_btn, cancel_btn, submit_btn, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id in ['open-dispute-btn', 'first-complaint-btn', 'new-complaint-btn']:
        return True
    elif button_id in ['cancel-complaint']:
        return False
    elif button_id == 'submit-complaint':
        return False  # Will be handled by submit callback
    
    return is_open

# Submit complaint callback
@app.callback(
    [Output('alert-container', 'children'),
     Output('complaint-subject', 'value'),
     Output('complaint-description', 'value'),
     Output('complaint-phone', 'value'),
     Output('complaint-category', 'value'),
     Output('complaint-priority', 'value'),
     Output('complaint-booking', 'value')],
    Input('submit-complaint', 'n_clicks'),
    [State('complaint-category', 'value'),
     State('complaint-subject', 'value'),
     State('complaint-description', 'value'),
     State('complaint-priority', 'value'),
     State('complaint-booking', 'value'),
     State('complaint-phone', 'value'),
     State('user-data', 'data')],
    prevent_initial_call=True
)
def submit_complaint(n_clicks, category_id, subject, description, priority, booking_id, phone, user_data):
    if not n_clicks or not user_data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Validation
    if not category_id or not subject or not description:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all required fields (Category, Subject, Description)."
        ], color="danger", dismissable=True, duration=5000)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Submit complaint
    success, result = create_complaint(
        user_data['user_id'],
        user_data.get('full_name', 'Unknown User'),
        user_data['email'],
        phone or '',
        category_id,
        subject,
        description,
        priority,
        booking_id if booking_id else None
    )
    
    if success:
        alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Complaint submitted successfully! Reference number: {result}"
        ], color="success", dismissable=True, duration=5000)
        # Clear form
        return alert, "", "", "", None, "medium", None
    else:
        alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error submitting complaint: {result}"
        ], color="danger", dismissable=True, duration=5000)
        return alert, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# View complaint details callback
@app.callback(
    [Output('complaint-detail-modal', 'is_open'),
     Output('complaint-detail-header', 'children'),
     Output('complaint-detail-content', 'children')],
    [Input({'type': 'view-complaint', 'index': dash.ALL}, 'n_clicks'),
     Input('close-detail-modal', 'n_clicks')],
    [State('user-complaints', 'data'),
     State('complaint-detail-modal', 'is_open')],
    prevent_initial_call=True
)
def view_complaint_details(view_clicks, close_click, complaints, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", ""
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if 'close-detail-modal' in trigger_id:
        return False, "", ""
    
    # Find which complaint was clicked
    if view_clicks and any(view_clicks):
        clicked_idx = None
        for i, clicks in enumerate(view_clicks):
            if clicks:
                clicked_idx = i
                break
        
        if clicked_idx is not None:
            complaint_id = ctx.triggered[0]['prop_id'].split('"index":')[1].split('}')[0]
            complaint_id = int(complaint_id)
            
            # Find the complaint
            complaint = next((c for c in complaints if c['id'] == complaint_id), None)
            if complaint:
                return True, create_complaint_detail_header(complaint), create_complaint_detail_content(complaint)
    
    return is_open, dash.no_update, dash.no_update

def create_complaint_detail_header(complaint):
    status_class = f"status-{complaint['status']}"
    priority_class = f"priority-{complaint['priority']}"
    
    return html.Div([
        html.Div([
            html.H4(complaint['subject'], className="mb-0"),
            html.Small(f"#{complaint['complaint_number']}", className="text-muted")
        ]),
        html.Div([
            html.Span(complaint['status'].replace('_', ' ').title(), 
                    className=f"status-badge {status_class} me-2"),
            html.Span(complaint['priority'].title(), 
                    className=f"priority-badge {priority_class}")
        ])
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})

def create_complaint_detail_content(complaint):
    # Get complaint updates
    updates = get_complaint_updates(complaint['id'])
    
    return html.Div([
        # Basic Information
        dbc.Card([
            dbc.CardHeader("Complaint Information"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Strong("Category: "), complaint['category_name']
                    ], width=4),
                    dbc.Col([
                        html.Strong("Priority: "), complaint['priority'].title()
                    ], width=4),
                    dbc.Col([
                        html.Strong("Status: "), complaint['status'].replace('_', ' ').title()
                    ], width=4)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Strong("Created: "), 
                        complaint['created_at'].strftime("%Y-%m-%d %H:%M") if complaint['created_at'] else "Unknown"
                    ], width=4),
                    dbc.Col([
                        html.Strong("Updated: "), 
                        complaint['updated_at'].strftime("%Y-%m-%d %H:%M") if complaint['updated_at'] else "Unknown"
                    ], width=4),
                    dbc.Col([
                        html.Strong("Days Open: "), str(complaint.get('days_open', 0))
                    ], width=4)
                ], className="mb-3"),
                html.Hr(),
                html.H6("Description:"),
                html.P(complaint['description'])
            ])
        ], className="mb-3"),
        
        # Linked Information
        dbc.Card([
            dbc.CardHeader("Linked Information"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Strong("Booking Reference: "), 
                        complaint.get('booking_reference', 'Not linked')
                    ], width=6),
                    dbc.Col([
                        html.Strong("Payment Reference: "), 
                        complaint.get('payment_reference', 'Not linked')
                    ], width=6)
                ])
            ])
        ], className="mb-3"),
        
        # Updates Timeline
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    "Updates & Timeline",
                    html.Span(f"({len(updates)} updates)", className="text-muted ms-2")
                ])
            ]),
            dbc.CardBody([
                create_updates_timeline(updates) if updates else html.P("No updates available.", className="text-muted")
            ])
        ], className="mb-3"),
        
        # Customer Response Section
        dbc.Card([
            dbc.CardHeader("Add Response"),
            dbc.CardBody([
                dbc.Textarea(
                    id=f"response-text-{complaint['id']}",
                    placeholder="Add your response or additional information...",
                    style={"minHeight": "100px"},
                    className="mb-3"
                ),
                dbc.Button([
                    html.I(className="fas fa-reply me-2"),
                    "Add Response"
                ], id=f"add-response-{complaint['id']}", color="primary")
            ])
        ])
    ])

def get_complaint_updates(complaint_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT * FROM complaint_updates 
        WHERE complaint_id = %s AND is_customer_visible = 1
        ORDER BY created_at DESC
        """
        cursor.execute(query, (complaint_id,))
        updates = cursor.fetchall()
        return updates
    except Error as e:
        logging.error(f"Error fetching complaint updates: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_updates_timeline(updates):
    timeline_items = []
    
    for update in updates:
        icon_class = "fas fa-info-circle"
        color_class = "text-primary"
        
        if update['update_type'] == 'status_change':
            icon_class = "fas fa-exchange-alt"
            color_class = "text-warning"
        elif update['update_type'] == 'assignment':
            icon_class = "fas fa-user-check"
            color_class = "text-info"
        elif update['update_type'] == 'customer_response':
            icon_class = "fas fa-comment"
            color_class = "text-success"
        
        timeline_items.append(
            html.Div([
                html.Div([
                    html.I(className=f"{icon_class} {color_class}")
                ], className="timeline-icon"),
                html.Div([
                    html.Div([
                        html.Strong(update['update_type'].replace('_', ' ').title()),
                        html.Span(
                            update['created_at'].strftime("%Y-%m-%d %H:%M") if update['created_at'] else "Unknown",
                            className="text-muted ms-2"
                        )
                    ]),
                    html.P(update['message'] if update['message'] else "No message", className="mb-1"),
                    html.Small(f"By: {update['created_by_name'] or 'System'}", className="text-muted")
                ], className="timeline-content")
            ], className="timeline-item mb-3")
        )
    
    return html.Div(timeline_items, className="timeline")

# Refresh data callback
@app.callback(
    Output('user-complaints', 'data', allow_duplicate=True),
    Input('refresh-interval', 'n_intervals'),
    State('user-data', 'data'),
    prevent_initial_call=True
)
def refresh_complaints(n_intervals, user_data):
    if not user_data:
        return dash.no_update
    
    user_id = user_data.get('user_id')
    if not user_id:
        return dash.no_update
    
    return get_user_complaints(user_id)

# Update complaint status (for customer responses)
@app.callback(
    Output('alert-container', 'children', allow_duplicate=True),
    Input({'type': 'add-response', 'index': dash.ALL}, 'n_clicks'),
    [State({'type': 'response-text', 'index': dash.ALL}, 'value'),
     State('user-data', 'data')],
    prevent_initial_call=True
)
def add_customer_response(n_clicks, response_texts, user_data):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks) or not user_data:
        return dash.no_update
    
    # Find which button was clicked
    trigger_prop_id = ctx.triggered[0]['prop_id']
    complaint_id = json.loads(trigger_prop_id.split('.')[0])['index']
    
    # Find the corresponding response text
    button_idx = None
    for i, clicks in enumerate(n_clicks):
        if clicks:
            button_idx = i
            break
    
    if button_idx is None or not response_texts[button_idx]:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please enter a response message."
        ], color="warning", dismissable=True, duration=5000)
    
    # Add the response
    success = add_complaint_update(
        complaint_id,
        'customer_response',
        response_texts[button_idx],
        user_data.get('full_name', 'Customer')
    )
    
    if success:
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Your response has been added successfully."
        ], color="success", dismissable=True, duration=5000)
    else:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Error adding response. Please try again."
        ], color="danger", dismissable=True, duration=5000)

def add_complaint_update(complaint_id, update_type, message, created_by_name):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO complaint_updates (complaint_id, update_type, message, 
                                     created_by_name, is_customer_visible)
        VALUES (%s, %s, %s, %s, 1)
        """
        cursor.execute(query, (complaint_id, update_type, message, created_by_name))
        
        # If it's a customer response, update complaint status to pending_customer
        if update_type == 'customer_response':
            update_status_query = """
            UPDATE complaints SET status = 'pending_customer', updated_at = NOW()
            WHERE id = %s
            """
            cursor.execute(update_status_query, (complaint_id,))
        
        conn.commit()
        return True
    except Error as e:
        logging.error(f"Error adding complaint update: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Close complaint callback (for resolved complaints)
@app.callback(
    Output('alert-container', 'children', allow_duplicate=True),
    Input({'type': 'close-complaint', 'index': dash.ALL}, 'n_clicks'),
    State('user-data', 'data'),
    prevent_initial_call=True
)
def close_complaint(n_clicks, user_data):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks) or not user_data:
        return dash.no_update
    
    # Find which complaint to close
    trigger_prop_id = ctx.triggered[0]['prop_id']
    complaint_id = json.loads(trigger_prop_id.split('.')[0])['index']
    
    # Close the complaint
    success = close_complaint_by_customer(complaint_id, user_data.get('full_name', 'Customer'))
    
    if success:
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Complaint has been closed successfully."
        ], color="success", dismissable=True, duration=5000)
    else:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Error closing complaint. Please try again."
        ], color="danger", dismissable=True, duration=5000)

def close_complaint_by_customer(complaint_id, customer_name):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update complaint status to closed
        query = """
        UPDATE complaints SET status = 'closed', closed_at = NOW(), updated_at = NOW()
        WHERE id = %s AND status = 'resolved'
        """
        cursor.execute(query, (complaint_id,))
        
        if cursor.rowcount > 0:
            # Add update record
            update_query = """
            INSERT INTO complaint_updates (complaint_id, update_type, old_status, 
                                         new_status, message, created_by_name)
            VALUES (%s, 'status_change', 'resolved', 'closed', 
                    'Complaint closed by customer', %s)
            """
            cursor.execute(update_query, (complaint_id, customer_name))
            conn.commit()
            return True
        
        return False
    except Error as e:
        logging.error(f"Error closing complaint: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run_server(debug=True)