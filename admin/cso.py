import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import mysql.connector
from mysql.connector import Error
import base64
import io
from PIL import Image
import bcrypt
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'warehouse_db',
    'user': 'root',
    'password': ''  
}

class DatabaseManager:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return True
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Error as e:
            logger.error(f"Database query error: {e}")
            return False if not fetch else []

# Initialize database manager
db_manager = DatabaseManager()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Custom CSS styles
custom_styles = {
    'sidebar': {
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '250px',
        'padding': '20px 10px',
        'background-color': '#2c3e50',
        'color': 'white',
        'overflow-y': 'auto'
    },
    'content': {
        'margin-left': '250px',
        'padding': '20px',
        'background-color': '#f8f9fa',
        'min-height': '100vh'
    },
    'header': {
        'background-color': '#34495e',
        'color': 'white',
        'padding': '15px 20px',
        'margin': '-20px -20px 20px -20px',
        'border-radius': '0 0 5px 5px'
    },
    'card': {
        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'border': 'none',
        'border-radius': '8px'
    },
    'form-control': {
        'border-radius': '5px',
        'border': '1px solid #ddd'
    }
}

# Available roles for functions
AVAILABLE_ROLES = [
    'access_units',
    'access_payments', 
    'access_analytics',
    'access_complaints',
    'general_functions'
]

# Helper functions
def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_functions():
    """Retrieve all functions from database"""
    query = "SELECT * FROM functions ORDER BY created_at DESC"
    return db_manager.execute_query(query, fetch=True)

def get_csos():
    """Retrieve all CSOs with their function details"""
    query = """
    SELECT c.*, f.function_name, f.function_role 
    FROM cso_officers c 
    LEFT JOIN functions f ON c.function_id = f.function_id 
    ORDER BY c.created_at DESC
    """
    return db_manager.execute_query(query, fetch=True)

def get_function_options():
    """Get function options for dropdown"""
    functions = get_functions()
    return [{'label': f['function_name'], 'value': f['function_id']} for f in functions]

# Layout components
def create_sidebar():
    return html.Div([
        html.H3("Admin Panel", className="text-center mb-4"),
        html.Hr(),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Dashboard", href="#", className="text-white")),
            dbc.NavItem(dbc.NavLink("Functions", href="#", id="functions-tab", className="text-white")),
            dbc.NavItem(dbc.NavLink("CSO Officers", href="#", id="cso-tab", className="text-white")),
            dbc.NavItem(dbc.NavLink("Settings", href="#", className="text-white")),
            dbc.NavItem(dbc.NavLink("Logout", href="#", className="text-white mt-4")),
        ], vertical=True, pills=True)
    ], style=custom_styles['sidebar'])

def create_header():
    return html.Div([
        html.H2("Warehouse Management System", className="mb-0"),
        html.P("Administrator Dashboard", className="mb-0 opacity-75")
    ], style=custom_styles['header'])

def create_function_form():
    return dbc.Card([
        dbc.CardHeader(html.H4("Create New Function")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Function Name"),
                    dbc.Input(id="function-name", type="text", placeholder="Enter function name"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Function Role"),
                    dcc.Dropdown(
                        id="function-role",
                        options=[{'label': role.replace('_', ' ').title(), 'value': role} for role in AVAILABLE_ROLES],
                        placeholder="Select function role"
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Description"),
                    dbc.Textarea(id="function-description", placeholder="Enter function description"),
                ], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Create Function", id="create-function-btn", color="primary", className="me-2"),
                    dbc.Button("Reset", id="reset-function-btn", color="secondary", outline=True),
                ], width=12),
            ]),
        ])
    ], style=custom_styles['card'])

def create_cso_form():
    return dbc.Card([
        dbc.CardHeader(html.H4("Create New CSO Officer")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("CSO Name"),
                    dbc.Input(id="cso-name", type="text", placeholder="Enter CSO name"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Function"),
                    dcc.Dropdown(
                        id="cso-function",
                        placeholder="Select function first"
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Email Address"),
                    dbc.Input(id="cso-email", type="email", placeholder="Enter email address"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Password"),
                    dbc.Input(id="cso-password", type="password", placeholder="Enter password"),
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Profile Image"),
                    dcc.Upload(
                        id="cso-image",
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Image')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        }
                    ),
                ], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Create CSO", id="create-cso-btn", color="success", className="me-2"),
                    dbc.Button("Reset", id="reset-cso-btn", color="secondary", outline=True),
                ], width=12),
            ]),
        ])
    ], style=custom_styles['card'])

def create_functions_table():
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Functions Management", className="d-inline"),
            dbc.Button("Refresh", id="refresh-functions", color="info", size="sm", className="float-end")
        ]),
        dbc.CardBody([
            html.Div(id="functions-table-container")
        ])
    ], style=custom_styles['card'])

def create_cso_table():
    return dbc.Card([
        dbc.CardHeader([
            html.H4("CSO Officers Management", className="d-inline"),
            dbc.Button("Refresh", id="refresh-cso", color="info", size="sm", className="float-end")
        ]),
        dbc.CardBody([
            html.Div(id="cso-table-container")
        ])
    ], style=custom_styles['card'])

# Main layout
app.layout = html.Div([
    create_sidebar(),
    html.Div([
        create_header(),
        
        # Alert container
        html.Div(id="alert-container", className="mb-3"),
        
        # Tab content
        html.Div(id="tab-content", children=[
            # Functions tab content
            html.Div(id="functions-content", children=[
                dbc.Row([
                    dbc.Col([create_function_form()], width=12)
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col([create_functions_table()], width=12)
                ])
            ], style={'display': 'block'}),
            
            # CSO tab content
            html.Div(id="cso-content", children=[
                dbc.Row([
                    dbc.Col([create_cso_form()], width=12)
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col([create_cso_table()], width=12)
                ])
            ], style={'display': 'none'})
        ])
    ], style=custom_styles['content']),
    
    # Hidden divs for storing data
    html.Div(id="hidden-div", style={'display': 'none'}),
    dcc.Store(id="current-tab", data="functions"),
    dcc.Interval(id="interval-component", interval=30000, n_intervals=0)  # Refresh every 30 seconds
])

# Callbacks
@app.callback(
    [Output("functions-content", "style"),
     Output("cso-content", "style"),
     Output("current-tab", "data")],
    [Input("functions-tab", "n_clicks"),
     Input("cso-tab", "n_clicks")],
    [State("current-tab", "data")]
)
def switch_tabs(functions_clicks, cso_clicks, current_tab):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'block'}, {'display': 'none'}, "functions"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "functions-tab":
        return {'display': 'block'}, {'display': 'none'}, "functions"
    elif button_id == "cso-tab":
        return {'display': 'none'}, {'display': 'block'}, "cso"
    
    return {'display': 'block'}, {'display': 'none'}, current_tab

@app.callback(
    Output("alert-container", "children"),
    [Input("create-function-btn", "n_clicks"),
     Input("create-cso-btn", "n_clicks")],
    [State("function-name", "value"),
     State("function-role", "value"),
     State("function-description", "value"),
     State("cso-name", "value"),
     State("cso-function", "value"),
     State("cso-email", "value"),
     State("cso-password", "value"),
     State("cso-image", "contents")]
)
def handle_form_submissions(func_clicks, cso_clicks, func_name, func_role, func_desc,
                           cso_name, cso_function, cso_email, cso_password, cso_image):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "create-function-btn" and func_clicks:
        if not all([func_name, func_role, func_desc]):
            return dbc.Alert("Please fill in all function fields", color="danger", dismissable=True)
        
        # Insert function into database
        query = """
        INSERT INTO functions (function_name, function_role, function_description, created_at)
        VALUES (%s, %s, %s, %s)
        """
        params = (func_name, func_role, func_desc, datetime.now())
        
        if db_manager.execute_query(query, params):
            return dbc.Alert("Function created successfully!", color="success", dismissable=True)
        else:
            return dbc.Alert("Error creating function", color="danger", dismissable=True)
    
    elif button_id == "create-cso-btn" and cso_clicks:
        if not all([cso_name, cso_function, cso_email, cso_password]):
            return dbc.Alert("Please fill in all CSO fields", color="danger", dismissable=True)
        
        # Process image if uploaded
        image_data = None
        if cso_image:
            try:
                content_type, content_string = cso_image.split(',')
                decoded = base64.b64decode(content_string)
                image_data = base64.b64encode(decoded).decode('utf-8')
            except Exception as e:
                logger.error(f"Image processing error: {e}")
        
        # Hash password
        hashed_password = hash_password(cso_password)
        
        # Insert CSO into database
        query = """
        INSERT INTO cso_officers (cso_name, function_id, email, password_hash, profile_image, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (cso_name, cso_function, cso_email, hashed_password, image_data, datetime.now())
        
        if db_manager.execute_query(query, params):
            return dbc.Alert("CSO Officer created successfully!", color="success", dismissable=True)
        else:
            return dbc.Alert("Error creating CSO Officer", color="danger", dismissable=True)
    
    return ""

@app.callback(
    Output("cso-function", "options"),
    [Input("functions-tab", "n_clicks"),
     Input("cso-tab", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_function_options(func_clicks, cso_clicks, n):
    return get_function_options()

@app.callback(
    Output("functions-table-container", "children"),
    [Input("refresh-functions", "n_clicks"),
     Input("create-function-btn", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_functions_table(refresh_clicks, create_clicks, n):
    functions = get_functions()
    if not functions:
        return html.P("No functions found", className="text-muted")
    
    # Convert to DataFrame for table display
    df = pd.DataFrame(functions)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    df['function_role'] = df['function_role'].str.replace('_', ' ').str.title()
    
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[
            {"name": "ID", "id": "function_id"},
            {"name": "Function Name", "id": "function_name"},
            {"name": "Role", "id": "function_role"},
            {"name": "Description", "id": "function_description"},
            {"name": "Created", "id": "created_at"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'white'},
        page_size=10
    )

@app.callback(
    Output("cso-table-container", "children"),
    [Input("refresh-cso", "n_clicks"),
     Input("create-cso-btn", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_cso_table(refresh_clicks, create_clicks, n):
    csos = get_csos()
    if not csos:
        return html.P("No CSO officers found", className="text-muted")
    
    # Convert to DataFrame for table display
    df = pd.DataFrame(csos)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[
            {"name": "ID", "id": "cso_id"},
            {"name": "CSO Name", "id": "cso_name"},
            {"name": "Function", "id": "function_name"},
            {"name": "Email", "id": "email"},
            {"name": "Created", "id": "created_at"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'white'},
        page_size=10
    )

# Reset form callbacks
@app.callback(
    [Output("function-name", "value"),
     Output("function-role", "value"),
     Output("function-description", "value")],
    [Input("reset-function-btn", "n_clicks")]
)
def reset_function_form(n_clicks):
    if n_clicks:
        return "", None, ""
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [Output("cso-name", "value"),
     Output("cso-function", "value"),
     Output("cso-email", "value"),
     Output("cso-password", "value")],
    [Input("reset-cso-btn", "n_clicks")]
)
def reset_cso_form(n_clicks):
    if n_clicks:
        return "", None, "", ""
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
