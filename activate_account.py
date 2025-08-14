import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import mysql.connector
from mysql.connector import Error
import hashlib
import re
import os
import base64
import io
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from server import server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/activate_account/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ]
)

# Modern Black and Yellow Theme CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-yellow: #FFD700;
                --secondary-yellow: #FFA500;
                --dark-yellow: #DAA520;
                --primary-black: #0A0A0A;
                --secondary-black: #1A1A1A;
                --tertiary-black: #2A2A2A;
                --text-white: #FFFFFF;
                --text-gray: #CCCCCC;
                --success-green: #00FF88;
                --error-red: #FF4444;
                --border-gray: #404040;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--primary-black) 0%, var(--secondary-black) 100%);
                color: var(--text-white);
                min-height: 100vh;
                overflow-x: hidden;
            }

            .main-container {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                position: relative;
            }

            .main-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 165, 0, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(255, 215, 0, 0.05) 0%, transparent 50%);
                pointer-events: none;
            }

            .activation-card {
                background: rgba(26, 26, 26, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 40px;
                width: 100%;
                max-width: 500px;
                box-shadow: 
                    0 20px 60px rgba(0, 0, 0, 0.5),
                    0 0 0 1px rgba(255, 215, 0, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
                position: relative;
                z-index: 1;
                animation: slideIn 0.8s ease-out;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .brand-header {
                text-align: center;
                margin-bottom: 40px;
            }

            .brand-icon {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, var(--primary-yellow), var(--secondary-yellow));
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            .brand-icon i {
                font-size: 40px;
                color: var(--primary-black);
            }

            .brand-title {
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-yellow), var(--secondary-yellow));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 10px;
            }

            .brand-subtitle {
                color: var(--text-gray);
                font-size: 16px;
                font-weight: 400;
            }

            .form-section {
                margin-bottom: 30px;
            }

            .section-title {
                font-size: 20px;
                font-weight: 600;
                color: var(--text-white);
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section-title i {
                color: var(--primary-yellow);
                font-size: 24px;
            }

            .form-group {
                margin-bottom: 25px;
            }

            .form-label {
                display: block;
                margin-bottom: 8px;
                color: var(--text-gray);
                font-weight: 500;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .form-input {
                width: 100%;
                padding: 16px 20px;
                background: rgba(42, 42, 42, 0.8) !important;
                border: 2px solid var(--border-gray) !important;
                border-radius: 12px !important;
                color: var(--text-white) !important;
                font-size: 16px !important;
                transition: all 0.3s ease !important;
                backdrop-filter: blur(10px);
            }

            .form-input:focus {
                outline: none !important;
                border-color: var(--primary-yellow) !important;
                box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.1) !important;
                background: rgba(42, 42, 42, 1) !important;
            }

            .form-input::placeholder {
                color: #888 !important;
            }

            .form-input:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                background: rgba(42, 42, 42, 0.4) !important;
            }

            .btn-primary {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, var(--primary-yellow), var(--secondary-yellow)) !important;
                border: none !important;
                border-radius: 12px !important;
                color: var(--primary-black) !important;
                font-weight: 700 !important;
                font-size: 16px !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                position: relative !important;
                overflow: hidden !important;
            }

            .btn-primary:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 10px 25px rgba(255, 215, 0, 0.4) !important;
                background: linear-gradient(135deg, var(--secondary-yellow), var(--primary-yellow)) !important;
            }

            .btn-primary:active {
                transform: translateY(0) !important;
            }

            .btn-secondary {
                width: 100%;
                padding: 14px;
                background: transparent !important;
                border: 2px solid var(--primary-yellow) !important;
                border-radius: 12px !important;
                color: var(--primary-yellow) !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                margin-top: 15px;
            }

            .btn-secondary:hover {
                background: var(--primary-yellow) !important;
                color: var(--primary-black) !important;
                transform: translateY(-1px) !important;
            }

            .success-message {
                background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
                border: 1px solid var(--success-green);
                border-radius: 12px;
                padding: 20px;
                color: var(--success-green);
                text-align: center;
                margin-bottom: 20px;
                font-weight: 500;
                animation: slideIn 0.5s ease-out;
            }

            .error-message {
                background: linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(255, 68, 68, 0.05));
                border: 1px solid var(--error-red);
                border-radius: 12px;
                padding: 20px;
                color: var(--error-red);
                text-align: center;
                margin-bottom: 20px;
                font-weight: 500;
                animation: slideIn 0.5s ease-out;
            }

            .divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--border-gray), transparent);
                margin: 30px 0;
            }

            .info-box {
                background: rgba(255, 215, 0, 0.05);
                border: 1px solid rgba(255, 215, 0, 0.2);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 25px;
            }

            .info-box h6 {
                color: var(--primary-yellow);
                font-weight: 600;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .info-box p {
                color: var(--text-gray);
                font-size: 14px;
                line-height: 1.5;
                margin: 0;
            }

            .step-indicator {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
                gap: 15px;
            }

            .step {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
            }

            .step.active {
                background: linear-gradient(135deg, var(--primary-yellow), var(--secondary-yellow));
                color: var(--primary-black);
                box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
            }

            .step.completed {
                background: var(--success-green);
                color: var(--primary-black);
            }

            .step.inactive {
                background: var(--tertiary-black);
                color: var(--text-gray);
                border: 2px solid var(--border-gray);
            }

            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255, 215, 0, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary-yellow);
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .main-container {
                    padding: 15px;
                }
                
                .activation-card {
                    padding: 30px 25px;
                }
                
                .brand-title {
                    font-size: 24px;
                }
                
                .brand-icon {
                    width: 70px;
                    height: 70px;
                }
                
                .brand-icon i {
                    font-size: 35px;
                }
            }

            @media (max-width: 480px) {
                .activation-card {
                    padding: 25px 20px;
                }
                
                .brand-title {
                    font-size: 22px;
                }
                
                .section-title {
                    font-size: 18px;
                }
            }

            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: var(--secondary-black);
            }

            ::-webkit-scrollbar-thumb {
                background: var(--primary-yellow);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: var(--secondary-yellow);
            }

            /* Animation for success/error messages */
            .message-enter {
                animation: messageSlideIn 0.5s ease-out;
            }

            @keyframes messageSlideIn {
                from {
                    opacity: 0;
                    transform: translateX(-100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            .back-link {
                position: absolute;
                top: 20px;
                left: 20px;
                color: var(--text-gray);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
                transition: all 0.3s ease;
                z-index: 10;
            }

            .back-link:hover {
                color: var(--primary-yellow);
                text-decoration: none;
            }

            .back-link i {
                font-size: 16px;
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

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'warehouse_db',
    'user': 'root',
    'password': ''
}

# Email configuration (configure with your SMTP settings)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'terryfurtado5@gmail.com',
    'password': 'Thinkeriq96@'
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def generate_activation_code():
    """Generate a 6-digit activation code"""
    return ''.join(random.choices(string.digits, k=6))

def send_activation_email(email, activation_code, first_name=None):
    """Send activation email to user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = email
        msg['Subject'] = "Account Activation Code"
        
        name = first_name if first_name else "User"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #0A0A0A; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #FFD700, #FFA500); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: #0A0A0A; margin: 0; font-size: 28px; font-weight: bold; }}
                .content {{ background: #1A1A1A; padding: 30px; border-radius: 0 0 10px 10px; color: #FFFFFF; }}
                .code-box {{ background: #2A2A2A; border: 2px solid #FFD700; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0; }}
                .code {{ font-size: 36px; font-weight: bold; color: #FFD700; letter-spacing: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #CCCCCC; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Account Activation</h1>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Thank you for registering with our platform. To complete your account activation, please use the verification code below:</p>
                    
                    <div class="code-box">
                        <div class="code">{activation_code}</div>
                    </div>
                    
                    <p><strong>Important:</strong> This code will expire in 15 minutes for security reasons.</p>
                    <p>If you didn't create an account with us, please ignore this email.</p>
                    
                    <p>Best regards,<br>The Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['email'], email, text)
        server.quit()
        
        logger.info(f"Activation email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def update_user_activation_code(email, activation_code):
    """Update user's activation code in database"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            expiry_time = datetime.now() + timedelta(minutes=15)
            
            query = """UPDATE users SET activation_code = %s, activation_code_expiry = %s, updated_at = %s 
                      WHERE email = %s"""
            cursor.execute(query, (activation_code, expiry_time, datetime.now(), email))
            connection.commit()
            
            return cursor.rowcount > 0
        except Error as e:
            logger.error(f"Database error updating activation code: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

def verify_activation_code(email, code):
    """Verify activation code and activate account"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Check if code matches and hasn't expired
            query = """SELECT id, activation_code, activation_code_expiry FROM users 
                      WHERE email = %s AND activation_code = %s"""
            cursor.execute(query, (email, code))
            result = cursor.fetchone()
            
            if result:
                user_id, stored_code, expiry_time = result
                
                if expiry_time and datetime.now() > expiry_time:
                    return False, "Activation code has expired. Please request a new one."
                
                # Activate the account
                update_query = """UPDATE users SET status = 'active', is_verified = 1, 
                                 activation_code = NULL, activation_code_expiry = NULL, 
                                 updated_at = %s WHERE id = %s"""
                cursor.execute(update_query, (datetime.now(), user_id))
                connection.commit()
                
                logger.info(f"User {email} account activated successfully")
                return True, "Account activated successfully!"
            else:
                return False, "Invalid activation code. Please check and try again."
                
        except Error as e:
            logger.error(f"Database error verifying activation code: {e}")
            return False, "An error occurred. Please try again."
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False, "Database connection failed. Please try again."

def get_user_by_email(email):
    """Get user information by email"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT first_name, last_name, company_name, user_type FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Database error getting user: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

# Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Back Link
    html.A([
        html.I(className="fas fa-arrow-left"),
        " Back to Login"
    ], href="/login/", className="back-link"),
    
    html.Div([
        html.Div([
            # Brand Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-shield-alt")
                ], className="brand-icon"),
                html.H1("Account Activation", className="brand-title"),
                html.P("Secure your account with email verification", className="brand-subtitle")
            ], className="brand-header"),
            
            # Step Indicator
            html.Div([
                html.Div("1", className="step active", id="step-1"),
                html.Div("2", className="step inactive", id="step-2")
            ], className="step-indicator"),
            
            # Messages
            html.Div(id="activation-messages"),
            
            # Step 1: Email Input
            html.Div([
                html.Div([
                    html.I(className="fas fa-envelope"),
                    "Enter Email Address"
                ], className="section-title"),
                
                html.Div([
                    html.Label("Email Address", className="form-label"),
                    dcc.Input(
                        id="email-input",
                        type="email",
                        placeholder="Enter your registered email address",
                        className="form-input",
                        value="",
                        disabled=False
                    )
                ], className="form-group"),
                
                html.Button(
                    "Send Activation Code",
                    id="send-code-btn",
                    className="btn-primary",
                    n_clicks=0
                )
            ], className="form-section", id="email-section"),
            
            # Step 2: Code Verification (Initially Hidden)
            html.Div([
                html.Div([
                    html.I(className="fas fa-key"),
                    "Enter Activation Code"
                ], className="section-title"),
                
                html.Div([
                    html.H6([
                        html.I(className="fas fa-info-circle"),
                        "Check Your Email"
                    ]),
                    html.P("We've sent a 6-digit activation code to your email address. The code will expire in 15 minutes.")
                ], className="info-box"),
                
                html.Div([
                    html.Label("Activation Code", className="form-label"),
                    dcc.Input(
                        id="activation-code-input",
                        type="text",
                        placeholder="Enter 6-digit code",
                        className="form-input",
                        maxLength=6,
                        value=""
                    )
                ], className="form-group"),
                
                html.Button(
                    "Verify Code",
                    id="verify-code-btn",
                    className="btn-primary",
                    n_clicks=0
                ),
                
                html.Button(
                    "Resend Code",
                    id="resend-code-btn",
                    className="btn-secondary",
                    n_clicks=0
                )
            ], className="form-section", id="code-section", style={"display": "none"})
            
        ], className="activation-card")
    ], className="main-container"),
    
    # Hidden div to store email for step 2
    html.Div(id="stored-email", style={"display": "none"})
])

# Callback to handle URL parameters and pre-fill email
@app.callback(
    Output("email-input", "value"),
    Output("email-input", "disabled"),
    Input("url", "search")
)
def handle_url_params(search):
    if search:
        # Parse URL parameters
        params = {}
        if search.startswith("?"):
            search = search[1:]
        for param in search.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value.replace("%40", "@")  # Decode @ symbol
        
        if "email" in params:
            return params["email"], True  # Pre-fill and disable editing
    
    return "", False  # Empty and enabled

# Callback to send activation code
@app.callback(
    Output("activation-messages", "children"),
    Output("email-section", "style"),
    Output("code-section", "style"),
    Output("step-1", "className"),
    Output("step-2", "className"),
    Output("stored-email", "children"),
    Input("send-code-btn", "n_clicks"),
    State("email-input", "value")
)
def send_activation_code(n_clicks, email):
    if n_clicks > 0 and email:
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            error_msg = html.Div("Please enter a valid email address.", className="error-message")
            return error_msg, {"display": "block"}, {"display": "none"}, "step active", "step inactive", ""
        
        # Check if user exists
        user_info = get_user_by_email(email)
        if not user_info:
            error_msg = html.Div("No account found with this email address.", className="error-message")
            return error_msg, {"display": "block"}, {"display": "none"}, "step active", "step inactive", ""
        
        # Generate and send activation code
        activation_code = generate_activation_code()
        first_name = user_info[0] if user_info[0] else None
        
        if update_user_activation_code(email, activation_code):
            if send_activation_email(email, activation_code, first_name):
                success_msg = html.Div(
                    "Activation code sent successfully! Please check your email.",
                    className="success-message"
                )
                return success_msg, {"display": "none"}, {"display": "block"}, "step completed", "step active", email
            else:
                error_msg = html.Div("Activation code sent successfully! Please check your email.", className="success-message")
                return error_msg, {"display": "block"}, {"display": "none"}, "step active", "step inactive", ""
        else:
            error_msg = html.Div("Failed to generate activation code. Please try again.", className="success-message")
            return error_msg, {"display": "block"}, {"display": "none"}, "step active", "step inactive", ""
    
    return "", {"display": "block"}, {"display": "none"}, "step active", "step inactive", ""

# Callback to verify activation code
@app.callback(
    Output("activation-messages", "children", allow_duplicate=True),
    Input("verify-code-btn", "n_clicks"),
    State("activation-code-input", "value"),
    State("stored-email", "children"),
    prevent_initial_call=True
)
def verify_code(n_clicks, code, stored_email):
    if n_clicks > 0 and code and stored_email:
        # Validate code format
        if len(code) != 6 or not code.isdigit():
            return html.Div("Please enter a valid 6-digit code.", className="error-message")
        
        # Verify the code
        success, message = verify_activation_code(stored_email, code)
        
        if success:
            success_msg = html.Div([
                html.Div(message, className="success-message"),
                html.Div([
                    "Your account has been activated successfully! You can now login to access your dashboard."
                ], style={"text-align": "center", "margin-top": "20px", "color": "var(--text-gray)"}),
                html.A(
                    "Go to Login",
                    href="/login/",
                    className="btn-primary",
                    style={"display": "inline-block", "text-decoration": "none", "margin-top": "20px"}
                )
            ])
        else:
            return html.Div(message, className="error-message")
    
    return ""

# Callback to resend activation code
@app.callback(
    Output("activation-messages", "children", allow_duplicate=True),
    Input("resend-code-btn", "n_clicks"),
    State("stored-email", "children"),
    prevent_initial_call=True
)
def resend_code(n_clicks, stored_email):
    if n_clicks > 0 and stored_email:
        # Get user info
        user_info = get_user_by_email(stored_email)
        if user_info:
            # Generate and send new activation code
            activation_code = generate_activation_code()
            first_name = user_info[0] if user_info[0] else None
            
            if update_user_activation_code(stored_email, activation_code):
                if send_activation_email(stored_email, activation_code, first_name):
                    return html.Div(
                        "New activation code sent successfully! Please check your email.",
                        className="success-message"
                    )
                else:
                    return html.Div("Failed to send activation email. Please try again.", className="error-message")
            else:
                return html.Div("Failed to generate activation code. Please try again.", className="error-message")
        else:
            return html.Div("User not found. Please try again.", className="error-message")
    
    return ""

# Callback to format activation code input (add spaces for better readability)
@app.callback(
    Output("activation-code-input", "value"),
    Input("activation-code-input", "value"),
    prevent_initial_call=True
)
def format_activation_code(value):
    if value:
        # Remove any non-digit characters
        digits_only = ''.join(filter(str.isdigit, value))
        # Limit to 6 digits
        return digits_only[:6]
    return value

if __name__ == '__main__':
    app.run_server(debug=True)