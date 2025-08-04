import dash
from dash import dcc, html, Input, Output, State, dash_table, callback, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector
from datetime import datetime, date
import dash_bootstrap_components as dbc

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='warehouse_db',
        user='root',
        password=''  # Update with your WAMP MySQL password if needed
    )

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary-black: #1a1a1a;
                --secondary-black: #2d2d2d;
                --accent-yellow: #ffd700;
                --bright-yellow: #ffed4e;
                --dark-yellow: #b8860b;
                --pure-white: #ffffff;
                --light-gray: #f8f9fa;
                --border-gray: #e9ecef;
                --shadow-light: rgba(0, 0, 0, 0.1);
                --shadow-medium: rgba(0, 0, 0, 0.15);
                --shadow-heavy: rgba(0, 0, 0, 0.25);
                --gradient-yellow: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                --gradient-dark: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            }

            * {
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                margin: 0;
                padding: 0;
                color: var(--primary-black);
                line-height: 1.6;
            }

            /* Main Container Styling */
            .container-fluid {
                padding: 2rem 3rem;
                max-width: 1400px;
                margin: 0 auto;
            }

            /* Header Styling */
            h1 {
                background: var(--gradient-dark);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
                font-size: 3.5rem;
                text-align: center;
                margin-bottom: 3rem;
                text-shadow: 2px 2px 4px var(--shadow-light);
                position: relative;
            }

            h1::after {
                content: '';
                position: absolute;
                bottom: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 4px;
                background: var(--gradient-yellow);
                border-radius: 2px;
            }

            /* Revolutionary Tab Menu Design */
            .tab-container {
                position: relative;
                margin-bottom: 3rem;
                background: var(--pure-white);
                border-radius: 20px;
                padding: 8px;
                box-shadow: 0 10px 30px var(--shadow-light);
                border: 2px solid var(--accent-yellow);
            }

            .tab-container::before {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: var(--gradient-yellow);
                border-radius: 22px;
                z-index: -1;
                opacity: 0.3;
            }

            .tab-container .tab {
                display: inline-block;
                position: relative;
                margin: 0 4px;
                border-radius: 14px;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .tab-container .tab-content {
                padding: 16px 28px;
                font-weight: 600;
                font-size: 0.95rem;
                text-decoration: none;
                color: var(--secondary-black);
                display: flex;
                align-items: center;
                gap: 8px;
                position: relative;
                z-index: 2;
                transition: all 0.3s ease;
                border-radius: 12px;
            }

            .tab-container .tab-content::before {
                content: attr(data-icon);
                font-family: 'Font Awesome 6 Free';
                font-weight: 900;
                font-size: 1.1rem;
            }

            .tab-container .tab:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
            }

            .tab-container .tab:hover .tab-content {
                color: var(--primary-black);
                background: rgba(255, 215, 0, 0.1);
            }

            /* Active Tab Styling */
            .tab-container .tab--selected {
                background: var(--gradient-dark);
                box-shadow: 0 8px 30px rgba(26, 26, 26, 0.3);
                transform: translateY(-1px);
            }

            .tab-container .tab--selected .tab-content {
                color: var(--pure-white);
                background: transparent;
            }

            .tab-container .tab--selected::after {
                content: '';
                position: absolute;
                bottom: -8px;
                left: 50%;
                transform: translateX(-50%);
                width: 6px;
                height: 6px;
                background: var(--accent-yellow);
                border-radius: 50%;
                box-shadow: 0 0 10px var(--accent-yellow);
            }

            /* Enhanced Card Designs */
            .card {
                background: var(--pure-white);
                border-radius: 16px;
                border: none;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                margin-bottom: 2rem;
            }

            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--gradient-yellow);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .card:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            }

            .card:hover::before {
                opacity: 1;
            }

            /* Summary Cards with Unique Designs */
            .summary-cards .card {
                text-align: center;
                padding: 2rem 1.5rem;
                position: relative;
                background: var(--pure-white);
            }

            .summary-cards .card-title {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                background: var(--gradient-dark);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .summary-cards .card-text {
                font-size: 1.1rem;
                font-weight: 500;
                color: var(--secondary-black);
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            /* Individual Card Color Accents */
            .summary-cards .row > div:nth-child(1) .card::before { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); }
            .summary-cards .row > div:nth-child(2) .card::before { background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%); }
            .summary-cards .row > div:nth-child(3) .card::before { background: linear-gradient(135deg, #17a2b8 0%, #117a8b 100%); }
            .summary-cards .row > div:nth-child(4) .card::before { background: var(--gradient-yellow); }
            .summary-cards .row > div:nth-child(5) .card::before { background: linear-gradient(135deg, #6c757d 0%, #495057 100%); }
            .summary-cards .row > div:nth-child(6) .card::before { background: linear-gradient(135deg, #e9ecef 0%, #adb5bd 100%); }
            .summary-cards .row > div:nth-child(7) .card::before { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); }
            .summary-cards .row > div:nth-child(8) .card::before { background: var(--gradient-dark); }

            /* Card Headers */
            .card-header {
                background: var(--gradient-dark) !important;
                color: var(--pure-white) !important;
                border: none !important;
                padding: 1.25rem 1.5rem;
                font-weight: 600;
                border-radius: 16px 16px 0 0 !important;
            }

            .card-header h5 {
                margin: 0;
                font-size: 1.2rem;
                color: var(--pure-white) !important;
            }

            .card-body {
                padding: 2rem;
                color: var(--secondary-black);
            }

            .card-body h4 {
                color: var(--primary-black);
                margin-bottom: 1rem;
                font-weight: 600;
            }

            .card-body h6 {
                color: var(--secondary-black);
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .card-body p {
                margin-bottom: 0.75rem;
                color: var(--secondary-black);
                font-size: 0.95rem;
            }

            /* Enhanced Form Styling */
            .form-control, .form-select {
                border: 2px solid var(--border-gray);
                border-radius: 12px;
                padding: 0.75rem 1rem;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                background: var(--pure-white);
                color: var(--primary-black);
            }

            .form-control:focus, .form-select:focus {
                border-color: var(--accent-yellow);
                box-shadow: 0 0 0 0.2rem rgba(255, 215, 0, 0.25);
                outline: none;
            }

            .form-label {
                font-weight: 600;
                color: var(--primary-black);
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            /* Revolutionary Button Design */
            .btn {
                border-radius: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 0.75rem 2rem;
                border: none;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                font-size: 0.85rem;
            }

            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }

            .btn:hover::before {
                left: 100%;
            }

            .btn-primary {
                background: var(--gradient-dark);
                color: var(--pure-white);
                box-shadow: 0 4px 15px rgba(26, 26, 26, 0.3);
            }

            .btn-primary:hover {
                background: var(--primary-black);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(26, 26, 26, 0.4);
            }

            .btn-success {
                background: var(--gradient-yellow);
                color: var(--primary-black);
                box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
            }

            .btn-success:hover {
                background: var(--dark-yellow);
                color: var(--pure-white);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
            }

            /* Badge Styling */
            .badge {
                font-size: 0.75rem;
                font-weight: 600;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            /* Alert Styling */
            .alert {
                border: none;
                border-radius: 12px;
                padding: 1rem 1.5rem;
                font-weight: 500;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 1.5rem;
            }

            .alert-success {
                background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(30, 126, 52, 0.05) 100%);
                color: #1e7e34;
                border-left: 4px solid #28a745;
            }

            .alert-danger {
                background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(200, 35, 51, 0.05) 100%);
                color: #c82333;
                border-left: 4px solid #dc3545;
            }

            .alert-info {
                background: linear-gradient(135deg, rgba(23, 162, 184, 0.1) 0%, rgba(17, 122, 139, 0.05) 100%);
                color: #117a8b;
                border-left: 4px solid #17a2b8;
            }

            /* Dropdown Styling */
            .Select-control {
                border: 2px solid var(--border-gray) !important;
                border-radius: 12px !important;
                min-height: 45px !important;
                background: var(--pure-white) !important;
            }

            .Select-control:hover {
                border-color: var(--accent-yellow) !important;
            }

            .Select--focused .Select-control {
                border-color: var(--accent-yellow) !important;
                box-shadow: 0 0 0 0.2rem rgba(255, 215, 0, 0.25) !important;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container-fluid {
                    padding: 1rem 1.5rem;
                }

                h1 {
                    font-size: 2.5rem;
                }

                .tab-container .tab-content {
                    padding: 12px 20px;
                    font-size: 0.85rem;
                }

                .summary-cards .card-title {
                    font-size: 2.5rem;
                }

                .card-body {
                    padding: 1.5rem;
                }
            }

            /* Loading Animation */
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .loading {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }

            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: var(--light-gray);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb {
                background: var(--gradient-yellow);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: var(--dark-yellow);
            }

            /* Enhanced spacing and typography */
            hr {
                border: none;
                height: 2px;
                background: var(--gradient-yellow);
                margin: 2rem 0;
                border-radius: 1px;
            }

            h3 {
                color: var(--primary-black);
                font-weight: 600;
                margin-bottom: 1.5rem;
                font-size: 2rem;
            }

            h4 {
                color: var(--secondary-black);
                font-weight: 600;
                margin-bottom: 1rem;
            }

            /* Micro-interactions */
            .card, .btn, .form-control, .alert {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            /* Focus indicators for accessibility */
            .btn:focus, .form-control:focus, .form-select:focus {
                outline: 2px solid var(--accent-yellow);
                outline-offset: 2px;
            }
        </style>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <script>
                // Enhanced tab interactions
                document.addEventListener('DOMContentLoaded', function() {
                    // Add icons to tabs based on their text
                    const tabIcons = {
                        'Summary': '\uf080',
                        'Warehouse & Units': '\uf1ad',
                        'Bookings': '\uf073',
                        'Payments': '\uf3d1',
                        'Complaints': '\uf4ad',
                        'CSO Management': '\uf508'
                    };
                    
                    // Apply icons and enhanced styling
                    setTimeout(() => {
                        const tabs = document.querySelectorAll('.tab-content');
                        tabs.forEach(tab => {
                            const text = tab.textContent.trim();
                            if (tabIcons[text]) {
                                tab.setAttribute('data-icon', tabIcons[text]);
                            }
                        });
                        
                        // Add container class for styling
                        const tabContainer = document.querySelector('.tabs-container') || 
                                           document.querySelector('[data-dash-is-loading]')?.parentElement?.querySelector('div');
                        if (tabContainer) {
                            tabContainer.classList.add('tab-container');
                        }
                    }, 100);
                    
                    // Enhanced card hover effects
                    document.addEventListener('mouseover', function(e) {
                        if (e.target.closest('.card')) {
                            e.target.closest('.card').style.transform = 'translateY(-8px)';
                        }
                    });
                    
                    document.addEventListener('mouseout', function(e) {
                        if (e.target.closest('.card')) {
                            e.target.closest('.card').style.transform = 'translateY(0)';
                        }
                    });
                    
                    // Add summary-cards class to summary section
                    const observer = new MutationObserver(function(mutations) {
                        mutations.forEach(function(mutation) {
                            const summarySection = document.querySelector('h3[children="Dashboard Summary"]')?.parentElement;
                            if (summarySection) {
                                summarySection.classList.add('summary-cards');
                            }
                        });
                    });
                    
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                });
            </script>
        </footer>
    </body>
</html>
'''

# Helper functions
def execute_query(query, params=None, fetch=True):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return [] if fetch else 0
    finally:
        cursor.close()
        conn.close()

def get_summary_data():
    queries = {
        'total_bookings': "SELECT COUNT(*) as count FROM bookings",
        'total_units': "SELECT COUNT(*) as count FROM units",
        'total_warehouses': "SELECT COUNT(*) as count FROM warehouses",
        'total_payments': "SELECT COUNT(*) as count FROM payments",
        'total_complaints': "SELECT COUNT(*) as count FROM complaints",
        'total_cso': "SELECT COUNT(*) as count FROM cso_officers",
        'active_bookings': "SELECT COUNT(*) as count FROM bookings WHERE status IN ('confirmed', 'pending')",
        'available_units': "SELECT COUNT(*) as count FROM units WHERE availability = 'not taken'"
    }
    
    summary = {}
    for key, query in queries.items():
        result = execute_query(query)
        summary[key] = result[0]['count'] if result else 0
    
    return summary

def get_warehouses():
    return execute_query("SELECT * FROM warehouses ORDER BY name")

def get_functions():
    return execute_query("SELECT * FROM functions WHERE is_active = 1 ORDER BY function_name")

def get_units_by_warehouse(warehouse_id):
    return execute_query("SELECT * FROM units WHERE warehouse_id = %s ORDER BY name", (warehouse_id,))

def get_bookings_data():
    query = """
    SELECT b.*, w.name as warehouse_name, u.name as unit_name 
    FROM bookings b 
    LEFT JOIN units u ON b.unit_id = u.id 
    LEFT JOIN warehouses w ON u.warehouse_id = w.id 
    ORDER BY b.created_at DESC
    """
    return execute_query(query)

def get_payments_data():
    query = """
    SELECT p.*, b.customer_name, u.name as unit_name, w.name as warehouse_name
    FROM payments p
    LEFT JOIN bookings b ON p.booking_id = b.id
    LEFT JOIN units u ON b.unit_id = u.id
    LEFT JOIN warehouses w ON u.warehouse_id = w.id
    ORDER BY p.payment_date DESC
    """
    return execute_query(query)

def get_complaints_data():
    query = """
    SELECT c.*, cc.category_name, cso.cso_name as assigned_to_name
    FROM complaints c
    LEFT JOIN complaint_categories cc ON c.category_id = cc.id
    LEFT JOIN cso_officers cso ON c.assigned_to = cso.cso_id
    ORDER BY c.created_at DESC
    """
    return execute_query(query)

def get_cso_data():
    query = """
    SELECT c.*, f.function_name
    FROM cso_officers c
    LEFT JOIN functions f ON c.function_id = f.function_id
    ORDER BY c.cso_name
    """
    return execute_query(query)

# Layout components
def create_summary_cards(data):
    cards = [
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_bookings'], className="card-title"),
                html.P("Total Bookings", className="card-text")
            ])
        ], color="primary", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['active_bookings'], className="card-title"),
                html.P("Active Bookings", className="card-text")
            ])
        ], color="success", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_units'], className="card-title"),
                html.P("Total Units", className="card-text")
            ])
        ], color="info", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['available_units'], className="card-title"),
                html.P("Available Units", className="card-text")
            ])
        ], color="warning", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_warehouses'], className="card-title"),
                html.P("Total Warehouses", className="card-text")
            ])
        ], color="secondary", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_payments'], className="card-title"),
                html.P("Total Payments", className="card-text")
            ])
        ], color="light", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_complaints'], className="card-title"),
                html.P("Total Complaints", className="card-text")
            ])
        ], color="danger", outline=True),
        dbc.Card([
            dbc.CardBody([
                html.H4(data['total_cso'], className="card-title"),
                html.P("CSO Officers", className="card-text")
            ])
        ], color="dark", outline=True),
    ]
    
    return dbc.Row([dbc.Col(card, width=3) for card in cards])

# Main layout
app.layout = html.Div([
    dbc.Container([
        html.H1("Warehouse Management Dashboard", className="mb-4 text-center"),
        
        dcc.Tabs(id="main-tabs", value="summary", children=[
            dcc.Tab(label="Summary", value="summary"),
            dcc.Tab(label="Warehouse & Units", value="warehouses"),
            dcc.Tab(label="Bookings", value="bookings"),
            dcc.Tab(label="Payments", value="payments"),
            dcc.Tab(label="Complaints", value="complaints"),
            dcc.Tab(label="CSO Management", value="cso"),
        ]),
        
        html.Div(id="tab-content", className="mt-4")
    ], fluid=True)
])

# Callbacks
@app.callback(Output("tab-content", "children"), Input("main-tabs", "value"))
def render_content(active_tab):
    if active_tab == "summary":
        summary_data = get_summary_data()
        return html.Div([
            html.H3("Dashboard Summary"),
            html.Hr(),
            create_summary_cards(summary_data),
            html.Div(id="summary-refresh", style={"display": "none"})
        ])
    
    elif active_tab == "warehouses":
        warehouses = get_warehouses()
        warehouse_options = [{"label": w["name"], "value": w["id"]} for w in warehouses]
        
        return html.Div([
            html.H3("Warehouse & Unit Management"),
            html.Hr(),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Add New Warehouse"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Warehouse Name"),
                                dbc.Input(id="warehouse-name", type="text", placeholder="Enter warehouse name")
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Location"),
                                dbc.Input(id="warehouse-location", type="text", placeholder="Enter location")
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Capacity"),
                                dbc.Input(id="warehouse-capacity", type="number", placeholder="Enter capacity")
                            ], width=2),
                            dbc.Col([
                                html.Br(),
                                dbc.Button("Add Warehouse", id="add-warehouse-btn", color="primary")
                            ], width=2)
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Add Units to Warehouse"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Select Warehouse"),
                                dcc.Dropdown(id="unit-warehouse-dropdown", options=warehouse_options, placeholder="Select warehouse")
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Unit Name"),
                                dbc.Input(id="unit-name", type="text", placeholder="Enter unit name")
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Price"),
                                dbc.Input(id="unit-price", type="number", step=0.01, placeholder="Enter price")
                            ], width=2),
                            dbc.Col([
                                dbc.Label("Status"),
                                dcc.Dropdown(id="unit-status", options=[
                                    {"label": "Active", "value": "active"},
                                    {"label": "Inactive", "value": "inactive"}
                                ], value="active")
                            ], width=2),
                            dbc.Col([
                                html.Br(),
                                dbc.Button("Add Unit", id="add-unit-btn", color="success")
                            ], width=2)
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            html.Div(id="warehouses-units-display"),
            html.Div(id="warehouse-alert"),
            html.Div(id="unit-alert")
        ])
    
    elif active_tab == "bookings":
        bookings = get_bookings_data()
        
        if not bookings:
            return html.Div([
                html.H3("Bookings Management"),
                html.Hr(),
                dbc.Alert("No bookings found.", color="info")
            ])
        
        cards = []
        for booking in bookings:
            card = dbc.Card([
                dbc.CardHeader(html.H5(f"Booking #{booking['id']} - {booking['customer_name']}")),
                dbc.CardBody([
                    html.P(f"Email: {booking['customer_email']}"),
                    html.P(f"Phone: {booking['customer_phone']}"),
                    html.P(f"Unit: {booking['unit_name']} ({booking['warehouse_name']})"),
                    html.P(f"Dates: {booking['start_date']} to {booking['end_date']}"),
                    html.P(f"Amount: ₦{booking['total_amount']}"),
                    dbc.Badge(booking['status'].title(), color="primary" if booking['status'] == 'confirmed' else "warning"),
                    html.Span(" "),
                    dbc.Badge(booking['payment_status'].title(), color="success" if booking['payment_status'] == 'paid' else "danger")
                ])
            ], className="mb-3")
            cards.append(card)
        
        return html.Div([
            html.H3("Bookings Management"),
            html.Hr(),
            html.Div(cards)
        ])
    
    elif active_tab == "payments":
        payments = get_payments_data()
        
        if not payments:
            return html.Div([
                html.H3("Payments Management"),
                html.Hr(),
                dbc.Alert("No payments found.", color="info")
            ])
        
        cards = []
        for payment in payments:
            card = dbc.Card([
                dbc.CardHeader(html.H5(f"Payment #{payment['id']} - {payment['customer_name'] or 'N/A'}")),
                dbc.CardBody([
                    html.P(f"Amount: ₦{payment['amount']}"),
                    html.P(f"Method: {payment['payment_method'].title()}"),
                    html.P(f"Reference: {payment['transaction_reference'] or 'N/A'}"),
                    html.P(f"Unit: {payment['unit_name'] or 'N/A'} ({payment['warehouse_name'] or 'N/A'})"),
                    html.P(f"Date: {payment['payment_date']}"),
                    dbc.Badge(payment['status'].title(), color="success" if payment['status'] == 'completed' else "warning")
                ])
            ], className="mb-3")
            cards.append(card)
        
        return html.Div([
            html.H3("Payments Management"),
            html.Hr(),
            html.Div(cards)
        ])
    
    elif active_tab == "complaints":
        complaints = get_complaints_data()
        
        if not complaints:
            return html.Div([
                html.H3("Complaints Management"),
                html.Hr(),
                dbc.Alert("No complaints found.", color="info")
            ])
        
        cards = []
        for complaint in complaints:
            priority_color = {
                'low': 'success',
                'medium': 'warning', 
                'high': 'danger',
                'urgent': 'dark'
            }.get(complaint['priority'], 'secondary')
            
            card = dbc.Card([
                dbc.CardHeader(html.H5(f"#{complaint['complaint_number']} - {complaint['customer_name']}")),
                dbc.CardBody([
                    html.P(f"Email: {complaint['customer_email']}"),
                    html.P(f"Subject: {complaint['subject']}"),
                    html.P(f"Category: {complaint['category_name'] or 'N/A'}"),
                    html.P(f"Description: {complaint['description'][:100]}..." if len(complaint['description']) > 100 else complaint['description']),
                    html.P(f"Assigned to: {complaint['assigned_to_name'] or 'Unassigned'}"),
                    html.P(f"Created: {complaint['created_at']}"),
                    dbc.Badge(complaint['status'].replace('_', ' ').title(), color="primary"),
                    html.Span(" "),
                    dbc.Badge(complaint['priority'].title(), color=priority_color)
                ])
            ], className="mb-3")
            cards.append(card)
        
        return html.Div([
            html.H3("Complaints Management"),
            html.Hr(),
            html.Div(cards)
        ])
    
    elif active_tab == "cso":
        functions = get_functions()
        function_options = [{"label": f["function_name"], "value": f["function_id"]} for f in functions]
        
        cso_officers = get_cso_data()
        
        cso_cards = []
        for officer in cso_officers:
            card = dbc.Card([
                dbc.CardHeader(html.H5(officer['cso_name'])),
                dbc.CardBody([
                    html.P(f"Email: {officer['email']}"),
                    html.P(f"Function: {officer['function_name']}"),
                    html.P(f"Status: {'Active' if officer['is_active'] else 'Inactive'}"),
                    html.P(f"Last Login: {officer['last_login'] or 'Never'}"),
                    html.P(f"Created: {officer['created_at']}")
                ])
            ], className="mb-3")
            cso_cards.append(card)
        
        return html.Div([
            html.H3("CSO Management"),
            html.Hr(),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Add New CSO Officer"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Officer Name"),
                                dbc.Input(id="cso-name", type="text", placeholder="Enter officer name")
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(id="cso-email", type="email", placeholder="Enter email")
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Password"),
                                dbc.Input(id="cso-password", type="password", placeholder="Enter password")
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Function"),
                                dcc.Dropdown(id="cso-function", options=function_options, placeholder="Select function")
                            ], width=2),
                            dbc.Col([
                                html.Br(),
                                dbc.Button("Add CSO", id="add-cso-btn", color="primary")
                            ], width=1)
                        ])
                    ])
                ], width=12)
            ]),
            
            html.Hr(),
            
            html.H4("Existing CSO Officers"),
            html.Div(cso_cards),
            html.Div(id="cso-alert")
        ])

# Warehouse management callbacks
@app.callback(
    [Output("warehouse-alert", "children"),
     Output("warehouses-units-display", "children"),
     Output("unit-warehouse-dropdown", "options")],
    [Input("add-warehouse-btn", "n_clicks")],
    [State("warehouse-name", "value"),
     State("warehouse-location", "value"),
     State("warehouse-capacity", "value")]
)
def add_warehouse(n_clicks, name, location, capacity):
    if n_clicks and name and location and capacity:
        query = "INSERT INTO warehouses (name, location, capacity) VALUES (%s, %s, %s)"
        result = execute_query(query, (name, location, capacity), fetch=False)
        
        if result:
            alert = dbc.Alert("Warehouse added successfully!", color="success", dismissable=True)
        else:
            alert = dbc.Alert("Failed to add warehouse.", color="danger", dismissable=True)
    else:
        alert = html.Div()
    
    # Refresh warehouse data
    warehouses = get_warehouses()
    warehouse_options = [{"label": w["name"], "value": w["id"]} for w in warehouses]
    
    # Display warehouses and their units
    warehouse_display = []
    for warehouse in warehouses:
        units = get_units_by_warehouse(warehouse['id'])
        unit_cards = []
        
        for unit in units:
            unit_card = dbc.Card([
                dbc.CardBody([
                    html.H6(unit['name']),
                    html.P(f"Price: ₦{unit['price']}"),
                    html.P(f"Status: {unit['status']}"),
                    html.P(f"Availability: {unit['availability']}")
                ])
            ], className="mb-2")
            unit_cards.append(unit_card)
        
        warehouse_card = dbc.Card([
            dbc.CardHeader(html.H5(f"{warehouse['name']} - {warehouse['location']}")),
            dbc.CardBody([
                html.P(f"Capacity: {warehouse['capacity']}"),
                html.P(f"Status: {warehouse['status']}"),
                html.H6("Units:"),
                html.Div(unit_cards) if unit_cards else html.P("No units added yet.")
            ])
        ], className="mb-3")
        
        warehouse_display.append(warehouse_card)
    
    return alert, warehouse_display, warehouse_options

# Unit management callback
@app.callback(
    Output("unit-alert", "children"),
    [Input("add-unit-btn", "n_clicks")],
    [State("unit-warehouse-dropdown", "value"),
     State("unit-name", "value"),
     State("unit-price", "value"),
     State("unit-status", "value")]
)
def add_unit(n_clicks, warehouse_id, name, price, status):
    if n_clicks and warehouse_id and name and price and status:
        query = "INSERT INTO units (warehouse_id, name, price, status) VALUES (%s, %s, %s, %s)"
        result = execute_query(query, (warehouse_id, name, price, status), fetch=False)
        
        if result:
            return dbc.Alert("Unit added successfully!", color="success", dismissable=True)
        else:
            return dbc.Alert("Failed to add unit.", color="danger", dismissable=True)
    
    return html.Div()

# CSO management callback
@app.callback(
    Output("cso-alert", "children"),
    [Input("add-cso-btn", "n_clicks")],
    [State("cso-name", "value"),
     State("cso-email", "value"),
     State("cso-password", "value"),
     State("cso-function", "value")]
)
def add_cso(n_clicks, name, email, password, function_id):
    if n_clicks and name and email and password and function_id:
        # Simple password hashing (in production, use proper hashing)
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = "INSERT INTO cso_officers (cso_name, email, password_hash, function_id) VALUES (%s, %s, %s, %s)"
        result = execute_query(query, (name, email, password_hash, function_id), fetch=False)
        
        if result:
            return dbc.Alert("CSO Officer added successfully!", color="success", dismissable=True)
        else:
            return dbc.Alert("Failed to add CSO Officer. Email might already exist.", color="danger", dismissable=True)
    
    return html.Div()

if __name__ == "__main__":
    app.run(debug=True)