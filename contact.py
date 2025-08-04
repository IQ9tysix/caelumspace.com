import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import logging

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/contact/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
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
        /* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #1a1a1a;
    background-color: #ffffff;
    overflow-x: hidden;
}

/* Header Styles */
.main-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    transition: all 0.3s ease;
}

.header-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 80px;
}

.logo-container .logo {
    height: 50px;
    width: auto;
    object-fit: contain;
}

.nav-menu {
    display: flex;
    align-items: center;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 2rem;
    list-style: none;
}

.nav-link {
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 500;
    font-size: 0.95rem;
    padding: 0.5rem 0;
    position: relative;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-link:hover {
    color: #FFD700;
}

.nav-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: #FFD700;
    transition: width 0.3s ease;
}

.nav-link:hover::after {
    width: 100%;
}

.auth-link {
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.3s ease;
}

.auth-link:hover {
    background: #FFD700;
    color: #1a1a1a;
    border-color: #FFD700;
    transform: translateY(-1px);
}

.mobile-menu-toggle, .mobile-menu-close {
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #1a1a1a;
    cursor: pointer;
    padding: 0.5rem;
}

/* Contact Hero Section */
.contact-hero-section {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    padding: 120px 2rem 80px;
    position: relative;
    overflow: hidden;
}

.contact-hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,215,0,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}

.contact-hero-container {
    max-width: 1400px;
    margin: 0 auto;
    position: relative;
    z-index: 2;
}

.contact-hero-content {
    text-align: center;
    color: white;
    margin-bottom: 4rem;
}

.contact-hero-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeInUp 0.8s ease-out;
}

.contact-hero-subtitle {
    font-size: 1.2rem;
    color: #ccc;
    max-width: 600px;
    margin: 0 auto;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

.contact-hero-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.contact-hero-item {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 215, 0, 0.2);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: fadeInUp 0.8s ease-out 0.4s both;
}

.contact-hero-item:hover {
    transform: translateY(-5px);
    background: rgba(255, 215, 0, 0.1);
    border-color: rgba(255, 215, 0, 0.4);
    box-shadow: 0 20px 40px rgba(255, 215, 0, 0.1);
}

.contact-hero-icon {
    font-size: 2.5rem;
    color: #FFD700;
    margin-bottom: 1rem;
    display: block;
}

.contact-hero-item h4 {
    color: #FFD700;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.contact-hero-item p {
    color: #ccc;
    font-size: 0.95rem;
    margin: 0.25rem 0;
}

/* Contact Main Section */
.contact-section {
    padding: 80px 2rem;
    background: #fafafa;
    position: relative;
}

.contact-container {
    max-width: 1400px;
    margin: 0 auto;
}

.contact-main-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: start;
}

/* Contact Form Section */
.contact-form-section {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}

.contact-form-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #FFD700, #FFA500);
}

.form-section-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
    position: relative;
}

.form-section-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 50px;
    height: 3px;
    background: #FFD700;
    border-radius: 2px;
}

.form-section-subtitle {
    color: #666;
    font-size: 1rem;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Form Styles */
.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group.full-width {
    grid-column: 1 / -1;
}

.form-label {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
}

.form-input {
    padding: 0.75rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    background: white;
    font-family: inherit;
}

.form-input:focus {
    outline: none;
    border-color: #FFD700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

.form-input::placeholder {
    color: #999;
}

/* Dropdown Styles */
.form-dropdown .Select-control {
    border: 2px solid #e0e0e0 !important;
    border-radius: 8px !important;
    padding: 0.25rem 0.5rem !important;
    min-height: 44px !important;
    transition: all 0.3s ease !important;
    box-shadow: none !important;
}

.form-dropdown .Select-control:hover {
    border-color: #FFD700 !important;
}

.form-dropdown .is-focused .Select-control {
    border-color: #FFD700 !important;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1) !important;
}

.form-dropdown .Select-placeholder {
    color: #999 !important;
    font-size: 0.95rem !important;
}

.form-dropdown .Select-menu-outer {
    border-radius: 8px !important;
    border: 1px solid #e0e0e0 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    z-index: 1000 !important;
}

.form-dropdown .Select-option:hover {
    background-color: rgba(255, 215, 0, 0.1) !important;
    color: #1a1a1a !important;
}

.form-dropdown .Select-option.is-selected {
    background-color: #FFD700 !important;
    color: #1a1a1a !important;
}

/* Textarea Styles */
.form-textarea {
    padding: 0.75rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    background: white;
    font-family: inherit;
    resize: vertical;
    min-height: 120px;
}

.form-textarea:focus {
    outline: none;
    border-color: #FFD700;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

/* Radio Button Styles */
.form-radio-group {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
}

.form-radio-group label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    color: #1a1a1a;
}

.form-radio-group input[type="radio"] {
    width: 18px;
    height: 18px;
    accent-color: #FFD700;
}

/* Checkbox Styles */
.form-checkbox {
    margin: 1rem 0;
}

.form-checkbox label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: #666;
    cursor: pointer;
}

.form-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #FFD700;
}

.form-terms {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-required-note {
    color: #999;
    font-size: 0.85rem;
    font-style: italic;
}

/* Submit Button Styles */
.form-submit-group {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.form-submit-btn, .form-reset-btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: inherit;
}

.form-submit-btn {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: #1a1a1a;
    flex: 1;
    justify-content: center;
}

.form-submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
}

.form-reset-btn {
    background: transparent;
    color: #666;
    border: 2px solid #e0e0e0;
    padding: 0.75rem 1.5rem;
}

.form-reset-btn:hover {
    background: #f5f5f5;
    border-color: #ccc;
    color: #1a1a1a;
}

/* Contact Info Section */
.contact-info-section {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.office-section {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.office-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #FFD700;
}

.office-info {
    margin-bottom: 2rem;
}

.office-info-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding: 0.5rem 0;
}

.office-info-item i {
    color: #FFD700;
    font-size: 1.1rem;
    width: 20px;
    text-align: center;
}

.office-info-item span {
    color: #1a1a1a;
    font-size: 0.95rem;
}

/* Map Container */
.map-container {
    margin: 2rem 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 2px solid #f0f0f0;
}

/* Contact Cards Grid */
.contact-cards-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-top: 2rem;
}

.contact-card {
    background: linear-gradient(135deg, #f9f9f9, #ffffff);
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.contact-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    transform: scaleX(0);
    transition: transform 0.3s ease;
    transform-origin: left;
}

.contact-card:hover::before {
    transform: scaleX(1);
}

.contact-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.15);
    border-color: rgba(255, 215, 0, 0.3);
}

.contact-card i {
    font-size: 2rem;
    color: #FFD700;
    margin-bottom: 1rem;
    display: block;
}

.contact-card h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

.contact-card p {
    color: #666;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* Footer */
.main-footer {
    background: #1a1a1a;
    color: white;
    padding: 4rem 2rem 2rem;
}

.footer-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.footer-section h4 {
    color: #FFD700;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    font-weight: 600;
}

.footer-section p, .footer-section ul {
    color: #ccc;
    line-height: 1.6;
}

.footer-section ul {
    list-style: none;
}

.footer-section ul li {
    margin-bottom: 0.5rem;
}

.footer-section a {
    color: #ccc;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-section a:hover {
    color: #FFD700;
}

.footer-bottom {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #333;
    color: #999;
}

/* Page Specific Styles */
.page-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    text-align: center;
    margin: 6rem auto 1rem;
    color: #1a1a1a;
    padding: 0 2rem;
}

.page-subtitle {
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 3rem;
    color: #666;
    padding: 0 2rem;
}

/* Mobile Responsive */
@media (max-width: 968px) {
    .contact-main-grid {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .contact-hero-info {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .contact-form-section,
    .office-section {
        padding: 2rem;
    }
    
    .form-row {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .form-submit-group {
        flex-direction: column;
    }
    
    .form-radio-group {
        flex-direction: column;
        gap: 1rem;
    }
}

@media (max-width: 768px) {
    .mobile-menu-toggle {
        display: block;
    }

    .nav-menu {
        position: fixed;
        top: 0;
        right: -100%;
        width: 300px;
        height: 100vh;
        background: white;
        flex-direction: column;
        justify-content: flex-start;
        padding: 2rem;
        box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
        transition: right 0.3s ease;
        z-index: 1001;
    }

    .nav-menu.active {
        right: 0;
    }

    .mobile-menu-close {
        display: block;
        position: absolute;
        top: 1rem;
        right: 1rem;
    }

    .nav-links {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
        width: 100%;
        margin-top: 3rem;
    }

    .nav-link {
        width: 100%;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .header-container {
        padding: 0 1rem;
    }
    
    .contact-hero-section {
        padding: 100px 1rem 60px;
    }
    
    .contact-section {
        padding: 60px 1rem;
    }
    
    .contact-hero-item {
        padding: 1.5rem;
    }
    
    .contact-form-section,
    .office-section {
        padding: 1.5rem;
    }
    
    .form-section-title {
        font-size: 1.5rem;
    }
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Loading states and animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Focus styles for accessibility */
*:focus {
    outline: 2px solid #FFD700;
    outline-offset: 2px;
}

/* Print styles */
@media print {
    .contact-hero-section,
    .main-header,
    .main-footer {
        display: none;
    }
    
    .contact-section {
        padding: 1rem;
    }
    
    .contact-main-grid {
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
        <script>
            // Mobile menu functionality
            document.addEventListener('DOMContentLoaded', function() {
                const menuToggle = document.getElementById('mobile-menu-toggle');
                const menuClose = document.getElementById('mobile-menu-close');
                const navMenu = document.getElementById('nav-menu');

                if (menuToggle) {
                    menuToggle.addEventListener('click', function() {
                        navMenu.classList.add('active');
                    });
                }

                if (menuClose) {
                    menuClose.addEventListener('click', function() {
                        navMenu.classList.remove('active');
                    });
                }

                // Close menu when clicking outside
                document.addEventListener('click', function(e) {
                    if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                        navMenu.classList.remove('active');
                    }
                });

        </script>
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

# Function to save contact form submission
def save_contact_submission(form_data):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO contact_submissions 
            (name, email, phone, subject_category, issue_type, message, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                form_data['name'],
                form_data['email'], 
                form_data['phone'],
                form_data['subject_category'],
                form_data['issue_type'],
                form_data['message'],
                datetime.now(),
                'pending'
            ))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error saving contact submission: {e}")
            if connection:
                connection.close()
            return False
    return False

# Create responsive header component
def create_header():
    return html.Header([
        html.Div([
            html.Div([
                html.Img(src="./assets/images/logo.jpg", alt="CaelumSpace Logo", className="logo")
            ], className="logo-container"),
            
            # Mobile menu toggle button
            html.Button([
                html.I(className="fas fa-bars")
            ], className="mobile-menu-toggle", id="mobile-menu-toggle"),
            
            # Navigation menu
            html.Nav([
                html.Div([
                    html.A("Home", href="/home/", className="nav-link"),
                    html.A("Warehouse & Units", href="/units/", className="nav-link"),
                    html.A("About Us", href="/about_us/", className="nav-link"),
                    html.A("Newsroom", href="/newsroom/", className="nav-link"),
                    html.A("Contact Us", href="/contact/", className="nav-link active"),
                    html.A([
                        html.I(className="fas fa-user-plus"),
                        html.Span("Signup")
                    ], href="/signup/", className="nav-link auth-link"),
                    html.A([
                        html.I(className="fas fa-sign-in-alt"),
                        html.Span("Login")
                    ], href="/login/", className="nav-link auth-link"),
                    html.A([
                        html.I(className="fas fa-sign-out-alt"),
                        html.Span("Logout")
                    ], href="/logout/", className="nav-link auth-link", id="logout-link", style={"display": "none"})
                ], className="nav-links"),
                
                # Mobile close button
                html.Button([
                    html.I(className="fas fa-times")
                ], className="mobile-menu-close", id="mobile-menu-close")
            ], className="nav-menu", id="nav-menu")
        ], className="header-container")
    ], className="main-header")

# Create contact hero section
def create_contact_hero():
    return html.Section([
        html.Div([
            html.Div([
                html.H1("Contact Us", className="contact-hero-title"),
                html.P("Get in touch with our team. We're here to help with all your storage needs.", className="contact-hero-subtitle"),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-clock contact-hero-icon"),
                        html.Div([
                            html.H4("Business Hours"),
                            html.P("Mon - Fri: 8:00 AM - 6:00 PM"),
                            html.P("Sat - Sun: 9:00 AM - 4:00 PM")
                        ])
                    ], className="contact-hero-item"),
                    html.Div([
                        html.I(className="fas fa-phone contact-hero-icon"),
                        html.Div([
                            html.H4("Call Us"),
                            html.P("+234 (0) 123-456-7890"),
                            html.P("Emergency: +234 (0) 987-654-3210")
                        ])
                    ], className="contact-hero-item"),
                    html.Div([
                        html.I(className="fas fa-envelope contact-hero-icon"),
                        html.Div([
                            html.H4("Email Us"),
                            html.P("info@caelumspace.com"),
                            html.P("support@caelumspace.com")
                        ])
                    ], className="contact-hero-item")
                ], className="contact-hero-info")
            ], className="contact-hero-content")
        ], className="contact-hero-container")
    ], className="contact-hero-section")

# Create contact form
def create_contact_form():
    return html.Section([
        html.Div([
            html.Div([
                # Contact Form
                html.Div([
                    html.H2("Send Us a Message", className="form-section-title"),
                    html.P("Fill out the form below and we'll get back to you as soon as possible.", className="form-section-subtitle"),
                    
                    html.Form([
                        # Personal Information Row
                        html.Div([
                            html.Div([
                                html.Label("Full Name *", className="form-label"),
                                dcc.Input(
                                    type="text",
                                    id="contact-name",
                                    className="form-input",
                                    placeholder="Enter your full name",
                                    required=True
                                )
                            ], className="form-group"),
                            html.Div([
                                html.Label("Email Address *", className="form-label"),
                                dcc.Input(
                                    type="email",
                                    id="contact-email",
                                    className="form-input",
                                    placeholder="Enter your email address",
                                    required=True
                                )
                            ], className="form-group")
                        ], className="form-row"),
                        
                        # Contact Information Row
                        html.Div([
                            html.Div([
                                html.Label("Phone Number", className="form-label"),
                                dcc.Input(
                                    type="tel",
                                    id="contact-phone",
                                    className="form-input",
                                    placeholder="+234 (0) 123-456-7890"
                                )
                            ], className="form-group"),
                            html.Div([
                                html.Label("Subject Category *", className="form-label"),
                                dcc.Dropdown(
                                    id="contact-subject-category",
                                    options=[
                                        {"label": "General Inquiry", "value": "general"},
                                        {"label": "Unit Rental", "value": "rental"},
                                        {"label": "Billing & Payments", "value": "billing"},
                                        {"label": "Technical Support", "value": "technical"},
                                        {"label": "Facility Access", "value": "access"},
                                        {"label": "Security Concerns", "value": "security"},
                                        {"label": "Feedback & Suggestions", "value": "feedback"},
                                        {"label": "Partnership Opportunities", "value": "partnership"}
                                    ],
                                    placeholder="Select a category",
                                    className="form-dropdown",
                                    clearable=False
                                )
                            ], className="form-group")
                        ], className="form-row"),
                        
                        # Issue Type Row
                        html.Div([
                            html.Div([
                                html.Label("Issue Type *", className="form-label"),
                                dcc.Dropdown(
                                    id="contact-issue-type",
                                    options=[
                                        {"label": "Question", "value": "question"},
                                        {"label": "Problem/Issue", "value": "problem"},
                                        {"label": "Complaint", "value": "complaint"},
                                        {"label": "Compliment", "value": "compliment"},
                                        {"label": "Request for Information", "value": "info_request"},
                                        {"label": "Request for Service", "value": "service_request"},
                                        {"label": "Emergency", "value": "emergency"}
                                    ],
                                    placeholder="Select issue type",
                                    className="form-dropdown",
                                    clearable=False
                                )
                            ], className="form-group"),
                            html.Div([
                                html.Label("Priority Level", className="form-label"),
                                dcc.Dropdown(
                                    id="contact-priority",
                                    options=[
                                        {"label": "Low - General inquiry", "value": "low"},
                                        {"label": "Medium - Standard request", "value": "medium"},
                                        {"label": "High - Urgent matter", "value": "high"},
                                        {"label": "Critical - Emergency", "value": "critical"}
                                    ],
                                    placeholder="Select priority level",
                                    className="form-dropdown",
                                    value="medium",
                                    clearable=False
                                )
                            ], className="form-group")
                        ], className="form-row"),
                        
                        # Message
                        html.Div([
                            html.Label("Message *", className="form-label"),
                            html.Textarea(
                                id="contact-message",
                                className="form-textarea",
                                placeholder="Please provide detailed information about your inquiry, including any relevant unit numbers, dates, or specific concerns...",
                                rows=6,
                                required=True
                            )
                        ], className="form-group full-width"),
                        
                        # Additional Options
                        html.Div([
                            html.Div([
                                html.Label("Preferred Contact Method", className="form-label"),
                                dcc.RadioItems(
                                    id="contact-method",
                                    options=[
                                        {"label": "Email", "value": "email"},
                                        {"label": "Call", "value": "phone"},
                                        {"label": "SMS/Text", "value": "sms"}
                                    ],
                                    value="email",
                                    className="form-radio-group",
                                    inline=True
                                )
                            ], className="form-group"),
                            html.Div([
                                html.Label("Best Time to Contact", className="form-label"),
                                dcc.Dropdown(
                                    id="contact-time",
                                    options=[
                                        {"label": "Morning (8 AM - 12 PM)", "value": "morning"},
                                        {"label": "Afternoon (12 PM - 5 PM)", "value": "afternoon"},
                                        {"label": "Evening (5 PM - 8 PM)", "value": "evening"},
                                        {"label": "Anytime", "value": "anytime"}
                                    ],
                                    placeholder="Select preferred time",
                                    value="anytime",
                                    className="form-dropdown"
                                )
                            ], className="form-group")
                        ], className="form-row"),
                        
                        # Terms and Submit
                        html.Div([
                            html.Div([
                                dcc.Checklist(
                                    id="contact-terms",
                                    options=[
                                        {"label": " I agree to the Privacy Policy and Terms of Service", "value": "agreed"}
                                    ],
                                    className="form-checkbox"
                                ),
                                html.Small("* Required fields", className="form-required-note")
                            ], className="form-terms")
                        ], className="form-group full-width"),
                        
                        # Submit Button
                        html.Div([
                            html.Button(
                                [
                                    html.I(className="fas fa-paper-plane"),
                                    html.Span("Send Message")
                                ],
                                type="submit",
                                id="contact-submit-btn",
                                className="form-submit-btn",
                                n_clicks=0
                            ),
                            html.Button(
                                [
                                    html.I(className="fas fa-redo"),
                                    html.Span("Reset Form")
                                ],
                                type="button",
                                id="contact-reset-btn",
                                className="form-reset-btn",
                                n_clicks=0
                            )
                        ], className="form-submit-group")
                    ], id="contact-form", className="contact-form")
                ], className="contact-form-section"),
                
                # Contact Information & Map
                html.Div([
                    html.H2("Visit Our Office", className="form-section-title"),
                    html.P("Find us at our convenient location in the heart of Onitsha.", className="form-section-subtitle"),
                    
                    # Office Information
                    html.Div([
                        html.Div([
                            html.H4("Main Office", className="office-title"),
                            html.Div([
                                html.I(className="fas fa-map-marker-alt"),
                                html.Span("123 Commercial Avenue, GRA Onitsha, Anambra State, Nigeria")
                            ], className="office-info-item"),
                            html.Div([
                                html.I(className="fas fa-phone"),
                                html.Span("+234 (0) 123-456-7890")
                            ], className="office-info-item"),
                            html.Div([
                                html.I(className="fas fa-envelope"),
                                html.Span("info@caelumspace.com")
                            ], className="office-info-item"),
                            html.Div([
                                html.I(className="fas fa-globe"),
                                html.Span("www.caelumspace.com")
                            ], className="office-info-item")
                        ], className="office-info"),
                        
                        # Map Container
                        html.Div([
                            html.Iframe(
                                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3966.521260322283!2d6.78216931411207!3d6.149516895493286!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNsKwMDgnNTguMyJOIDYCsDQ2JzU1LjgiRQ!5e0!3m2!1sen!2sng!4v1234567890",
                                width="100%",
                                height="350",
                                style={"border": "0", "borderRadius": "8px"},
                                # loading="lazy",
                                referrerPolicy="no-referrer-when-downgrade"
                            )
                        ], className="map-container"),
                        
                        # Additional Contact Cards
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-headset"),
                                html.H4("24/7 Support"),
                                html.P("Round-the-clock assistance for all emergencies and urgent matters.")
                            ], className="contact-card"),
                            html.Div([
                                html.I(className="fas fa-tools"),
                                html.H4("Technical Support"),
                                html.P("Expert help with access codes, security systems, and facility features.")
                            ], className="contact-card"),
                            html.Div([
                                html.I(className="fas fa-handshake"),
                                html.H4("Customer Relations"),
                                html.P("Dedicated team for feedback, suggestions, and partnership opportunities.")
                            ], className="contact-card")
                        ], className="contact-cards-grid")
                    ], className="office-section")
                ], className="contact-info-section")
            ], className="contact-main-grid")
        ], className="contact-container")
    ], className="contact-section")

# Create footer
def create_footer():
    return html.Footer([
        html.Div([
            html.Div([
                html.Div([
                    html.H4("CaelumSpace"),
                    html.P("Premium storage solutions for modern living. Secure, accessible, and reliable.")
                ], className="footer-section"),
                html.Div([
                    html.H4("Quick Links"),
                    html.Ul([
                        html.Li(html.A("Find Units", href="/units/")),
                        html.Li(html.A("Pricing", href="/pricing/")),
                        html.Li(html.A("About Us", href="/about/")),
                        html.Li(html.A("Contact", href="/contact/"))
                    ])
                ], className="footer-section"),
                html.Div([
                    html.H4("Support"),
                    html.Ul([
                        html.Li(html.A("Help Center", href="/help/")),
                        html.Li(html.A("Privacy Policy", href="/privacy/")),
                        html.Li(html.A("Terms of Service", href="/terms/")),
                        html.Li(html.A("FAQ", href="/faq/"))
                    ])
                ], className="footer-section"),
                html.Div([
                    html.H4("Contact Info"),
                    html.P("📧 info@caelumspace.com"),
                    html.P("📞 +234 (0) 123-456-7890"),
                    html.P("📍 123 Commercial Ave, Onitsha, Anambra")
                ], className="footer-section")
            ], className="footer-container"),
            html.Div([
                html.P("© 2025 CaelumSpace. All rights reserved.")
            ], className="footer-bottom")
        ])
    ], className="main-footer")

# Main contact page layout
def create_contact_layout():
    return html.Div([
        create_header(),
        create_contact_hero(),
        create_contact_form(),
        create_footer(),
        
        # Success/Error Toast Messages
        html.Div([
            html.Div(
                id="contact-success-toast",
                className="toast toast-success",
                style={"display": "none"}
            ),
            html.Div(
                id="contact-error-toast", 
                className="toast toast-error",
                style={"display": "none"}
            )
        ], className="toast-container")
    ])

# Set the initial layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=create_contact_layout())
])

# Mobile menu toggle callback
@app.callback(
    Output('nav-menu', 'className'),
    [Input('mobile-menu-toggle', 'n_clicks'),
     Input('mobile-menu-close', 'n_clicks')],
    [State('nav-menu', 'className')],
    prevent_initial_call=True
)
def toggle_mobile_menu(toggle_clicks, close_clicks, current_class):
    """Toggle mobile menu"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# Form submission callback
@app.callback(
    [Output('contact-success-toast', 'children'),
     Output('contact-success-toast', 'style'),
     Output('contact-error-toast', 'children'),
     Output('contact-error-toast', 'style'),
     Output('contact-name', 'value'),
     Output('contact-email', 'value'),
     Output('contact-phone', 'value'),
     Output('contact-subject-category', 'value'),
     Output('contact-issue-type', 'value'),
     Output('contact-message', 'value'),
     Output('contact-terms', 'value')],
    [Input('contact-submit-btn', 'n_clicks'),
     Input('contact-reset-btn', 'n_clicks')],
    [State('contact-name', 'value'),
     State('contact-email', 'value'),
     State('contact-phone', 'value'),
     State('contact-subject-category', 'value'),
     State('contact-issue-type', 'value'),
     State('contact-priority', 'value'),
     State('contact-message', 'value'),
     State('contact-method', 'value'),
     State('contact-time', 'value'),
     State('contact-terms', 'value')],
    prevent_initial_call=True
)
def handle_form_submission(submit_clicks, reset_clicks, name, email, phone, 
                          subject_category, issue_type, priority, message, 
                          contact_method, contact_time, terms):
    """Handle contact form submission and reset"""
    ctx = dash.callback_context
    
    # Default return values
    success_toast = ""
    success_style = {"display": "none"}
    error_toast = ""
    error_style = {"display": "none"}
    
    # Default form values for reset
    form_values = ["", "", "", None, None, "", []]
    
    if not ctx.triggered:
        return [success_toast, success_style, error_toast, error_style] + form_values
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'contact-reset-btn':
        # Reset form
        return [success_toast, success_style, error_toast, error_style] + form_values
    
    elif button_id == 'contact-submit-btn':
        # Validate required fields
        if not all([name, email, subject_category, issue_type, message]):
            error_toast = [
                html.I(className="fas fa-exclamation-triangle"),
                html.Span("Please fill in all required fields.")
            ]
            error_style = {"display": "flex"}
            return [success_toast, success_style, error_toast, error_style] + [
                name or "", email or "", phone or "", subject_category, 
                issue_type, message or "", terms or []
            ]
        
        if not terms or 'agreed' not in terms:
            error_toast = [
                html.I(className="fas fa-exclamation-triangle"),
                html.Span("Please agree to the Terms of Service and Privacy Policy.")
            ]
            error_style = {"display": "flex"}
            return [success_toast, success_style, error_toast, error_style] + [
                name, email, phone or "", subject_category, 
                issue_type, message, terms or []
            ]
        
        # Prepare form data
        form_data = {
            'name': name,
            'email': email,
            'phone': phone or "",
            'subject_category': subject_category,
            'issue_type': issue_type,
            'message': message
        }
        
        # Save to database
        if save_contact_submission(form_data):
            success_toast = [
                html.I(className="fas fa-check-circle"),
                html.Span("Thank you! Your message has been sent successfully. We'll get back to you soon.")
            ]
            success_style = {"display": "flex"}
            # Clear form after successful submission
            form_values = ["", "", "", None, None, "", []]
        else:
            error_toast = [
                html.I(className="fas fa-exclamation-triangle"),
                html.Span("Sorry, there was an error sending your message. Please try again.")
            ]
            error_style = {"display": "flex"}
            # Keep form data on error
            form_values = [name, email, phone or "", subject_category, 
                          issue_type, message, terms]
    
    return [success_toast, success_style, error_toast, error_style] + form_values
