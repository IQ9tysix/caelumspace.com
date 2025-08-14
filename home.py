import dash
from dash import Dash, dcc, html, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta
import hashlib
import secrets
import pyodbc
import re
from flask import session, request, redirect, url_for
import logging
import mysql.connector
from mysql.connector import Error
import urllib.parse

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/home/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)

# Custom CSS integrated into app.index_string
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

            /* Hero Section */
            .hero-section {
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }

            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.4);
                z-index: 1;
            }

            .hero-container {
                position: relative;
                z-index: 2;
                text-align: center;
                color: white;
                max-width: 800px;
                padding: 0 2rem;
            }

            .hero-title {
                font-size: clamp(2.5rem, 5vw, 4rem);
                font-weight: 700;
                margin-bottom: 1.5rem;
                letter-spacing: -0.02em;
            }

            .hero-subtitle {
                font-size: 1.2rem;
                margin-bottom: 2.5rem;
                opacity: 0.9;
                font-weight: 400;
            }

            .cta-button {
                display: inline-block;
                background: #FFD700;
                color: #1a1a1a;
                padding: 1rem 2rem;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                border: 2px solid #FFD700;
            }

            .cta-button:hover {
                background: transparent;
                color: #FFD700;
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
            }

            .secondary-button {
                display: inline-block;
                background: transparent;
                color: #1a1a1a;
                padding: 1rem 2rem;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                border: 2px solid #1a1a1a;
                transition: all 0.3s ease;
                margin-left: 1rem;
            }

            .secondary-button:hover {
                background: #1a1a1a;
                color: white;
                transform: translateY(-2px);
            }

            /* Section Styles */
            .section-title {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 700;
                text-align: center;
                margin-bottom: 1rem;
                color: #1a1a1a;
                letter-spacing: -0.02em;
            }

            .section-subtitle {
                font-size: 1.1rem;
                text-align: center;
                margin-bottom: 4rem;
                color: #666;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }

            .services-section, .units-section, .how-it-works, .blog-section, .faq-section {
                padding: 6rem 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }

            /* Services Grid */
            .services-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-top: 4rem;
            }

            .service-card {
                background: white;
                padding: 3rem 2rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }

            .service-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
            }

            .service-icon {
                font-size: 3rem;
                color: #FFD700;
                margin-bottom: 1.5rem;
            }

            .service-card h3 {
                font-size: 1.4rem;
                margin-bottom: 1rem;
                color: #1a1a1a;
                font-weight: 600;
            }

            .service-card p {
                color: #666;
                line-height: 1.6;
            }

            /* Steps Container */
            .steps-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin-top: 4rem;
            }

            .step-card {
                text-align: center;
                padding: 2rem 1rem;
            }

            .step-number {
                width: 60px;
                height: 60px;
                background: #FFD700;
                color: #1a1a1a;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0 auto 1.5rem;
            }

            .step-card h3 {
                font-size: 1.3rem;
                margin-bottom: 1rem;
                color: #1a1a1a;
                font-weight: 600;
            }

            .step-card p {
                color: #666;
                line-height: 1.6;
            }

            /* Units Grid */
            .units-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
                gap: 2rem;
                margin-top: 3rem;
            }

            .unit-card {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }

            .unit-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
            }

            .unit-image-container {
                position: relative;
                overflow: hidden;
                height: 220px;
            }

            .unit-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }

            .unit-card:hover .unit-image {
                transform: scale(1.05);
            }

            .unit-info {
                padding: 1.5rem;
            }

            .unit-price {
                font-size: 1.4rem;
                font-weight: 700;
                color: #FFD700;
                margin-bottom: 0.5rem;
            }

            .unit-name {
                font-size: 1.2rem;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
            }

            .unit-location {
                color: #666;
                margin-bottom: 1rem;
                font-size: 0.95rem;
            }

            .unit-status {
                display: inline-block;
                background: #e8f5e8;
                color: #2d5a2d;
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
                margin-bottom: 1rem;
            }

            .unit-details-btn {
                display: inline-block;
                background: #1a1a1a;
                color: white;
                padding: 0.7rem 1.5rem;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .unit-details-btn:hover {
                background: #FFD700;
                color: #1a1a1a;
                transform: translateY(-1px);
            }

            /* Blog Section */
            .blog-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
                margin-top: 3rem;
            }

            .blog-card {
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }

            .blog-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
            }

            .blog-image-container {
                height: 200px;
                overflow: hidden;
            }

            .blog-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }

            .blog-card:hover .blog-image {
                transform: scale(1.05);
            }

            .blog-content {
                padding: 1.5rem;
            }

            .blog-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.8rem;
                line-height: 1.4;
            }

            .blog-excerpt {
                color: #666;
                margin-bottom: 1rem;
                line-height: 1.5;
            }

            .blog-read-more {
                color: #FFD700;
                text-decoration: none;
                font-weight: 500;
                font-size: 0.95rem;
                transition: color 0.3s ease;
            }

            .blog-read-more:hover {
                color: #1a1a1a;
            }

            /* FAQ Section */
            .faq-container {
                max-width: 800px;
                margin: 0 auto;
            }

            .faq-item {
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }

            .faq-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1.5rem 0;
                cursor: pointer;
            }

            .faq-question {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1a1a1a;
            }

            .faq-toggle {
                background: none;
                border: none;
                font-size: 1.2rem;
                color: #FFD700;
                cursor: pointer;
                transition: transform 0.3s ease;
            }

            .faq-answer {
                padding-bottom: 1.5rem;
                color: #666;
                line-height: 1.6;
                display: none;
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

            /* Mobile Responsive */
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

                .hero-container {
                    padding: 0 1rem;
                }

                .services-section, .units-section, .how-it-works, .blog-section, .faq-section {
                    padding: 4rem 1rem;
                }

                .units-container {
                    grid-template-columns: 1fr;
                }

                .services-container {
                    grid-template-columns: 1fr;
                }

                .steps-container {
                    grid-template-columns: 1fr;
                }

                .blog-container {
                    grid-template-columns: 1fr;
                }

                .secondary-button {
                    margin-left: 0;
                    margin-top: 1rem;
                }
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

            .units-page {
                min-height: calc(100vh - 80px);
                padding: 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }

            .no-units-message {
                text-align: center;
                color: #666;
                font-size: 1.1rem;
                padding: 3rem;
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

            .service-card, .unit-card, .blog-card, .step-card {
                animation: fadeInUp 0.6s ease-out;
            }

            .auth-section {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.profile-container {
    position: relative;
}

.profile-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    transition: background-color 0.2s ease;
}

.profile-display:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.profile-initials {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
}

.profile-name {
    font-weight: 500;
    color: #333;
}

.profile-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-width: 180px;
    z-index: 1000;
    margin-top: 0.5rem;
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    text-decoration: none;
    color: #333;
    transition: background-color 0.2s ease;
}

.dropdown-item:hover {
    background-color: #f8f9fa;
    text-decoration: none;
    color: #333;
}

.dropdown-divider {
    margin: 0.5rem 0;
    border: none;
    border-top: 1px solid #e1e5e9;
}

.icon-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 6px;
    transition: background-color 0.2s ease;
}

.icon-link:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.nav-text {
    font-size: 14px;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .auth-section {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .profile-dropdown {
        right: 0;
        left: auto;
    }
    
    .nav-text {
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

                // FAQ toggle functionality
                const faqToggles = document.querySelectorAll('.faq-toggle');
                faqToggles.forEach(toggle => {
                    toggle.addEventListener('click', function() {
                        const target = this.getAttribute('data-target');
                        const answer = document.getElementById(target);
                        const icon = this.querySelector('i');
                        
                        if (answer.style.display === 'block') {
                            answer.style.display = 'none';
                            icon.className = 'fas fa-plus';
                        } else {
                            answer.style.display = 'block';
                            icon.className = 'fas fa-minus';
                        }
                    });
                });
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

# Session management functions
def get_current_user():
    """Get current user from session"""
    if not session.get('authenticated', False):
        return None
    
    user_type = session.get('user_type')
    
    if user_type == 'admin':
        return {
            'type': 'admin',
            'id': session.get('user_id'),  # This will be 'admin'
            'email': session.get('email'),
            'is_admin': session.get('is_admin', False),
            'name': 'Admin'
        }
    
    elif user_type == 'cso':
        return {
            'type': 'cso',
            'id': session.get('cso_id'),
            'cso_name': session.get('cso_name'),
            'email': session.get('email'),
            'function_role': session.get('function_role'),
            'function_name': session.get('function_name'),
            'name': session.get('cso_name')
        }
    
    elif user_type == 'user':
        return {
            'type': 'user',
            'id': session.get('user_id'),
            'email': session.get('email'),
            'status': session.get('status'),
            'first_name': session.get('first_name'),
            'last_name': session.get('last_name'),
            'name': f"{session.get('first_name', '')} {session.get('last_name', '')}".strip() or session.get('email', '').split('@')[0]
        }
    
    return None
    
# Fetch units from database with warehouse images
def fetch_available_units(limit=None):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT u.id, u.name as unit_name, w.name as warehouse_name, 
                   w.location as warehouse_location, u.price, u.availability, w.image_path
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            WHERE u.status = 'active' AND u.availability = 'not taken'
            ORDER BY u.created_at DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            units = cursor.fetchall()
            cursor.close()
            connection.close()
            return units
        except Error as e:
            print(f"Error fetching units: {e}")
            if connection:
                connection.close()
            return []
    return []

# Fetch all units for units page
def fetch_all_units():
    return fetch_available_units()

# Fetch unit details by ID
def fetch_unit_details(unit_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT u.id, u.name as unit_name, w.name as warehouse_name, 
                   w.location as warehouse_location, u.price, u.availability, 
                   w.image_path, u.status, u.created_at, u.updated_at
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            WHERE u.id = %s
            """
            cursor.execute(query, (unit_id,))
            unit = cursor.fetchone()
            cursor.close()
            connection.close()
            return unit
        except Error as e:
            print(f"Error fetching unit details: {e}")
            if connection:
                connection.close()
            return None
    return None

def create_header():
    # Get current user session data
    current_user = get_current_user()
    
    # Determine what navigation elements to show
    if current_user:
        user_type = current_user['type']
        
        # For admin and cso, only show logout
        if user_type in ['admin', 'cso']:
            # Get user name for profile display
            if user_type == 'admin':
                display_name = "Admin"
                initials = "A"
            else:  # cso
                cso_name = current_user.get('cso_name', '')
                name_parts = cso_name.split() if cso_name else ['CSO']
                display_name = cso_name or "CSO"
                # Get first letter of first and last name
                if len(name_parts) >= 2:
                    initials = f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
                else:
                    initials = name_parts[0][0].upper() if name_parts else "C"
            
            auth_links = [
                html.Div([
                    html.Div([
                        html.Span(initials, className="profile-initials"),
                        html.Span(display_name, className="profile-name")
                    ], className="profile-display"),
                    html.A([
                        html.I(className="fas fa-sign-out-alt"),
                        html.Span("Logout")
                    ], href="/logout/", className="nav-link auth-link")
                ], className="auth-section")
            ]
            
        else:  # user type
            # Get user name for profile display
            first_name = current_user.get('first_name', '')
            last_name = current_user.get('last_name', '')
            email = current_user.get('email', '')
            
            # Try to get name from session or email
            if first_name and last_name:
                display_name = f"{first_name} {last_name}"
                initials = f"{first_name[0]}{last_name[0]}".upper()
            elif first_name:
                display_name = first_name
                initials = first_name[0].upper()
            else:
                # Fallback to email
                display_name = email.split('@')[0] if email else "User"
                initials = display_name[0].upper() if display_name else "U"
            
            auth_links = [
                html.Div([
                    # Saved items icon
                    html.A([
                        html.I(className="fas fa-heart"),
                        html.Span("Saved", className="nav-text")
                    ], href="/saved/", className="nav-link icon-link", title="Saved Items"),
                    
                    # Profile section
                    html.Div([
                        html.Div([
                            html.Span(initials, className="profile-initials"),
                            html.I(className="fas fa-chevron-down profile-dropdown-icon")
                        ], className="profile-display", id="profile-dropdown-trigger"),
                        
                        # Profile dropdown menu
                        html.Div([
                            html.A([
                                html.I(className="fas fa-user"),
                                html.Span("Profile")
                            ], href="/profile/", className="dropdown-item"),
                            html.A([
                                html.I(className="fas fa-cog"),
                                html.Span("Settings")
                            ], href="/settings/", className="dropdown-item"),
                            html.Hr(className="dropdown-divider"),
                            html.A([
                                html.I(className="fas fa-sign-out-alt"),
                                html.Span("Logout")
                            ], href="/logout/", className="dropdown-item")
                        ], className="profile-dropdown", id="profile-dropdown", style={"display": "none"})
                    ], className="profile-container")
                ], className="auth-section")
            ]
    else:
        # Not logged in - show signup and login
        auth_links = [
            html.A([
                html.I(className="fas fa-user-plus"),
                html.Span("Signup")
            ], href="/signup/", className="nav-link auth-link"),
            html.A([
                html.I(className="fas fa-sign-in-alt"),
                html.Span("Login")
            ], href="/login/", className="nav-link auth-link")
        ]
    
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
                    html.A("Warehouses", href="/units/", className="nav-link"),
                    html.A("About Us", href="/about_us/", className="nav-link"),
                    html.A("Newsroom", href="/newsroom/", className="nav-link"),
                    html.A("Contact Us", href="/contact/", className="nav-link"),
                    
                    # Dynamic auth links based on session
                    html.Div(auth_links, className="auth-links-container")
                ], className="nav-links"),
                
                # Mobile close button
                html.Button([
                    html.I(className="fas fa-times")
                ], className="mobile-menu-close", id="mobile-menu-close")
            ], className="nav-menu", id="nav-menu")
        ], className="header-container")
    ], className="main-header")

# Add this callback to handle profile dropdown toggle for users
@app.callback(
    Output("profile-dropdown", "style"),
    Input("profile-dropdown-trigger", "n_clicks"),
    State("profile-dropdown", "style"),
    prevent_initial_call=True
)
def toggle_profile_dropdown(n_clicks, current_style):
    if n_clicks:
        if current_style.get("display") == "none":
            return {"display": "block"}
        else:
            return {"display": "none"}
    return {"display": "none"}

# Client-side callback to close dropdown when clicking outside
app.clientside_callback(
    """
    function(n_clicks) {
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('profile-dropdown');
            const trigger = document.getElementById('profile-dropdown-trigger');
            
            if (dropdown && trigger && !trigger.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output("profile-dropdown", "id"),
    Input("profile-dropdown-trigger", "n_clicks"),
    prevent_initial_call=True
)

# Create hero section with single background image
def create_hero_section():
    return html.Section([
        html.Div([
            html.Div([
                html.H1("Premium Storage Solutions", className="hero-title"),
                html.P("Secure, accessible, and affordable storage units for all your needs", className="hero-subtitle"),
                html.A("Get Started Today", href="/units/", className="cta-button hero-cta")
            ], className="hero-content")
        ], className="hero-container")
    ], className="hero-section", 
    style={
        "backgroundImage": "url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')",
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "backgroundRepeat": "no-repeat"
    })

# Create services section
def create_services():
    services = [
        {
            "icon": "fas fa-search",
            "title": "Find Storage Units",
            "description": "Browse through hundreds of storage units in various sizes and locations to find the perfect fit for your needs."
        },
        {
            "icon": "fas fa-key",
            "title": "Rent Units",
            "description": "Secure your storage unit with our streamlined rental process. Quick approval and instant access to your space."
        },
        {
            "icon": "fas fa-cog",
            "title": "Manage Online",
            "description": "Control your storage experience through our advanced online platform. Pay bills, access units, and monitor your storage."
        }
    ]
    
    return html.Section([
        html.Div([
            html.H2("Our Services", className="section-title"),
            html.P("Comprehensive storage solutions designed for your convenience", className="section-subtitle"),
            html.Div([
                html.Div([
                    html.I(className=f"service-icon {service['icon']}"),
                    html.H3(service['title']),
                    html.P(service['description'])
                ], className="service-card") for service in services
            ], className="services-container")
        ])
    ], className="services-section", id="services")

# Create how it works section
def create_how_it_works():
    steps = [
        {"number": "1", "title": "Find Your Unit", "description": "Browse available storage units by location and size"},
        {"number": "2", "title": "Pay Securely", "description": "Complete your rental with our secure payment system"},
        {"number": "3", "title": "Manage Online", "description": "Access your account and manage your storage remotely"},
        {"number": "4", "title": "Move In", "description": "Get your access code and start using your storage unit"}
    ]
    
    return html.Section([
        html.Div([
            html.H2("How It Works", className="section-title"),
            html.P("Get started with storage in four simple steps", className="section-subtitle"),
            html.Div([
                html.Div([
                    html.Div(step['number'], className="step-number"),
                    html.H3(step['title']),
                    html.P(step['description'])
                ], className="step-card") for step in steps
            ], className="steps-container")
        ])
    ], className="how-it-works")

# Create units display section for homepage
def create_units_display():
    units = fetch_available_units(6)  # Limit to 6 units for homepage
    
    unit_cards = []
    for unit in units:
        # Use warehouse image or fallback
        image_src = unit.get('image_path', 'https://blog.fglobalshipping.com/wp-content/uploads/2019/06/Outsourced-Warehouse-1024x683.jpg')
        if not image_src or image_src.strip() == '':
            image_src = 'https://groupagecontainer.com/wp-content/uploads/2023/06/groupage-container-shipping-to-nigeria.jpg'
            
        unit_cards.append(
            html.Div([
                html.Div([
                    html.Img(src=image_src, alt=f"{unit['unit_name']} Storage", className="unit-image")
                ], className="unit-image-container"),
                html.Div([
                    html.Div(f"₦{unit['price']}/month", className="unit-price"),
                    html.Div(unit['unit_name'], className="unit-name"),
                    html.Div(f"{unit['warehouse_name']} - {unit['warehouse_location']}", className="unit-location"),
                    html.A("View Details", href=f"/unit_details/{unit['id']}", className="unit-details-btn")
                ], className="unit-info")
            ], className="unit-card")
        )
    
    return html.Section([
        html.Div([
            html.H2("Available Units", className="section-title"),
            html.P("Discover premium storage spaces in prime locations", className="section-subtitle"),
            html.Div(unit_cards, className="units-container", id="units-container"),
            html.Div([
                html.A("View All Units", href="/units/", className="cta-button", 
                      style={"marginTop": "40px", "display": "inline-block"})
            ], style={"textAlign": "center"})
        ])
    ], className="units-section", id="units")

# Create blog/articles section with images
def create_blog_section():
    blog_posts = [
        {
            "title": "Storage Tips for Small Businesses", 
            "excerpt": "Maximize your storage efficiency with these professional tips.",
            "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        },
        {
            "title": "Seasonal Storage Solutions", 
            "excerpt": "How to store seasonal items safely and efficiently.",
            "image": "https://plus.unsplash.com/premium_photo-1661302828763-4ec9b91d9ce3?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8aW5kdXN0cmlhbCUyMHdhcmVob3VzZXxlbnwwfHwwfHx8MA%3D%3D"
        },
        {
            "title": "Moving Made Easy", 
            "excerpt": "Expert advice for a seamless moving experience.",
            "image": "https://redstagfulfillment.com/wp-content/uploads/351A0293-scaled.jpg"
        },
        {
            "title": "Security Features Guide", 
            "excerpt": "Understanding our advanced security measures for your peace of mind.",
            "image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
        }
    ]
    
    return html.Section([
        html.Div([
            html.H2("Latest Insights", className="section-title"),
            html.P("Stay informed with our latest storage tips and news", className="section-subtitle"),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=post['image'], alt=post['title'], className="blog-image")
                    ], className="blog-image-container"),
                    html.Div([
                        html.H3(post['title'], className="blog-title"),
                        html.P(post['excerpt'], className="blog-excerpt"),
                        html.A("Read More", href="#", className="blog-read-more")
                    ], className="blog-content")
                ], className="blog-card") for post in blog_posts
            ], className="blog-container"),
            html.Div([
                html.A("See More Articles", href="/blog/", className="cta-button",
                      style={"marginTop": "40px", "display": "inline-block"})
            ], style={"textAlign": "center"})
        ])
    ], className="blog-section")

# Create FAQ section with proper state management
def create_faq_section():
    faqs = [
        {
            "question": "What sizes of storage units do you offer?",
            "answer": "We offer a variety of storage unit sizes ranging from small 5x5 units perfect for closet storage to large 10x30 units suitable for multiple rooms of furniture."
        },
        {
            "question": "How secure are your storage facilities?",
            "answer": "Our facilities feature 24/7 security monitoring, individual unit alarms, secure access codes, and well-lit premises with security cameras throughout."
        },
        {
            "question": "Can I access my unit anytime?",
            "answer": "Yes, our facilities offer 24/7 access so you can retrieve or store your items whenever it's convenient for you."
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept all major credit cards, debit cards, bank transfers, and online payments through our secure platform."
        },
        {
            "question": "Do you offer climate-controlled units?",
            "answer": "Yes, we have climate-controlled units available to protect sensitive items from temperature and humidity fluctuations."
        }
    ]
    
    return html.Section([
        html.Div([
            html.H2("Frequently Asked Questions", className="section-title"),
            html.P("Find answers to common questions about our storage services", className="section-subtitle"),
            html.Div([
                html.Div([
                    html.Button([
                        html.H4(faq['question'], className="faq-question"),
                        html.I(className="fas fa-plus", id=f"faq-icon-{i}")
                    ], className="faq-header", id=f"faq-header-{i}", n_clicks=0),
                    html.Div([
                        html.P(faq['answer'])
                    ], className="faq-answer", id=f"faq-answer-{i}", style={"display": "none"})
                ], className="faq-item", id=f"faq-item-{i}") for i, faq in enumerate(faqs)
            ], className="faq-container", id="faq-container")
        ])
    ], className="faq-section")

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
                    html.P("📞 +1 (555) 123-4567"),
                    html.P("📍 123 Storage Ave, City, State")
                ], className="footer-section")
            ], className="footer-container"),
            html.Div([
                html.P("© 2025 CaelumSpace. All rights reserved.")
            ], className="footer-bottom")
        ])
    ], className="main-footer")

# Create all units page layout
def create_all_units_layout():
    units = fetch_all_units()
    
    unit_cards = []
    for unit in units:
        # Use warehouse image or fallback
        image_src = unit.get('image_path', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80')
        if not image_src or image_src.strip() == '':
            image_src = 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80'
            
        unit_cards.append(
            html.Div([
                html.Div([
                    html.Img(src=image_src, alt=f"{unit['unit_name']} Storage", className="unit-image")
                ], className="unit-image-container"),
                html.Div([
                    html.Div(f"₦{unit['price']}/month", className="unit-price"),
                    html.Div(unit['unit_name'], className="unit-name"),
                    html.Div(f"{unit['warehouse_name']} - {unit['warehouse_location']}", className="unit-location"),
                    html.Div("Available", className="unit-status"),
                    html.A("View Details", href=f"/unit_details/{unit['id']}", className="unit-details-btn")
                ], className="unit-info")
            ], className="unit-card")
        )
    
    return html.Div([
        create_header(),
        html.Section([
            html.Div([
                html.H1("All Available Units", className="page-title"),
                html.P("Browse all our available storage units", className="page-subtitle"),
                html.Div(unit_cards if unit_cards else [
                    html.Div("No units available at the moment.", className="no-units-message")
                ], className="units-container")
            ])
        ], className="units-page"),
        create_faq_section(),
        create_footer()
    ])

# Create unit details page layout
def create_unit_details_layout(unit_id):
    unit = fetch_unit_details(unit_id)
    
    if not unit:
        return html.Div([
            create_header(),
            html.Section([
                html.Div([
                    html.H1("Unit Not Found", className="page-title"),
                    html.P("The requested unit could not be found.", className="error-message"),
                    html.A("Back to Units", href="/units/", className="cta-button")
                ])
            ], className="error-page"),
            create_footer()
        ])
    
    # Use warehouse image or fallback
    image_src = unit.get('image_path', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80')
    if not image_src or image_src.strip() == '':
        image_src = 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
    
    return html.Div([
        create_header(),
        html.Section([
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=image_src, alt=f"{unit['unit_name']} Storage", className="unit-detail-image")
                    ], className="unit-image-section"),
                    html.Div([
                        html.H1(unit['unit_name'], className="unit-detail-title"),
                        html.Div([
                            html.Span("Location: ", className="detail-label"),
                            html.Span(f"{unit['warehouse_name']} - {unit['warehouse_location']}")
                        ], className="unit-detail-item"),
                        html.Div([
                            html.Span("Price: ", className="detail-label"),
                            html.Span(f"₦{unit['price']}/month", className="unit-detail-price")
                        ], className="unit-detail-item"),
                        html.Div([
                            html.Span("Status: ", className="detail-label"),
                            html.Span(unit['availability'].title(), className="unit-detail-status")
                        ], className="unit-detail-item"),
                        html.Div([
                            html.Span("Unit ID: ", className="detail-label"),
                            html.Span(f"#{unit['id']:04d}")
                        ], className="unit-detail-item"),
                        html.Div([
                            html.A("Book This Unit", href=f"/booking/{unit['id']}", className="cta-button book-unit-btn"),
                            html.A("Back to Units", href="/units/", className="secondary-button")
                        ], className="unit-actions")
                    ], className="unit-info-section")
                ], className="unit-detail-container"),
                
                # Additional unit information
                html.Div([
                    html.H3("Unit Features", className="features-title"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-shield-alt"),
                            html.Span("24/7 Security")
                        ], className="feature-item"),
                        html.Div([
                            html.I(className="fas fa-thermometer-half"),
                            html.Span("Climate Controlled")
                        ], className="feature-item"),
                        html.Div([
                            html.I(className="fas fa-key"),
                            html.Span("Individual Access Code")
                        ], className="feature-item"),
                        html.Div([
                            html.I(className="fas fa-video"),
                            html.Span("CCTV Monitoring")
                        ], className="feature-item")
                    ], className="features-grid")
                ], className="unit-features-section")
            ])
        ], className="unit-details-page"),
        create_faq_section(),
        create_footer()
    ])

# Main homepage layout
def create_layout():
    return html.Div([
        create_header(),
        create_hero_section(),
        create_services(),
        create_how_it_works(),
        create_units_display(),
        create_blog_section(),
        create_faq_section(),
        create_footer()
    ])

# Set the initial layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# FIXED: Mobile menu toggle - simplified and removed DOM manipulation
@app.callback(
    Output('nav-menu', 'className'),
    [Input('mobile-menu-toggle', 'n_clicks'),
     Input('mobile-menu-close', 'n_clicks')],
    [State('nav-menu', 'className')],
    prevent_initial_call=True
)
def toggle_mobile_menu(toggle_clicks, close_clicks, current_class):
    """Toggle mobile menu without DOM manipulation"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# FIXED: FAQ toggle - using proper Dash callbacks instead of clientside DOM manipulation
@app.callback(
    [Output(f'faq-answer-{i}', 'style') for i in range(5)] +
    [Output(f'faq-icon-{i}', 'className') for i in range(5)],
    [Input(f'faq-header-{i}', 'n_clicks') for i in range(5)],
    prevent_initial_call=True
)
def toggle_faq(*args):
    """Toggle FAQ items properly"""
    ctx = dash.callback_context
    
    # Initialize all FAQs as closed
    answer_styles = [{"display": "none"} for _ in range(5)]
    icon_classes = ["fas fa-plus" for _ in range(5)]
    
    if ctx.triggered:
        # Find which FAQ was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        faq_index = int(button_id.split('-')[-1])
        
        # Open the clicked FAQ
        answer_styles[faq_index] = {"display": "block"}
        icon_classes[faq_index] = "fas fa-minus"
    
    return answer_styles + icon_classes

# FIXED: URL routing callback - removed circular dependency
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=False
)
def display_page(pathname):
    """Handle URL routing without causing loops"""
    if pathname == '/units/' or pathname == '/units':
        return create_all_units_layout()
    elif pathname and pathname.startswith('/unit_details/'):
        try:
            unit_id = int(pathname.split('/')[-1])
            return create_unit_details_layout(unit_id)
        except (ValueError, IndexError):
            return html.Div([
                create_header(),
                html.Section([
                    html.Div([
                        html.H1("Invalid Unit ID", className="page-title"),
                        html.P("Please provide a valid unit ID.", className="error-message"),
                        html.A("Back to Units", href="/units/", className="cta-button")
                    ])
                ], className="error-page"),
                create_footer()
            ])
    else:
        # Default to homepage
        return create_layout()