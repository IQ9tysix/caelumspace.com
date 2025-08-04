import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime
from flask import session
import logging

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/logout/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_user_info():
    """Get current user information before logout."""
    if not session.get('authenticated'):
        return None
    
    user_type = session.get('user_type')
    if user_type == 'admin':
        return {
            'type': 'admin',
            'name': 'Administrator',
            'email': session.get('email', 'admin@gmail.com')
        }
    elif user_type == 'cso':
        return {
            'type': 'cso',
            'name': session.get('cso_name', 'CSO Officer'),
            'email': session.get('email', ''),
            'function': session.get('function_name', '')
        }
    elif user_type == 'user':
        return {
            'type': 'user',
            'name': 'User',
            'email': session.get('email', '')
        }
    return None

def clear_user_session():
    """Clear all session data and log the logout."""
    user_info = get_current_user_info()
    if user_info:
        logger.info(f"User logout: {user_info['type']} - {user_info['email']}")
    
    session.clear()
    logger.info("Session cleared successfully")
    return user_info

app.layout = dbc.Container([
    dcc.Location(id='logout-url', refresh=False),
    dcc.Store(id='logout-store', storage_type='memory'),
    
    html.Div([
        # Main logout container
        html.Div([
            html.Div([
                # Logo section
                html.Div([
                    html.Img(
                        src=app.get_asset_url('images/logo.png'),
                        alt="Warehouse Logo",
                        style={
                            'maxWidth': '80px',
                            'marginBottom': '20px'
                        }
                    )
                ], className="text-center"),
                
                # Logout content
                html.Div(id="logout-content", children=[
                    # Initial logout processing message
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-spinner fa-spin", style={'fontSize': '24px', 'color': '#007bff'}),
                            html.H4("Signing you out...", className="mt-3"),
                            html.P("Please wait while we securely log you out.", className="text-muted")
                        ], className="text-center")
                    ])
                ]),
                
                # Action buttons (initially hidden)
                html.Div(id="logout-actions", children=[], style={'display': 'none'})
                
            ], className="logout-card")
        ], className="logout-container")
    ], className="logout-wrapper")
], fluid=True, className="p-0")

# Main logout callback
@app.callback(
    [Output('logout-content', 'children'),
     Output('logout-actions', 'children'),
     Output('logout-actions', 'style'),
     Output('logout-store', 'data')],
    [Input('logout-url', 'pathname')],
    prevent_initial_call=False
)
def handle_logout(pathname):
    """Handle the logout process."""
    
    # Get user info before clearing session
    user_info = get_current_user_info()
    
    if user_info is None:
        # User not logged in
        content = html.Div([
            html.Div([
                html.I(className="fas fa-info-circle", style={'fontSize': '48px', 'color': '#17a2b8'}),
                html.H3("Not Logged In", className="mt-3"),
                html.P("You are not currently logged in to the system.", className="text-muted")
            ], className="text-center")
        ])
        
        actions = html.Div([
            dbc.Button(
                "Go to Login",
                href="/login",
                color="primary",
                className="me-2",
                external_link=True
            ),
            dbc.Button(
                "Go to Home",
                href="/",
                color="outline-secondary",
                external_link=True
            )
        ], className="text-center mt-4")
        
        return content, actions, {'display': 'block'}, {'logged_out': False}
    
    # Clear the session
    cleared_user = clear_user_session()
    
    # Create success message based on user type
    if cleared_user['type'] == 'admin':
        welcome_msg = f"Goodbye, {cleared_user['name']}"
        description = "You have been successfully logged out of the admin panel."
    elif cleared_user['type'] == 'cso':
        welcome_msg = f"Goodbye, {cleared_user['name']}"
        description = f"You have been logged out from {cleared_user.get('function', 'CSO')} dashboard."
    else:
        welcome_msg = "Goodbye"
        description = "You have been successfully logged out of your account."
    
    content = html.Div([
        html.Div([
            html.I(className="fas fa-check-circle", style={'fontSize': '48px', 'color': '#28a745'}),
            html.H3(welcome_msg, className="mt-3"),
            html.P(description, className="text-muted"),
            html.Hr(),
            html.P([
                html.Small([
                    "Logged out at: ",
                    html.Strong(datetime.now().strftime("%B %d, %Y at %I:%M %p"))
                ], className="text-muted")
            ])
        ], className="text-center")
    ])
    
    actions = html.Div([
        dbc.Button(
            "Sign In Again",
            href="/login",
            color="primary",
            className="me-2",
            external_link=True
        ),
        dbc.Button(
            "Go to Home",
            href="/",
            color="outline-secondary",
            external_link=True
        )
    ], className="text-center mt-4")
    
    return content, actions, {'display': 'block'}, {
        'logged_out': True,
        'user_type': cleared_user['type'],
        'logout_time': datetime.now().isoformat()
    }

# Auto-redirect callback (optional - redirects to login after 5 seconds)
@app.callback(
    Output('logout-url', 'href'),
    [Input('logout-store', 'data')],
    prevent_initial_call=True
)
def auto_redirect(logout_data):
    """Auto redirect to login page after successful logout (optional)."""
    if logout_data and logout_data.get('logged_out'):
        # Uncomment the line below if you want auto-redirect after 5 seconds
        # import time; time.sleep(5); return "/login"
        pass
    return dash.no_update

# CSS styles for the logout page
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            .logout-wrapper {
                min-height: 100vh;
                background: linear-gradient(135deg, #FFFF00 0%, #FFFFFF 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .logout-container {
                width: 100%;
                max-width: 500px;
            }
            
            .logout-card {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .logout-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #007bff, #28a745, #17a2b8);
            }
            
            .logout-card h3 {
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .logout-card h4 {
                color: #2c3e50;
                font-weight: 500;
                margin-bottom: 10px;
            }
            
            .logout-card p {
                color: #6c757d;
                margin-bottom: 15px;
            }
            
            .logout-card .text-muted {
                color: #6c757d !important;
            }
            
            .btn {
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 500;
                text-decoration: none;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .fa-spinner {
                animation: spin 1s linear infinite;
            }
            
            .fa-check-circle {
                color: #28a745 !important;
                animation: fadeInScale 0.5s ease-out;
            }
            
            .fa-info-circle {
                color: #17a2b8 !important;
                animation: fadeInScale 0.5s ease-out;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes fadeInScale {
                0% {
                    opacity: 0;
                    transform: scale(0.5);
                }
                100% {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            
            hr {
                border: none;
                height: 1px;
                background: linear-gradient(90deg, transparent, #dee2e6, transparent);
                margin: 20px 0;
            }
            
            @media (max-width: 576px) {
                .logout-card {
                    padding: 30px 20px;
                    margin: 10px;
                }
                
                .btn {
                    width: 100%;
                    margin-bottom: 10px;
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

# Server route for logout (alternative method)
@app.server.route('/logout')
def logout_route():
    """Server route for logout (alternative to Dash page)."""
    user_info = get_current_user_info()
    clear_user_session()
    
    if user_info:
        logger.info(f"Server route logout: {user_info['type']} - {user_info['email']}")
    
    # Redirect to login page
    from flask import redirect
    return redirect('/login?message=logged_out')
