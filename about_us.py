import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta
import hashlib
import secrets
import pyodbc
import re
from flask import session
import logging
import mysql.connector
from mysql.connector import Error

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/about_us/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
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

            /* ===== ABOUT US PAGE STYLES ===== */

/* Hero Section */
.about-hero-section {
    background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
    color: white;
    padding: 8rem 2rem 6rem;
    margin-top: 80px;
    position: relative;
    overflow: hidden;
}

.about-hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="%23FFD700" stroke-width="0.3" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}

.about-hero-container {
    max-width: 1400px;
    margin: 0 auto;
    text-align: center;
    position: relative;
    z-index: 2;
}

.about-hero-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: white;
    letter-spacing: -0.02em;
}

.about-hero-subtitle {
    font-size: clamp(1.1rem, 2.5vw, 1.4rem);
    color: #FFD700;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Company Story Section */
.company-story-section {
    padding: 8rem 2rem;
    background: #ffffff;
}

.story-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.story-content {
    padding-right: 2rem;
}

.section-title {
    font-size: clamp(2rem, 3vw, 2.8rem);
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 2rem;
    letter-spacing: -0.01em;
    position: relative;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 60px;
    height: 3px;
    background: #FFD700;
    border-radius: 2px;
}

.section-title.center {
    text-align: center;
}

.section-title.center::after {
    left: 50%;
    transform: translateX(-50%);
}

.story-paragraph {
    font-size: 1.1rem;
    line-height: 1.8;
    color: #555;
    margin-bottom: 1.5rem;
    font-weight: 400;
}

.story-image-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.story-image {
    width: 100%;
    height: 400px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.story-image:hover {
    transform: scale(1.05);
}

/* Mission, Vision, Values Section */
.mvv-section {
    padding: 8rem 2rem;
    background: #f8f9fa;
}

.mvv-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 3rem;
    margin-top: 4rem;
}

.mvv-card {
    background: white;
    padding: 3rem 2rem;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 215, 0, 0.1);
    position: relative;
    overflow: hidden;
}

.mvv-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #FFD700, #FFA500);
}

.mvv-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.mvv-icon-container {
    width: 80px;
    height: 80px;
    margin: 0 auto 2rem;
    background: linear-gradient(135deg, #FFD700, #FFA500);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1a1a1a;
    font-size: 2rem;
    box-shadow: 0 10px 20px rgba(255, 215, 0, 0.3);
}

.mvv-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
}

.mvv-description {
    font-size: 1rem;
    line-height: 1.7;
    color: #666;
}

.values-card {
    text-align: left;
}

.values-list {
    list-style: none;
    padding: 0;
}

.values-list li {
    padding: 0.8rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    color: #555;
    font-size: 1rem;
    position: relative;
    padding-left: 2rem;
}

.values-list li::before {
    content: '▶';
    position: absolute;
    left: 0;
    color: #FFD700;
    font-size: 0.8rem;
}

.values-list li:last-child {
    border-bottom: none;
}

/* What We Do Section */
.what-we-do-section {
    padding: 8rem 2rem;
    background: white;
}

.section-subtitle {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    max-width: 800px;
    margin: 0 auto 4rem;
    line-height: 1.6;
}

.about-services-grid {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2.5rem;
}

.about-service-card {
    background: white;
    padding: 2.5rem 2rem;
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.about-service-card::before {
    content: '';
    position: absolute;
    top: -100%;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.05), rgba(255, 215, 0, 0.1));
    transition: top 0.3s ease;
}

.about-service-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    border-color: #FFD700;
}

.about-service-card:hover::before {
    top: 0;
}

.service-icon-container {
    width: 70px;
    height: 70px;
    margin: 0 auto 1.5rem;
    background: #1a1a1a;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFD700;
    font-size: 1.8rem;
    position: relative;
    z-index: 2;
    transition: all 0.3s ease;
}

.about-service-card:hover .service-icon-container {
    background: #FFD700;
    color: #1a1a1a;
    transform: scale(1.1);
}

.service-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1rem;
    position: relative;
    z-index: 2;
}

.service-description {
    font-size: 1rem;
    line-height: 1.6;
    color: #666;
    position: relative;
    z-index: 2;
}

/* Impact Section */
.impact-section {
    padding: 8rem 2rem;
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    color: white;
}

.stats-grid {
    max-width: 1400px;
    margin: 0 auto 6rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
}

.stat-card {
    text-align: center;
    padding: 2rem 1rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 215, 0, 0.2);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 215, 0, 0.1);
    border-color: #FFD700;
}

.stat-icon {
    font-size: 2.5rem;
    color: #FFD700;
    margin-bottom: 1rem;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    color: #ccc;
    font-weight: 500;
}

.impact-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.impact-subtitle {
    font-size: 1.8rem;
    font-weight: 600;
    color: #FFD700;
    margin-bottom: 1.5rem;
}

.impact-description {
    font-size: 1.1rem;
    line-height: 1.7;
    color: #ccc;
    margin-bottom: 1.5rem;
}

.impact-image-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.impact-image {
    width: 100%;
    height: 350px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.impact-image:hover {
    transform: scale(1.05);
}

/* Team Section */
.team-section {
    padding: 8rem 2rem;
    background: #f8f9fa;
}

.team-grid {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 3rem;
}

.team-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.team-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.team-image-container {
    position: relative;
    overflow: hidden;
    height: 280px;
}

.team-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.team-card:hover .team-image {
    transform: scale(1.1);
}

.team-info {
    padding: 2rem;
    text-align: center;
}

.team-name {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

.team-position {
    font-size: 1rem;
    color: #FFD700;
    font-weight: 500;
    margin-bottom: 1rem;
}

.team-description {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #666;
}

/* CTA Section */
.about-cta-section {
    padding: 6rem 2rem;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    text-align: center;
    color: #1a1a1a;
}

.cta-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1a1a1a;
}

.cta-subtitle {
    font-size: 1.2rem;
    margin-bottom: 2.5rem;
    color: rgba(26, 26, 26, 0.8);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.cta-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.cta-button {
    padding: 1rem 2.5rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    display: inline-block;
    min-width: 180px;
    text-align: center;
}

.cta-button.primary {
    background: #1a1a1a;
    color: white;
    border: 2px solid #1a1a1a;
}

.cta-button.primary:hover {
    background: transparent;
    color: #1a1a1a;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(26, 26, 26, 0.3);
}

.cta-button.secondary {
    background: transparent;
    color: #1a1a1a;
    border: 2px solid #1a1a1a;
}

.cta-button.secondary:hover {
    background: #1a1a1a;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(26, 26, 26, 0.3);
}

/* Mobile Responsive */
@media (max-width: 1024px) {
    .story-container,
    .impact-container {
        grid-template-columns: 1fr;
        gap: 3rem;
    }
    
    .story-content {
        padding-right: 0;
        text-align: center;
    }
    
    .mvv-container,
    .about-services-grid {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
    
    .team-grid {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
    }
    
    .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
}

@media (max-width: 768px) {
    .about-hero-section {
        padding: 6rem 1rem 4rem;
    }
    
    .company-story-section,
    .mvv-section,
    .what-we-do-section,
    .impact-section,
    .team-section {
        padding: 4rem 1rem;
    }
    
    .about-cta-section {
        padding: 4rem 1rem;
    }
    
    .mvv-container,
    .about-services-grid {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .team-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
    }
    
    .cta-buttons {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .cta-button {
        width: 100%;
        max-width: 300px;
    }
    
    .mvv-card {
        padding: 2rem 1.5rem;
    }
    
    .about-service-card {
        padding: 2rem 1.5rem;
    }
    
    .team-info {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .section-title {
        font-size: 2rem;
    }
    
    .stat-number {
        font-size: 2rem;
    }
    
    .stat-icon {
        font-size: 2rem;
    }
    
    .mvv-icon-container {
        width: 70px;
        height: 70px;
        font-size: 1.5rem;
    }
    
    .service-icon-container {
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
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

# Database connection function (kept for consistency)
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

# Create responsive header component
def create_header():
    return html.Header([
        html.Div([
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
                        html.A("About Us", href="/about_us/", className="nav-link active"),
                        html.A("Newsroom", href="/newsroom/", className="nav-link"),
                        html.A("Contact Us", href="/contact/", className="nav-link"),
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
            ], className="header-container section-container")
        ])
    ], className="main-header")

# Create hero section for About Us
def create_about_hero():
    return html.Section([
        html.Div([
            html.Div([
                html.H1("About CaelumSpace", className="about-hero-title"),
                html.P("Revolutionizing storage solutions with innovative technology and exceptional service", className="about-hero-subtitle")
            ], className="about-hero-content")
        ], className="about-hero-container section-container")
    ], className="about-hero-section")

# Create company story section
def create_company_story():
    return html.Section([
        html.Div([
            html.Div([
                html.Div([
                    html.H2("Our Story", className="section-title"),
                    html.P("Founded in 2018, CaelumSpace emerged from a simple yet powerful vision: to transform the way people think about storage. What began as a small startup with a passion for innovation has grown into a leading provider of premium storage solutions.", className="story-paragraph"),
                    html.P("Our founders recognized that traditional storage facilities were outdated, inconvenient, and failed to meet the evolving needs of modern consumers and businesses. They envisioned a future where storage would be seamless, secure, and accessible through cutting-edge technology.", className="story-paragraph"),
                    html.P("Today, CaelumSpace operates multiple state-of-the-art facilities across the region, serving thousands of satisfied customers who trust us with their most valuable possessions.", className="story-paragraph")
                ], className="story-content"),
                html.Div([
                    html.Img(src="https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", 
                            alt="CaelumSpace Facility", className="story-image")
                ], className="story-image-container")
            ], className="story-container")
        ], className="section-container")
    ], className="company-story-section")

# Create mission, vision, values section
def create_mission_vision_values():
    return html.Section([
        html.Div([
            html.H2("Our Foundation", className="section-title center"),
            html.Div([
                # Mission
                html.Div([
                    html.Div([
                        html.I(className="fas fa-bullseye")
                    ], className="mvv-icon-container"),
                    html.H3("Our Mission", className="mvv-title"),
                    html.P("To provide innovative, secure, and accessible storage solutions that simplify our customers' lives while exceeding their expectations through exceptional service and cutting-edge technology.", className="mvv-description")
                ], className="mvv-card"),
                
                # Vision
                html.Div([
                    html.Div([
                        html.I(className="fas fa-eye")
                    ], className="mvv-icon-container"),
                    html.H3("Our Vision", className="mvv-title"),
                    html.P("To be the global leader in smart storage solutions, creating a world where storing and accessing belongings is effortless, secure, and perfectly integrated into people's daily lives.", className="mvv-description")
                ], className="mvv-card"),
                
                # Values
                html.Div([
                    html.Div([
                        html.I(className="fas fa-heart")
                    ], className="mvv-icon-container"),
                    html.H3("Our Values", className="mvv-title"),
                    html.Ul([
                        html.Li("Security First - Your trust is our foundation"),
                        html.Li("Innovation - Constantly evolving to serve you better"),
                        html.Li("Transparency - Clear pricing, honest communication"),
                        html.Li("Excellence - Exceeding expectations in every interaction"),
                        html.Li("Sustainability - Protecting our environment for future generations")
                    ], className="values-list")
                ], className="mvv-card values-card")
            ], className="mvv-container")
        ], className="section-container")
    ], className="mvv-section")

# Create what we do section
def create_what_we_do():
    services = [
        {
            "icon": "fas fa-warehouse",
            "title": "Premium Storage Facilities",
            "description": "State-of-the-art climate-controlled facilities with advanced security systems and 24/7 monitoring to protect your belongings."
        },
        {
            "icon": "fas fa-mobile-alt",
            "title": "Smart Technology Platform",
            "description": "Our innovative digital platform allows you to manage your storage, make payments, and access your unit remotely with ease."
        },
        {
            "icon": "fas fa-truck",
            "title": "Logistics & Moving Services",
            "description": "Comprehensive moving and logistics support to make your storage experience seamless from start to finish."
        },
        {
            "icon": "fas fa-users",
            "title": "Business Solutions",
            "description": "Tailored storage solutions for businesses of all sizes, including inventory management and document storage."
        },
        {
            "icon": "fas fa-home",
            "title": "Personal Storage",
            "description": "Flexible storage options for personal belongings, seasonal items, and life transitions with convenient access."
        },
        {
            "icon": "fas fa-shield-alt",
            "title": "Insurance & Protection",
            "description": "Comprehensive insurance options and advanced security measures to ensure your items are always protected."
        }
    ]
    
    return html.Section([
        html.Div([
            html.H2("What We Do", className="section-title center"),
            html.P("CaelumSpace offers a comprehensive range of storage solutions designed to meet the diverse needs of our customers", className="section-subtitle center"),
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className=service['icon'])
                    ], className="service-icon-container"),
                    html.H4(service['title'], className="service-title"),
                    html.P(service['description'], className="service-description")
                ], className="about-service-card") for service in services
            ], className="about-services-grid")
        ], className="section-container")  # Added section-container
    ], className="what-we-do-section")

# Create impact section
def create_impact_section():
    stats = [
        {"number": "10,000+", "label": "Satisfied Customers", "icon": "fas fa-users"},
        {"number": "25+", "label": "Storage Facilities", "icon": "fas fa-building"},
        {"number": "50,000+", "label": "Storage Units", "icon": "fas fa-boxes"},
        {"number": "99.9%", "label": "Uptime Guarantee", "icon": "fas fa-clock"},
        {"number": "24/7", "label": "Customer Support", "icon": "fas fa-headset"},
        {"number": "5 Years", "label": "Industry Experience", "icon": "fas fa-award"}
    ]
    
    return html.Section([
        html.Div([
            html.H2("Our Impact", className="section-title center"),
            html.P("Making a difference in communities through reliable storage solutions and exceptional service", className="section-subtitle center"),
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className=stat['icon'])
                    ], className="stat-icon"),
                    html.Div(stat['number'], className="stat-number"),
                    html.Div(stat['label'], className="stat-label")
                ], className="stat-card") for stat in stats
            ], className="stats-grid"),
            
            html.Div([
                html.Div([
                    html.H3("Community Commitment", className="impact-subtitle"),
                    html.P("We believe in giving back to the communities we serve. Through partnerships with local charities, educational initiatives, and environmental sustainability programs, CaelumSpace is committed to making a positive impact beyond storage.", className="impact-description"),
                    html.P("Our green initiatives include solar-powered facilities, recycling programs, and carbon-neutral operations, ensuring that our growth contributes to a sustainable future.", className="impact-description")
                ], className="impact-content"),
                html.Div([
                    html.Img(src="https://images.unsplash.com/photo-1559136555-9303baea8ebd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", 
                            alt="Community Impact", className="impact-image")
                ], className="impact-image-container")
            ], className="impact-container")
        ], className="section-container")  # Added section-container
    ], className="impact-section")

# Create team section
def create_team_section():
    team_members = [
        {
            "name": "Sarah Johnson",
            "position": "Chief Executive Officer",
            "image": "https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "description": "With over 15 years in logistics and technology, Sarah leads CaelumSpace's vision for innovative storage solutions."
        },
        {
            "name": "Michael Chen",
            "position": "Chief Technology Officer",
            "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "description": "Michael spearheads our technology initiatives, ensuring our platform remains at the forefront of innovation."
        },
        {
            "name": "Emily Rodriguez",
            "position": "Head of Operations",
            "image": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "description": "Emily oversees daily operations across all facilities, maintaining our high standards of service and security."
        },
        {
            "name": "David Thompson",
            "position": "Customer Experience Director",
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "description": "David ensures every customer interaction exceeds expectations through continuous service improvement."
        }
    ]
    
    return html.Section([
        html.Div([
            html.H2("Meet Our Leadership Team", className="section-title center"),
            html.P("Passionate professionals dedicated to revolutionizing the storage industry", className="section-subtitle center"),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=member['image'], alt=member['name'], className="team-image")
                    ], className="team-image-container"),
                    html.Div([
                        html.H4(member['name'], className="team-name"),
                        html.P(member['position'], className="team-position"),
                        html.P(member['description'], className="team-description")
                    ], className="team-info")
                ], className="team-card") for member in team_members
            ], className="team-grid")
        ], className="section-container")  # Added section-container
    ], className="team-section")

# Create call to action section
def create_cta_section():
    return html.Section([
        html.Div([
            html.H2("Ready to Experience the CaelumSpace Difference?", className="cta-title"),
            html.P("Join thousands of satisfied customers who trust us with their storage needs", className="cta-subtitle"),
            html.Div([
                html.A("Find Storage Units", href="/units/", className="cta-button primary"),
                html.A("Contact Us", href="/contact/", className="cta-button secondary")
            ], className="cta-buttons")
        ], className="section-container")  # Added section-container
    ], className="about-cta-section")

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
            ], className="footer-container section-container"),  # Added section-container
            html.Div([
                html.P("© 2025 CaelumSpace. All rights reserved.")
            ], className="footer-bottom section-container")  # Added section-container
        ])
    ], className="main-footer")

# Main page layout wrapper
def create_about_layout():
    return html.Div([
        create_header(),
        create_about_hero(),
        create_company_story(),
        create_mission_vision_values(),
        create_what_we_do(),
        create_impact_section(),
        create_team_section(),
        create_cta_section(),
        create_footer()
    ], className="page-container")


# Set the initial layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
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
    """Toggle mobile menu without DOM manipulation"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# URL routing callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=False
)
def display_page(pathname):
    """Handle URL routing"""
    return create_about_layout()