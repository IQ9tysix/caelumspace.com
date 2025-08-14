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
    url_base_pathname="/user_payment/",
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
                background: #f8f9fa;
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
            
            /* Payment Styles */
            .payment-container {
                padding: 30px;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .payment-card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                margin-bottom: 25px;
                border: 1px solid #e9ecef;
            }
            
            .payment-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }
            
            .payment-header h3 {
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }
            
            .payment-header p {
                margin: 5px 0 0 0;
                opacity: 0.9;
                font-size: 16px;
            }
            
            .booking-details {
                padding: 25px;
                border-bottom: 1px solid #e9ecef;
            }
            
            .detail-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding: 10px 0;
            }
            
            .detail-row:last-child {
                margin-bottom: 0;
            }
            
            .detail-label {
                font-weight: 600;
                color: #495057;
                font-size: 14px;
            }
            
            .detail-value {
                color: #212529;
                font-size: 14px;
            }
            
            .amount-row {
                border-top: 2px solid #e9ecef;
                padding-top: 15px;
                margin-top: 15px;
            }
            
            .amount-row .detail-value {
                font-size: 20px;
                font-weight: 700;
                color: #28a745;
            }
            
            .payment-methods {
                padding: 25px;
            }
            
            .payment-methods h5 {
                margin-bottom: 20px;
                color: #495057;
                font-weight: 600;
            }
            
            .method-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 25px;
            }
            
            .payment-method {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                background: white;
            }
            
            .payment-method:hover {
                border-color: #3498db;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);
            }
            
            .payment-method.selected {
                border-color: #3498db;
                background: #f8f9ff;
                box-shadow: 0 3px 10px rgba(52, 152, 219, 0.3);
            }
            
            .payment-method i {
                font-size: 36px;
                margin-bottom: 10px;
                color: #3498db;
            }
            
            .payment-method h6 {
                margin: 0;
                color: #495057;
                font-weight: 600;
            }
            
            .payment-method p {
                margin: 5px 0 0 0;
                font-size: 12px;
                color: #6c757d;
            }
            
            .payment-actions {
                padding: 0 25px 25px 25px;
            }
            
            .pay-button {
                width: 100%;
                padding: 15px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                border: none;
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
            }
            
            .pay-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
            }
            
            .pay-button:disabled {
                background: #6c757d;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .cancel-button {
                width: 100%;
                padding: 12px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                border: 1px solid #dc3545;
                background: white;
                color: #dc3545;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
            }
            
            .cancel-button:hover {
                background: #dc3545;
                color: white;
            }
            
            .security-info {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #28a745;
            }
            
            .security-info h6 {
                color: #28a745;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .security-info p {
                margin: 0;
                font-size: 13px;
                color: #6c757d;
            }
            
            .status-badge {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
            }
            
            .status-pending {
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }
            
            .status-confirmed {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .breadcrumb-nav {
                background: white;
                padding: 15px 30px;
                border-bottom: 1px solid #e9ecef;
            }
            
            .breadcrumb {
                margin: 0;
                background: none;
                padding: 0;
            }
            
            .breadcrumb-item a {
                color: #3498db;
                text-decoration: none;
            }
            
            .breadcrumb-item.active {
                color: #6c757d;
            }
            
            /* Success Modal */
            .success-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: none;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            }
            
            .success-modal {
                background: white;
                border-radius: 12px;
                padding: 40px;
                max-width: 400px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .success-icon {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: #28a745;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                margin: 0 auto 20px;
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
                .payment-container {
                    padding: 15px;
                }
                .method-grid {
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
        print(f"Error connecting to MySQL: {e}")
        return None

# Get booking details
def get_booking_details(booking_id):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT b.*, u.name as unit_name, w.name as warehouse_name, w.location as warehouse_location
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE b.id = %s
        """
        cursor.execute(query, (booking_id,))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error fetching booking: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Process payment
def process_payment(booking_id, payment_method, amount):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Generate transaction reference
        transaction_ref = f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{booking_id}"
        
        # Insert payment record
        payment_query = """
        INSERT INTO payments (booking_id, amount, payment_method, transaction_reference, status, notes)
        VALUES (%s, %s, %s, %s, 'completed', %s)
        """
        payment_notes = f"Payment processed via {payment_method}"
        cursor.execute(payment_query, (booking_id, amount, payment_method, transaction_ref, payment_notes))
        
        # Update booking payment status
        booking_query = """
        UPDATE bookings SET payment_status = 'paid', status = 'confirmed', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        cursor.execute(booking_query, (booking_id,))
        
        connection.commit()
        return True
    except Error as e:
        print(f"Error processing payment: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Main layout
def create_layout():
    return html.Div([
        # Sidebar
        html.Div([
            html.Div([
                html.H4("Storage Dashboard", className="mb-0"),
                html.Small("User Panel", className="text-muted")
            ], className="sidebar-header"),
            
            html.Ul([
                html.Li([html.A([html.I(className="fas fa-home me-2"), "Home"], href="/user_dashboard/")]),
                html.Li([html.A([html.I(className="fas fa-calendar me-2"), "Book Unit"], href="/user_booking/")]),
                html.Li([html.A([html.I(className="fas fa-list me-2"), "Manage Bookings"], href="/manage_bookings/")]),
                html.Li([html.A([html.I(className="fas fa-exclamation-triangle me-2"), "Complaints"], href="/user_complaints/")]),
                html.Li([html.A([html.I(className="fas fa-credit-card me-2"), "Payment & Invoice"], href="#", className="active")]),
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
                    html.H5("Payment & Invoice", className="mb-0")
                ], className="header-left"),
                
                html.Div([
                    # Notifications
                    dbc.DropdownMenu([
                        dbc.DropdownMenuItem("No new notifications", disabled=True),
                    ], label=html.I(className="fas fa-bell"), 
                       color="light", className="me-2"),
                    
                    # Profile section
                    html.Div([
                        html.Div("JD", className="profile-avatar"),
                        html.Div([
                            html.Div("John Doe", className="profile-name"),
                            html.Div("Individual", className="profile-type")
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
            
            # Breadcrumb
            html.Nav([
                html.Ol([
                    html.Li([
                        html.A("Dashboard", href="/user_dashboard/")
                    ], className="breadcrumb-item"),
                    html.Li([
                        html.A("Book Unit", href="/user_booking/")
                    ], className="breadcrumb-item"),
                    html.Li("Payment", className="breadcrumb-item active")
                ], className="breadcrumb")
            ], className="breadcrumb-nav"),
            
            # Content
            html.Div([
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content')
            ], className="payment-container")
            
        ], id="main-content", className="main-content"),
        
        # Success overlay
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-check")
                ], className="success-icon"),
                html.H4("Payment Successful!", style={'color': '#28a745', 'marginBottom': '15px'}),
                html.P("Your booking has been confirmed and payment processed successfully.", 
                      style={'marginBottom': '25px', 'color': '#6c757d'}),
                html.Button("View Bookings", id="view-bookings-btn", 
                           className="btn btn-success btn-lg")
            ], className="success-modal")
        ], id="success-overlay", className="success-overlay")
    ])

# Callback to handle page routing and display
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'href')
)
def display_page(href):
    if not href:
        return html.Div("Loading...")
    
    # Parse URL to get booking_id
    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)
    booking_id = params.get('booking_id', [None])[0]
    
    if not booking_id:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'fontSize': '48px', 'color': '#dc3545', 'marginBottom': '20px'}),
                html.H4("No Booking ID Found", style={'color': '#dc3545'}),
                html.P("Please select a booking from your dashboard to proceed with payment."),
                html.A("Go to Bookings", href="/manage_bookings/", className="btn btn-primary")
            ], style={'textAlign': 'center', 'padding': '50px'})
        ])
    
    # Get booking details
    booking = get_booking_details(booking_id)
    
    if not booking:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'fontSize': '48px', 'color': '#dc3545', 'marginBottom': '20px'}),
                html.H4("Booking Not Found", style={'color': '#dc3545'}),
                html.P("The booking you're trying to pay for could not be found."),
                html.A("Go to Bookings", href="/manage_bookings/", className="btn btn-primary")
            ], style={'textAlign': 'center', 'padding': '50px'})
        ])
    
    # Check if already paid
    if booking['payment_status'] == 'paid':
        return html.Div([
            html.Div([
                html.I(className="fas fa-check-circle", style={'fontSize': '48px', 'color': '#28a745', 'marginBottom': '20px'}),
                html.H4("Already Paid", style={'color': '#28a745'}),
                html.P("This booking has already been paid for."),
                html.A("View Bookings", href="/manage_bookings/", className="btn btn-success")
            ], style={'textAlign': 'center', 'padding': '50px'})
        ])
    
    # Calculate duration
    start_date = booking['start_date']
    end_date = booking['end_date']
    duration = (end_date - start_date).days
    
    return html.Div([
        html.Div([
            # Payment Header
            html.Div([
                html.H3("Complete Your Payment"),
                html.P(f"Booking #{booking['id']} - {booking['unit_name']}")
            ], className="payment-header"),
            
            # Booking Details
            html.Div([
                html.H5("Booking Details", style={'marginBottom': '20px', 'color': '#495057'}),
                
                html.Div([
                    html.Span("Customer Name:", className="detail-label"),
                    html.Span(booking['customer_name'], className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Unit:", className="detail-label"),
                    html.Span(booking['unit_name'], className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Warehouse:", className="detail-label"),
                    html.Span(f"{booking['warehouse_name']} - {booking['warehouse_location']}", className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Start Date:", className="detail-label"),
                    html.Span(booking['start_date'].strftime('%B %d, %Y'), className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("End Date:", className="detail-label"),
                    html.Span(booking['end_date'].strftime('%B %d, %Y'), className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Duration:", className="detail-label"),
                    html.Span(f"{duration} days", className="detail-value")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Status:", className="detail-label"),
                    html.Span(booking['status'].replace('_', ' ').title(), 
                             className=f"status-badge status-{booking['status']}")
                ], className="detail-row"),
                
                html.Div([
                    html.Span("Total Amount:", className="detail-label"),
                    html.Span(f"₦{booking['total_amount']:,.2f}", className="detail-value")
                ], className="detail-row amount-row"),
                
            ], className="booking-details"),
            
            # Payment Methods
            html.Div([
                html.H5("Select Payment Method"),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-university"),
                        html.H6("Bank Transfer"),
                        html.P("Direct bank transfer")
                    ], className="payment-method", id="method-transfer", **{'data-method': 'transfer'}),
                    
                    html.Div([
                        html.I(className="fas fa-credit-card"),
                        html.H6("Debit/Credit Card"),
                        html.P("Visa, Mastercard accepted")
                    ], className="payment-method", id="method-card", **{'data-method': 'card'}),
                    
                    html.Div([
                        html.I(className="fab fa-paypal"),
                        html.H6("Paystack"),
                        html.P("Secure online payment")
                    ], className="payment-method", id="method-paystack", **{'data-method': 'online'}),
                    
                    html.Div([
                        html.I(className="fas fa-money-bill-wave"),
                        html.H6("Cash Payment"),
                        html.P("Pay at warehouse location")
                    ], className="payment-method", id="method-cash", **{'data-method': 'cash'})
                ], className="method-grid"),
                
                # Security Info
                html.Div([
                    html.H6([html.I(className="fas fa-shield-alt me-2"), "Secure Payment"]),
                    html.P("Your payment information is encrypted and secure. We do not store your card details.")
                ], className="security-info"),
                
            ], className="payment-methods"),
            
            # Payment Actions
            html.Div([
                html.Button("Complete Payment", id="pay-button", className="pay-button", disabled=True),
                html.Button("Cancel & Return", id="cancel-button", className="cancel-button")
            ], className="payment-actions"),
            
            # Hidden fields
            dcc.Store(id='selected-method', data=''),
            dcc.Store(id='booking-data', data=booking)
            
        ], className="payment-card")
    ])

# Callback for payment method selection
@app.callback(
    [Output('method-transfer', 'className'),
     Output('method-card', 'className'),
     Output('method-paystack', 'className'),
     Output('method-cash', 'className'),
     Output('selected-method', 'data'),
     Output('pay-button', 'disabled')],
    [Input('method-transfer', 'n_clicks'),
     Input('method-card', 'n_clicks'),
     Input('method-paystack', 'n_clicks'),
     Input('method-cash', 'n_clicks')],
    prevent_initial_call=True
)
def select_payment_method(transfer_clicks, card_clicks, paystack_clicks, cash_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['payment-method'] * 4, '', True
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    classes = ['payment-method'] * 4
    selected_method = ''
    
    if triggered_id == 'method-transfer':
        classes[0] = 'payment-method selected'
        selected_method = 'transfer'
    elif triggered_id == 'method-card':
        classes[1] = 'payment-method selected'
        selected_method = 'card'
    elif triggered_id == 'method-paystack':
        classes[2] = 'payment-method selected'
        selected_method = 'online'
    elif triggered_id == 'method-cash':
        classes[3] = 'payment-method selected'
        selected_method = 'cash'
    
    return classes[0], classes[1], classes[2], classes[3], selected_method, selected_method == ''

# Callback for payment processing
@app.callback(
    Output('success-overlay', 'style'),
    Input('pay-button', 'n_clicks'),
    [State('selected-method', 'data'),
     State('booking-data', 'data')],
    prevent_initial_call=True
)
def process_payment_callback(n_clicks, selected_method, booking_data):
    if n_clicks and selected_method and booking_data:
        # Process the payment
        success = process_payment(booking_data['id'], selected_method, booking_data['total_amount'])
        
        if success:
            return {'display': 'flex'}
    
    return {'display': 'none'}

# Callback for redirect after successful payment
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            setTimeout(function() {
                window.location.href = '/manage_bookings/';
            }, 2000);
        }
        return '';
    }
    """,
    Output('view-bookings-btn', 'style'),
    Input('view-bookings-btn', 'n_clicks')
)

# Callback for cancel button
@app.callback(
    Output('url', 'href', allow_duplicate=True),
    Input('cancel-button', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_payment(n_clicks):
    if n_clicks:
        return '/manage_bookings/'
    return dash.no_update

# Sidebar toggle callback
clientside_callback(
    """
    function(n_clicks) {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');
        
        if (sidebar && mainContent) {
            sidebar.classList.toggle('hidden');
            mainContent.classList.toggle('expanded');
        }
        
        return '';
    }
    """,
    Output('sidebar-toggle', 'style'),
    Input('sidebar-toggle', 'n_clicks')
)

app.layout = create_layout()
