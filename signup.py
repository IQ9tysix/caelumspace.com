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
from datetime import datetime
import logging
from server import server

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/signup/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection function with connection pooling
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='warehouse_db',
            user='root',
            password='',  # Consider using environment variables
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False,
            pool_name='warehouse_pool',
            pool_size=5,
            pool_reset_session=True
        )
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

# Improved password hashing with salt
def hash_password(password):
    salt = os.urandom(32)  # 32 bytes = 256 bits
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + pwdhash

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to validate phone number (improved)
def is_valid_phone(phone):
    # Remove all non-digit characters
    cleaned_phone = re.sub(r'\D', '', phone)
    # Check if it's between 10-15 digits
    return len(cleaned_phone) >= 10 and len(cleaned_phone) <= 15

# Function to validate password strength
def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

# Function to validate CAC number
def is_valid_cac(cac_number):
    # CAC number should be alphanumeric and between 6-10 characters
    return re.match(r'^[A-Z0-9]{6,10}$', cac_number.upper()) is not None

# Improved file save function with better error handling
def save_file(file_content, filename):
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{secure_filename(filename)}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Check file size (limit to 5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise ValueError("File size exceeds 5MB limit")
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"File saved successfully: {unique_filename}")
        return unique_filename
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

# Function to create file preview
def create_file_preview(contents, filename):
    if not contents or not filename:
        return html.Div()
    
    try:
        content_type, content_string = contents.split(',')
        file_size = len(base64.b64decode(content_string))
        file_size_mb = file_size / (1024 * 1024)
        
        preview = html.Div([
            html.I(className="fas fa-file", style={"color": "#28a745", "fontSize": "24px"}),
            html.Div([
                html.Strong(filename),
                html.Br(),
                html.Small(f"Size: {file_size_mb:.2f} MB")
            ], style={"marginLeft": "10px"})
        ], style={
            "display": "flex",
            "alignItems": "center",
            "padding": "10px",
            "border": "1px solid #ddd",
            "borderRadius": "5px",
            "backgroundColor": "#f8f9fa",
            "marginTop": "10px"
        })
        
        return preview
    except:
        return html.Div()

# Initialize Dash app
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Add CSS styles for the application
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            /* Global Styles */
            :root {
                --primary-yellow: #FFC107; /* A slightly softer yellow */
                --light-yellow-outline: rgba(255, 193, 7, 0.3); /* Light yellow for outlines */
                --dark-text: #343a40;
                --light-text: #ffffff;
                --medium-text: #6c757d;
                --light-background: #ffffff;
                --border-color: #e9ecef;
                --hover-border: #adb5bd;
                --button-bg: #495057; /* Darker, more mature button background */
                --button-hover-bg: #343a40;
                --success-color: #28a745;
                --error-color: #dc3545;
                --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                --transition-speed: 0.3s ease-in-out;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Poppins', sans-serif;
                background-color: var(--light-background); /* White background */
                min-height: 100vh;
                # display: flex;
                # flex-direction: column;
                justify-content: center;
                align-items: center;
                color: var(--dark-text);
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            /* Container for the entire signup form */
            .signup-container {
                max-width: 950px; /* Slightly wider for better spacing */
                width: 95%;
                margin: 30px auto;
                padding: 20px;
                background: var(--light-background);
                border-radius: 15px;
                box-shadow: var(--card-shadow);
                transition: transform var(--transition-speed);
            }

            .signup-container:hover {
                transform: translateY(-5px);
            }

            /* Header Section */
            .form-header {
                text-align: center;
                margin-bottom: 10px;
            }

            .form-title {
                color: var(--dark-text);
                font-size: 1.8rem; /* Larger, more impactful title */
                font-weight: 700;
                margin-bottom: 5px;
                letter-spacing: -0.5px;
            }

            .form-subtitle {
                color: var(--medium-text);
                font-size: 1.15rem; /* Clear and readable subtitle */
                font-weight: 400;
                line-height: 0.6;
            }

            /* Tab Buttons for Signup Type */
            .signup-type-buttons {
                display: flex;
                gap: 15px; /* More space between buttons */
                margin-bottom: 35px;
                justify-content: center;
                background-color: #f1f3f5; /* Light grey background for tabs */
                padding: 8px;
                border-radius: 12px;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
            }

            .signup-type-btn {
                flex: 1;
                max-width: 220px; /* Consistent width */
                padding: 12px 25px; /* Generous padding */
                border-radius: 10px; /* Softer corners */
                font-weight: 600;
                font-size: 1rem;
                background-color: transparent;
                border: none;
                color: var(--medium-text);
                cursor: pointer;
                transition: all var(--transition-speed);
                position: relative;
                overflow: hidden;
            }

            .signup-type-btn.active {
                background-color: var(--primary-yellow);
                color: var(--light-text);
                box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
                transform: translateY(-2px); /* Lift effect */
            }

            .signup-type-btn:not(.active):hover {
                color: var(--dark-text);
                background-color: rgba(255, 193, 7, 0.1); /* Light yellow hint on hover */
            }

            /* Form Sections and Inputs */
            .forms-container {
                background: var(--light-background); /* White background for internal forms */
                padding: 0; /* Padding handled by individual form-section */
                border-radius: 15px;
            }

            .form-section {
                padding: 30px; /* Consistent internal padding */
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); /* Subtle shadow */
                background: var(--light-background);
                transition: opacity 0.5s ease;
            }

            .form-label {
                font-weight: 600;
                color: var(--dark-text);
                margin-bottom: 8px;
                display: block; /* Ensures it takes full width */
                font-size: 0.95rem;
            }

            .form-label.required::after {
                content: " *";
                color: var(--error-color);
                font-size: 0.9em;
                vertical-align: super;
            }

            .form-input, .form-select {
                width: 100%;
                border: 1px solid var(--border-color);
                border-radius: 8px; /* Slightly more rounded inputs */
                padding: 12px 15px; /* Ample padding */
                font-size: 1rem;
                color: var(--dark-text);
                background-color: var(--light-background);
                transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
            }

            .form-input:focus, .form-select:focus {
                outline: none;
                border-color: var(--primary-yellow); /* Yellow outline */
                box-shadow: 0 0 0 3px var(--light-yellow-outline); /* Soft yellow glow */
            }

            .form-input:hover, .form-select:hover {
                border-color: var(--hover-border);
            }

            /* Validation Feedback */
            .password-strong, .email-valid, .phone-valid, .cac-valid {
                border-color: var(--success-color) !important;
            }

            .password-weak, .email-invalid, .phone-invalid, .cac-invalid {
                border-color: var(--error-color) !important;
            }

            .password-match {
                border-color: var(--success-color) !important;
            }

            .password-mismatch {
                border-color: var(--error-color) !important;
            }

            /* File Upload */
            .file-upload {
                border: 2px dashed var(--border-color);
                border-radius: 10px;
                padding: 30px; /* More padding for a larger drop zone */
                text-align: center;
                cursor: pointer;
                transition: all var(--transition-speed);
                background: #fdfdfd;
                margin-top: 15px;
            }

            .file-upload:hover {
                border-color: var(--primary-yellow);
                background: rgba(255, 193, 7, 0.05); /* Very light yellow background on hover */
            }

            .file-upload i {
                font-size: 48px;
                color: var(--primary-yellow); /* Yellow icon */
                margin-bottom: 15px;
            }

            .file-upload-text {
                font-size: 1.05rem;
                font-weight: 500;
                color: var(--dark-text);
            }

            .file-upload-subtext {
                font-size: 0.85rem;
                color: var(--medium-text);
                margin-top: 5px;
            }

            /* Terms and Conditions */
            .terms-section {
                background: #f8f9fa; /* Light background for terms */
                padding: 25px;
                border-radius: 10px;
                margin-top: 25px;
                margin-bottom: 10px;
                border: 1px solid #e0e0e0;
            }

            .form-checkbox {
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }

            .form-checkbox input[type="checkbox"] {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                border: 1px solid var(--border-color);
                border-radius: 4px;
                appearance: none; /* Hide default checkbox */
                -webkit-appearance: none;
                cursor: pointer;
                position: relative;
                transition: all var(--transition-speed);
            }

            .form-checkbox input[type="checkbox"]:checked {
                background-color: var(--primary-yellow);
                border-color: var(--primary-yellow);
            }

            .form-checkbox input[type="checkbox"]:checked::before {
                content: '\\f00c'; /* Font Awesome check icon */
                font-family: 'Font Awesome 6 Free';
                font-weight: 900;
                color: var(--dark-text);
                font-size: 14px;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }

            .form-checkbox label {
                font-size: 0.95rem;
                color: var(--medium-text);
                cursor: pointer;
            }

            .form-checkbox label a {
                color: var(--primary-yellow);
                text-decoration: none;
                font-weight: 600;
            }

            .form-checkbox label a:hover {
                text-decoration: underline;
            }

            /* Submit Button */
            .submit-btn {
                width: 100%;
                padding: 16px; /* Larger hit area */
                font-size: 1.15rem;
                font-weight: 600;
                border-radius: 10px;
                background-color: var(--button-bg); /* Muted, professional color */
                border: none;
                color: white;
                cursor: pointer;
                transition: all var(--transition-speed);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
                letter-spacing: 0.5px;
            }

            .submit-btn:hover {
                background-color: var(--button-hover-bg); /* Darker on hover */
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            }

            .submit-btn:active {
                transform: translateY(0);
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .submit-btn:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
                box-shadow: none;
                transform: none;
            }

            /* Authentication Footer */
            .auth-footer {
                text-align: center;
                margin-top: 30px;
                font-size: 0.95rem;
                color: var(--medium-text);
            }

            .auth-link {
                color: var(--primary-yellow);
                text-decoration: none;
                font-weight: 600;
                transition: color var(--transition-speed), text-decoration var(--transition-speed);
            }

            .auth-link:hover {
                color: #e0a800; /* Slightly darker yellow on hover */
                text-decoration: underline;
            }

            /* Message Containers */
            .message-container {
                margin-bottom: 25px;
                min-height: 40px; /* Ensure space even when empty */
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .success-message {
                background: #d4edda;
                color: var(--success-color);
                border: 1px solid #c3e6cb;
                padding: 15px 20px;
                border-radius: 8px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .error-message {
                background: #f8d7da;
                color: var(--error-color);
                border: 1px solid #f5c6cb;
                padding: 15px 20px;
                border-radius: 8px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .success-message i, .error-message i {
                font-size: 1.2rem;
            }

            /* Responsive Adjustments */
            @media (max-width: 768px) {
                .signup-container {
                    padding: 25px;
                    margin: 20px auto;
                }

                .form-title {
                    font-size: 2.2rem;
                }

                .form-subtitle {
                    font-size: 1rem;
                }

                .signup-type-buttons {
                    flex-direction: column;
                    gap: 10px;
                }

                .signup-type-btn {
                    max-width: 100%;
                    padding: 10px 20px;
                }

                .form-section {
                    padding: 20px;
                }

                .submit-btn {
                    font-size: 1rem;
                    padding: 14px;
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

app.layout = html.Div([
    # Store components for state management
    dcc.Store(id='signup-type', data='individual'),
    dcc.Store(id='signup-message', data=''),
    dcc.Store(id='signup-message-type', data=''),
    

    # Main container
    dbc.Container([
        dbc.Row([
            dbc.Col([
                # Main signup container
                html.Div([
                    # Header section
                    html.Div([
                        html.H3("Sign up", className="form-title"),
                        html.P("Create your account to get started", className="form-subtitle")
                    ], className="form-header"),
                    
                    # Success/Error messages
                    html.Div(id="message-container", className="message-container"),
                    
                    # Signup type buttons
                    html.Div([
                        dbc.Button("Individual Account", id="individual-btn", className="signup-type-btn active", size="lg"),
                        dbc.Button("Corporate Account", id="corporate-btn", className="signup-type-btn", size="lg")
                    ], className="signup-type-buttons"),
                    
                    # Forms container
                    html.Div([
                        # Individual signup form
                        html.Div([
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("First Name", className="form-label required"),
                                        dbc.Input(
                                            id="first-name",
                                            type="text",
                                            placeholder="Enter your first name",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Last Name", className="form-label required"),
                                        dbc.Input(
                                            id="last-name",
                                            type="text",
                                            placeholder="Enter your last name",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Email Address", className="form-label required"),
                                        dbc.Input(
                                            id="email",
                                            type="email",
                                            placeholder="Enter your email address",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Phone Number", className="form-label required"),
                                        dbc.Input(
                                            id="phone",
                                            type="tel",
                                            placeholder="Enter your phone number",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Password", className="form-label required"),
                                        dbc.Input(
                                            id="password",
                                            type="password",
                                            placeholder="Create a password",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Confirm Password", className="form-label required"),
                                        dbc.Input(
                                            id="confirm-password",
                                            type="password",
                                            placeholder="Confirm your password",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Residential Address", className="form-label required"),
                                        dbc.Input(
                                            id="address",
                                            type="text",
                                            placeholder="Enter your residential address",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Country", className="form-label required"),
                                        dbc.Select(
                                            id="country",
                                            options=[
                                                {"label": "Select Country", "value": ""},
                                                {"label": "Nigeria", "value": "NG"},
                                                {"label": "United States", "value": "US"},
                                                {"label": "United Kingdom", "value": "UK"},
                                                {"label": "Canada", "value": "CA"},
                                                {"label": "Australia", "value": "AU"}
                                            ],
                                            value="",
                                            className="form-select",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("State/Province", className="form-label required"),
                                        dbc.Select(
                                            id="state",
                                            options=[
                                                {"label": "Select State/Province", "value": ""},
                                                {"label": "Lagos", "value": "Lagos"},
                                                {"label": "Abuja", "value": "Abuja"},
                                                {"label": "Kano", "value": "Kano"},
                                                {"label": "Rivers", "value": "Rivers"},
                                                {"label": "Ogun", "value": "Ogun"}
                                            ],
                                            value="",
                                            className="form-select",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("City", className="form-label required"),
                                        dbc.Input(
                                            id="city",
                                            type="text",
                                            placeholder="Enter your city",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("ID Type", className="form-label required"),
                                        dbc.Select(
                                            id="id-type",
                                            options=[
                                                {"label": "Select ID Type", "value": ""},
                                                {"label": "National ID (NIN)", "value": "NIN"},
                                                {"label": "International Passport", "value": "passport"},
                                                {"label": "Driver's License", "value": "license"}
                                            ],
                                            value="",
                                            className="form-select",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("ID Number", className="form-label required"),
                                        dbc.Input(
                                            id="id-number",
                                            type="text",
                                            placeholder="Enter your ID number",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Upload ID Document", className="form-label required"),
                                        dcc.Upload(
                                            id="id-document",
                                            children=html.Div([
                                                html.I(className="fas fa-cloud-upload-alt"),
                                                html.Br(),
                                                html.Span("Click to upload ID document (Max 5MB)")
                                            ]),
                                            className="file-upload",
                                            accept=".jpg,.jpeg,.png,.pdf"
                                        ),
                                        html.Div(id="id-document-preview")
                                    ], width=12)
                                ], className="mb-3")
                            ], className="form-section")
                        ], id="individual-form"),
                        
                        # Corporate signup form
                        html.Div([
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Company Name", className="form-label required"),
                                        dbc.Input(
                                            id="company-name",
                                            type="text",
                                            placeholder="Enter company name",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("CAC Registration Number", className="form-label required"),
                                        dbc.Input(
                                            id="cac-number",
                                            type="text",
                                            placeholder="Enter CAC number",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Business Address", className="form-label required"),
                                        dbc.Input(
                                            id="business-address",
                                            type="text",
                                            placeholder="Enter business address",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Contact Person First Name", className="form-label required"),
                                        dbc.Input(
                                            id="contact-first-name",
                                            type="text",
                                            placeholder="Enter contact person's first name",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Contact Person Last Name", className="form-label required"),
                                        dbc.Input(
                                            id="contact-last-name",
                                            type="text",
                                            placeholder="Enter contact person's last name",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Contact Email", className="form-label required"),
                                        dbc.Input(
                                            id="contact-email",
                                            type="email",
                                            placeholder="Enter contact email address",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Contact Phone", className="form-label required"),
                                        dbc.Input(
                                            id="contact-phone",
                                            type="tel",
                                            placeholder="Enter contact phone number",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Company Password", className="form-label required"),
                                        dbc.Input(
                                            id="company-password",
                                            type="password",
                                            placeholder="Create a password",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Confirm Password", className="form-label required"),
                                        dbc.Input(
                                            id="company-confirm-password",
                                            type="password",
                                            placeholder="Confirm your password",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Country", className="form-label required"),
                                        dbc.Select(
                                            id="company-country",
                                            options=[
                                                {"label": "Select Country", "value": ""},
                                                {"label": "Nigeria", "value": "NG"},
                                                {"label": "United States", "value": "US"},
                                                {"label": "United Kingdom", "value": "UK"},
                                                {"label": "Canada", "value": "CA"},
                                                {"label": "Australia", "value": "AU"}
                                            ],
                                            value="",
                                            className="form-select",
                                            required=True
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("State/Province", className="form-label required"),
                                        dbc.Select(
                                            id="company-state",
                                            options=[
                                                {"label": "Select State/Province", "value": ""},
                                                {"label": "Lagos", "value": "Lagos"},
                                                {"label": "Abuja", "value": "Abuja"},
                                                {"label": "Kano", "value": "Kano"},
                                                {"label": "Rivers", "value": "Rivers"},
                                                {"label": "Ogun", "value": "Ogun"}
                                            ],
                                            value="",
                                            className="form-select",
                                            required=True
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("City", className="form-label required"),
                                        dbc.Input(
                                            id="company-city",
                                            type="text",
                                            placeholder="Enter city",
                                            className="form-input",
                                            required=True
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Upload Business Document (CAC Certificate)", className="form-label required"),
                                        dcc.Upload(
                                            id="business-document",
                                            children=html.Div([
                                                html.I(className="fas fa-cloud-upload-alt"),
                                                html.Br(),
                                                html.Span("Click to upload business document (Max 5MB)")
                                            ]),
                                            className="file-upload",
                                            accept=".jpg,.jpeg,.png,.pdf"
                                        ),
                                        html.Div(id="business-document-preview")
                                    ], width=12)
                                ], className="mb-3")
                            ], className="form-section")
                        ], id="corporate-form", style={"display": "none"}),
                        
                        # Terms and conditions
                        html.Div([
                            dbc.Checklist(
                                id="privacy-policy",
                                options=[{"label": "I agree to the Privacy Policy", "value": "agreed"}],
                                value=[],
                                inline=True,
                                className="form-checkbox"
                            ),
                            dbc.Checklist(
                                id="terms-conditions",
                                options=[{"label": "I accept the Terms & Conditions", "value": "accepted"}],
                                value=[],
                                inline=True,
                                className="form-checkbox"
                            )
                        ], className="terms-section"),
                        
                        # Submit button
                        dbc.Button(
                            "Create Account",
                            id="submit-btn",
                            className="submit-btn",
                            size="lg",
                            disabled=False
                        ),
                        
                        # Sign in link
                        html.Div([
                            html.P([
                                "Already have an account? ",
                                html.A("Sign In", href="/login", className="auth-link")
                            ])
                        ], className="auth-footer")
                    ], className="forms-container")
                ], className="signup-container")
            ], width=12)
        ])
    ], fluid=True)
])

# Callback for file preview - ID document
@app.callback(
    Output('id-document-preview', 'children'),
    Input('id-document', 'contents'),
    State('id-document', 'filename')
)
def update_id_document_preview(contents, filename):
    return create_file_preview(contents, filename)

# Callback for file preview - Business document
@app.callback(
    Output('business-document-preview', 'children'),
    Input('business-document', 'contents'),
    State('business-document', 'filename')
)
def update_business_document_preview(contents, filename):
    return create_file_preview(contents, filename)

# Enhanced form submission callback with corporate support
@app.callback(
    Output('message-container', 'children'),
    [Input('submit-btn', 'n_clicks')],
    [State('signup-type', 'data'),
     # Individual fields
     State('first-name', 'value'),
     State('last-name', 'value'),
     State('email', 'value'),
     State('phone', 'value'),
     State('password', 'value'),
     State('confirm-password', 'value'),
     State('address', 'value'),
     State('country', 'value'),
     State('state', 'value'),
     State('city', 'value'),
     State('id-type', 'value'),
     State('id-number', 'value'),
     State('id-document', 'contents'),
     State('id-document', 'filename'),
     # Corporate fields
     State('company-name', 'value'),
     State('cac-number', 'value'),
     State('business-address', 'value'),
     State('contact-first-name', 'value'),
     State('contact-last-name', 'value'),
     State('contact-email', 'value'),
     State('contact-phone', 'value'),
     State('company-password', 'value'),
     State('company-confirm-password', 'value'),
     State('company-country', 'value'),
     State('company-state', 'value'),
     State('company-city', 'value'),
     State('business-document', 'contents'),
     State('business-document', 'filename'),
     # Common fields
     State('privacy-policy', 'value'),
     State('terms-conditions', 'value')]
)
def handle_signup(n_clicks, signup_type, 
                 # Individual fields
                 first_name, last_name, email, phone, password, confirm_password, 
                 address, country, state, city, id_type, id_number, id_document, id_filename,
                 # Corporate fields
                 company_name, cac_number, business_address, contact_first_name, contact_last_name,
                 contact_email, contact_phone, company_password, company_confirm_password,
                 company_country, company_state, company_city, business_document, business_filename,
                 # Common fields
                 privacy_policy, terms_conditions):
    
    if not n_clicks:
        return ""
    
    # Enhanced validation
    if not privacy_policy or not terms_conditions:
        return html.Div("Please agree to the Privacy Policy and Terms & Conditions", 
                       className="error-message")
    
    try:
        if signup_type == 'individual':
            # Individual validation
            if not all([first_name, last_name, email, phone, password, confirm_password, 
                       address, country, state, city, id_type, id_number]):
                return html.Div("Please fill in all required fields", className="error-message")
            
            # Password validation
            if password != confirm_password:
                return html.Div("Passwords do not match", className="error-message")
            
            is_strong, message = is_strong_password(password)
            if not is_strong:
                return html.Div(message, className="error-message")
            
            # File validation
            if not id_document or not id_filename:
                return html.Div("Please upload your ID document", className="error-message")
            
            # Email validation
            if not is_valid_email(email):
                return html.Div("Please enter a valid email address", className="error-message")
            
            # Phone validation
            if not is_valid_phone(phone):
                return html.Div("Please enter a valid phone number", className="error-message")
            
            # Process file upload
            try:
                content_type, content_string = id_document.split(',')
                decoded = base64.b64decode(content_string)
                id_document_filename = save_file(decoded, id_filename)
                
                if not id_document_filename:
                    return html.Div("Error uploading ID document", className="error-message")
            except Exception as e:
                return html.Div(f"Error processing file upload: {str(e)}", className="error-message")
            
            # Database operations
            connection = get_db_connection()
            if not connection:
                return html.Div("Database connection error", className="error-message")
            
            try:
                cursor = connection.cursor()
                connection.start_transaction()
                
                # Check if email already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
                if cursor.fetchone()[0] > 0:
                    return html.Div("Email address already exists", className="error-message")
                
                # Insert individual user
                query = """
                INSERT INTO users (user_type, first_name, last_name, email, phone, password_hash, 
                                 address, country, state, city, id_type, id_number, id_document_path, 
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    'individual', first_name, last_name, email, phone, hash_password(password),
                    address, country, state, city, id_type, id_number, id_document_filename,
                    datetime.now(), datetime.now()
                )
                
                cursor.execute(query, values)
                connection.commit()
                

                # For Individual User Success Message:
                logger.info(f"Individual user {email} successfully registered")
                activation_link = f"/activate_account/?email={email}"
                return html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={"color": "#00FF88", "font-size": "24px", "margin-right": "10px"}),
                        f"Congratulations {first_name}! Your account has been created successfully."
                    ], style={"margin-bottom": "15px", "display": "flex", "align-items": "center"}),
                    html.Div([
                        "To secure your account and access your dashboard, please verify your email address."
                    ], style={"margin-bottom": "20px", "color": "#CCCCCC"}),
                    html.A(
                        "Verify Email Address",
                        href=activation_link,
                        className="btn-primary",
                        style={
                            "display": "inline-block",
                            "text-decoration": "none",
                            "padding": "12px 30px",
                            "background": "linear-gradient(135deg, #FFD700, #FFA500)",
                            "color": "#0A0A0A",
                            "border-radius": "8px",
                            "font-weight": "600",
                            "text-transform": "uppercase",
                            "letter-spacing": "1px",
                            "transition": "all 0.3s ease"
                        }
                    )
                ], className="success-message")
                
            except Error as e:
                connection.rollback()
                logger.error(f"Database error during individual signup: {e}")
                return html.Div("Error creating account. Please try again.", className="error-message")
            finally:
                cursor.close()
                connection.close()
        
        elif signup_type == 'corporate':
            # Corporate validation
            if not all([company_name, cac_number, business_address, contact_first_name, contact_last_name,
                       contact_email, contact_phone, company_password, company_confirm_password,
                       company_country, company_state, company_city]):
                return html.Div("Please fill in all required fields", className="error-message")
            
            # Password validation
            if company_password != company_confirm_password:
                return html.Div("Passwords do not match", className="error-message")
            
            is_strong, message = is_strong_password(company_password)
            if not is_strong:
                return html.Div(message, className="error-message")
            
            # Email validation
            if not is_valid_email(contact_email):
                return html.Div("Please enter a valid contact email address", className="error-message")
            
            # Phone validation
            if not is_valid_phone(contact_phone):
                return html.Div("Please enter a valid contact phone number", className="error-message")
            
            # CAC validation
            if not is_valid_cac(cac_number):
                return html.Div("Please enter a valid CAC number", className="error-message")
            
            # File validation
            if not business_document or not business_filename:
                return html.Div("Please upload your business document", className="error-message")
            
            # Process file upload
            try:
                content_type, content_string = business_document.split(',')
                decoded = base64.b64decode(content_string)
                business_document_filename = save_file(decoded, business_filename)
                
                if not business_document_filename:
                    return html.Div("Error uploading business document", className="error-message")
            except Exception as e:
                return html.Div(f"Error processing file upload: {str(e)}", className="error-message")
            
            # Database operations
            connection = get_db_connection()
            if not connection:
                return html.Div("Database connection error", className="error-message")
            
            try:
                cursor = connection.cursor()
                connection.start_transaction()
                
                # Check if email already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s OR contact_email = %s",
                              (contact_email, contact_email))
                if cursor.fetchone()[0] > 0:
                    return html.Div("Email address already exists", className="error-message")
                
                # Check if CAC number already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE cac_number = %s", (cac_number,))
                if cursor.fetchone()[0] > 0:
                    return html.Div("CAC number already exists", className="error-message")
                
                # Insert corporate user
                query = """
                INSERT INTO users (user_type, company_name, cac_number, business_address, 
                                 contact_first_name, contact_last_name, contact_email, contact_phone, 
                                 password_hash, country, state, city, business_document_path, 
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    'corporate', company_name, cac_number, business_address,
                    contact_first_name, contact_last_name, contact_email, contact_phone,
                    hash_password(company_password), company_country, company_state, company_city,
                    business_document_filename, datetime.now(), datetime.now()
                )
                
                cursor.execute(query, values)
                connection.commit()
                

                # For Corporate User Success Message:
                logger.info(f"Corporate user {company_name} successfully registered")
                activation_link = f"/activate_account/?email={email}"
                return html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle", style={"color": "#00FF88", "font-size": "24px", "margin-right": "10px"}),
                        f"Congratulations! Corporate account for {company_name} has been created successfully."
                    ], style={"margin-bottom": "15px", "display": "flex", "align-items": "center"}),
                    html.Div([
                        "To secure your account and access your dashboard, please verify your email address."
                    ], style={"margin-bottom": "20px", "color": "#CCCCCC"}),
                    html.A(
                        "Verify Email Address",
                        href=activation_link,
                        className="btn-primary",
                        style={
                            "display": "inline-block",
                            "text-decoration": "none",
                            "padding": "12px 30px",
                            "background": "linear-gradient(135deg, #FFD700, #FFA500)",
                            "color": "#0A0A0A",
                            "border-radius": "8px",
                            "font-weight": "600",
                            "text-transform": "uppercase",
                            "letter-spacing": "1px",
                            "transition": "all 0.3s ease"
                        }
                    )
                ], className="success-message")
                
            except Error as e:
                connection.rollback()
                logger.error(f"Database error during corporate signup: {e}")
                return html.Div("Error creating account. Please try again.", className="error-message")
            finally:
                cursor.close()
                connection.close()
    
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        return html.Div("An unexpected error occurred. Please try again.", className="error-message")

# Callback for switching between individual and corporate forms
@app.callback(
    [Output('individual-btn', 'className'),
     Output('corporate-btn', 'className'),
     Output('individual-form', 'style'),
     Output('corporate-form', 'style'),
     Output('signup-type', 'data')],
    [Input('individual-btn', 'n_clicks'),
     Input('corporate-btn', 'n_clicks')],
    [State('signup-type', 'data')]
)
def toggle_signup_type(individual_clicks, corporate_clicks, current_type):
    ctx = callback_context
    if not ctx.triggered:
        return 'signup-type-btn active', 'signup-type-btn', {'display': 'block'}, {'display': 'none'}, 'individual'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'individual-btn':
        return ('signup-type-btn active', 'signup-type-btn', 
                {'display': 'block'}, {'display': 'none'}, 'individual')
    elif button_id == 'corporate-btn':
        return ('signup-type-btn', 'signup-type-btn active', 
                {'display': 'none'}, {'display': 'block'}, 'corporate')
    
    # Default return
    return 'signup-type-btn active', 'signup-type-btn', {'display': 'block'}, {'display': 'none'}, 'individual'

# Callback for real-time password validation
@app.callback(
    Output('password', 'className'),
    Input('password', 'value')
)
def validate_password_strength(password):
    if not password:
        return 'form-input'
    
    is_strong, _ = is_strong_password(password)
    if is_strong:
        return 'form-input password-strong'
    else:
        return 'form-input password-weak'

# Callback for real-time password validation (corporate)
@app.callback(
    Output('company-password', 'className'),
    Input('company-password', 'value')
)
def validate_company_password_strength(password):
    if not password:
        return 'form-input'
    
    is_strong, _ = is_strong_password(password)
    if is_strong:
        return 'form-input password-strong'
    else:
        return 'form-input password-weak'

# Callback for password confirmation validation
@app.callback(
    Output('confirm-password', 'className'),
    [Input('confirm-password', 'value'),
     Input('password', 'value')]
)
def validate_password_confirmation(confirm_password, password):
    if not confirm_password:
        return 'form-input'
    
    if confirm_password == password:
        return 'form-input password-match'
    else:
        return 'form-input password-mismatch'

# Callback for corporate password confirmation validation
@app.callback(
    Output('company-confirm-password', 'className'),
    [Input('company-confirm-password', 'value'),
     Input('company-password', 'value')]
)
def validate_company_password_confirmation(confirm_password, password):
    if not confirm_password:
        return 'form-input'
    
    if confirm_password == password:
        return 'form-input password-match'
    else:
        return 'form-input password-mismatch'

# Callback for email validation
@app.callback(
    Output('email', 'className'),
    Input('email', 'value')
)
def validate_email_input(email):
    if not email:
        return 'form-input'
    
    if is_valid_email(email):
        return 'form-input email-valid'
    else:
        return 'form-input email-invalid'

# Callback for corporate email validation
@app.callback(
    Output('contact-email', 'className'),
    Input('contact-email', 'value')
)
def validate_contact_email_input(email):
    if not email:
        return 'form-input'
    
    if is_valid_email(email):
        return 'form-input email-valid'
    else:
        return 'form-input email-invalid'

# Callback for phone validation
@app.callback(
    Output('phone', 'className'),
    Input('phone', 'value')
)
def validate_phone_input(phone):
    if not phone:
        return 'form-input'
    
    if is_valid_phone(phone):
        return 'form-input phone-valid'
    else:
        return 'form-input phone-invalid'

# Callback for corporate phone validation
@app.callback(
    Output('contact-phone', 'className'),
    Input('contact-phone', 'value')
)
def validate_contact_phone_input(phone):
    if not phone:
        return 'form-input'
    
    if is_valid_phone(phone):
        return 'form-input phone-valid'
    else:
        return 'form-input phone-invalid'

# Callback for CAC number validation
@app.callback(
    Output('cac-number', 'className'),
    Input('cac-number', 'value')
)
def validate_cac_input(cac):
    if not cac:
        return 'form-input'
    
    if is_valid_cac(cac):
        return 'form-input cac-valid'
    else:
        return 'form-input cac-invalid'

# Callback to update state options based on country selection
@app.callback(
    Output('state', 'options'),
    Input('country', 'value')
)
def update_state_options(country):
    if country == 'NG':
        return [
            {"label": "Select State", "value": ""},
            {"label": "Abia", "value": "Abia"},
            {"label": "Adamawa", "value": "Adamawa"},
            {"label": "Akwa Ibom", "value": "Akwa Ibom"},
            {"label": "Anambra", "value": "Anambra"},
            {"label": "Bauchi", "value": "Bauchi"},
            {"label": "Bayelsa", "value": "Bayelsa"},
            {"label": "Benue", "value": "Benue"},
            {"label": "Borno", "value": "Borno"},
            {"label": "Cross River", "value": "Cross River"},
            {"label": "Delta", "value": "Delta"},
            {"label": "Ebonyi", "value": "Ebonyi"},
            {"label": "Edo", "value": "Edo"},
            {"label": "Ekiti", "value": "Ekiti"},
            {"label": "Enugu", "value": "Enugu"},
            {"label": "FCT", "value": "FCT"},
            {"label": "Gombe", "value": "Gombe"},
            {"label": "Imo", "value": "Imo"},
            {"label": "Jigawa", "value": "Jigawa"},
            {"label": "Kaduna", "value": "Kaduna"},
            {"label": "Kano", "value": "Kano"},
            {"label": "Katsina", "value": "Katsina"},
            {"label": "Kebbi", "value": "Kebbi"},
            {"label": "Kogi", "value": "Kogi"},
            {"label": "Kwara", "value": "Kwara"},
            {"label": "Lagos", "value": "Lagos"},
            {"label": "Nasarawa", "value": "Nasarawa"},
            {"label": "Niger", "value": "Niger"},
            {"label": "Ogun", "value": "Ogun"},
            {"label": "Ondo", "value": "Ondo"},
            {"label": "Osun", "value": "Osun"},
            {"label": "Oyo", "value": "Oyo"},
            {"label": "Plateau", "value": "Plateau"},
            {"label": "Rivers", "value": "Rivers"},
            {"label": "Sokoto", "value": "Sokoto"},
            {"label": "Taraba", "value": "Taraba"},
            {"label": "Yobe", "value": "Yobe"},
            {"label": "Zamfara", "value": "Zamfara"}
        ]
    else:
        return [
            {"label": "Select State/Province", "value": ""},
            {"label": "State/Province 1", "value": "state1"},
            {"label": "State/Province 2", "value": "state2"}
        ]

# Callback to update corporate state options based on country selection
@app.callback(
    Output('company-state', 'options'),
    Input('company-country', 'value')
)
def update_company_state_options(country):
    if country == 'NG':
        return [
            {"label": "Select State", "value": ""},
            {"label": "Abia", "value": "Abia"},
            {"label": "Adamawa", "value": "Adamawa"},
            {"label": "Akwa Ibom", "value": "Akwa Ibom"},
            {"label": "Anambra", "value": "Anambra"},
            {"label": "Bauchi", "value": "Bauchi"},
            {"label": "Bayelsa", "value": "Bayelsa"},
            {"label": "Benue", "value": "Benue"},
            {"label": "Borno", "value": "Borno"},
            {"label": "Cross River", "value": "Cross River"},
            {"label": "Delta", "value": "Delta"},
            {"label": "Ebonyi", "value": "Ebonyi"},
            {"label": "Edo", "value": "Edo"},
            {"label": "Ekiti", "value": "Ekiti"},
            {"label": "Enugu", "value": "Enugu"},
            {"label": "FCT", "value": "FCT"},
            {"label": "Gombe", "value": "Gombe"},
            {"label": "Imo", "value": "Imo"},
            {"label": "Jigawa", "value": "Jigawa"},
            {"label": "Kaduna", "value": "Kaduna"},
            {"label": "Kano", "value": "Kano"},
            {"label": "Katsina", "value": "Katsina"},
            {"label": "Kebbi", "value": "Kebbi"},
            {"label": "Kogi", "value": "Kogi"},
            {"label": "Kwara", "value": "Kwara"},
            {"label": "Lagos", "value": "Lagos"},
            {"label": "Nasarawa", "value": "Nasarawa"},
            {"label": "Niger", "value": "Niger"},
            {"label": "Ogun", "value": "Ogun"},
            {"label": "Ondo", "value": "Ondo"},
            {"label": "Osun", "value": "Osun"},
            {"label": "Oyo", "value": "Oyo"},
            {"label": "Plateau", "value": "Plateau"},
            {"label": "Rivers", "value": "Rivers"},
            {"label": "Sokoto", "value": "Sokoto"},
            {"label": "Taraba", "value": "Taraba"},
            {"label": "Yobe", "value": "Yobe"},
            {"label": "Zamfara", "value": "Zamfara"}
        ]
    else:
        return [
            {"label": "Select State/Province", "value": ""},
            {"label": "State/Province 1", "value": "state1"},
            {"label": "State/Province 2", "value": "state2"}
        ]
