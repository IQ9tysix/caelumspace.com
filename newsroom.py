import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/newsroom/",
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

              /* Newsroom Hero Section */
        .newsroom-hero-section {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 120px 0 80px;
            position: relative;
            overflow: hidden;
        }

        .newsroom-hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="%23FFD700" stroke-width="0.5" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }

        .newsroom-hero-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 2;
        }

        .newsroom-hero-content {
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
        }

        .newsroom-hero-title {
            font-size: clamp(3rem, 6vw, 5rem);
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1.5rem;
            letter-spacing: -0.02em;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .newsroom-hero-subtitle {
            font-size: 1.25rem;
            color: #cccccc;
            margin-bottom: 3rem;
            line-height: 1.7;
            font-weight: 400;
        }

        .newsroom-filters {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 16px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 215, 0, 0.2);
        }

        .filter-btn {
            background: transparent;
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .filter-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .filter-btn:hover::before {
            left: 100%;
        }

        .filter-btn:hover,
        .filter-btn.active {
            background: #FFD700;
            color: #1a1a1a;
            border-color: #FFD700;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        }

        /* Featured Story Section */
        .featured-story-section {
            padding: 100px 0;
            background: linear-gradient(to bottom, #f8f9fa, #ffffff);
            position: relative;
        }

        .featured-story-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .featured-story-card {
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: grid;
            grid-template-columns: 1fr 1fr;
            align-items: center;
            position: relative;
            border: 1px solid rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }

        .featured-story-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15);
        }

        .featured-content {
            padding: 4rem;
        }

        .featured-category {
            display: inline-block;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #1a1a1a;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1.5rem;
        }

        .featured-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 1.5rem;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }

        .featured-excerpt {
            font-size: 1.1rem;
            color: #666666;
            margin-bottom: 2rem;
            line-height: 1.7;
        }

        .featured-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .featured-meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #888888;
            font-size: 0.9rem;
        }

        .featured-meta-item i {
            color: #FFD700;
        }

        .featured-cta-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #1a1a1a, #333333);
            color: #ffffff;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .featured-cta-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .featured-cta-btn:hover::before {
            left: 100%;
        }

        .featured-cta-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(26, 26, 26, 0.3);
        }

        .featured-image-container {
            position: relative;
            overflow: hidden;
        }

        .featured-image {
            width: 100%;
            height: 500px;
            object-fit: cover;
            transition: transform 0.5s ease;
        }

        .featured-story-card:hover .featured-image {
            transform: scale(1.05);
        }

        /* News Grid Section */
        .news-section {
            padding: 100px 0;
            background: #ffffff;
        }

        .news-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .news-section-header {
            text-align: center;
            margin-bottom: 4rem;
        }

        .news-section-title {
            font-size: 3rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }

        .news-section-subtitle {
            font-size: 1.1rem;
            color: #666666;
            max-width: 600px;
            margin: 0 auto;
        }

        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .article-card {
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.05);
            position: relative;
        }

        .article-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }

        .article-image-container {
            position: relative;
            overflow: hidden;
            height: 250px;
        }

        .article-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }

        .article-card:hover .article-image {
            transform: scale(1.1);
        }

        .article-content {
            padding: 2rem;
        }

        .article-category-container {
            margin-bottom: 1rem;
        }

        .article-category {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .category-press-release {
            background: rgba(255, 215, 0, 0.15);
            color: #B8860B;
        }

        .category-industry-insights {
            background: rgba(26, 26, 26, 0.1);
            color: #1a1a1a;
        }

        .category-news {
            background: rgba(0, 123, 255, 0.1);
            color: #0056b3;
        }

        .category-company-updates {
            background: rgba(40, 167, 69, 0.1);
            color: #155724;
        }

        .article-title {
            margin-bottom: 1rem;
        }

        .article-title-link {
            color: #1a1a1a;
            text-decoration: none;
            font-size: 1.3rem;
            font-weight: 600;
            line-height: 1.3;
            transition: color 0.3s ease;
            display: block;
        }

        .article-title-link:hover {
            color: #FFD700;
        }

        .article-excerpt {
            color: #666666;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }

        .article-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .article-meta-item {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            color: #888888;
            font-size: 0.85rem;
        }

        .article-meta-item i {
            color: #FFD700;
            font-size: 0.8rem;
        }

        .article-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }

        .article-tag {
            background: rgba(26, 26, 26, 0.05);
            color: #666666;
            padding: 0.3rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .article-read-more {
            color: #1a1a1a;
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
            position: relative;
        }

        .article-read-more::after {
            content: '→';
            transition: transform 0.3s ease;
        }

        .article-read-more:hover {
            color: #FFD700;
        }

        .article-read-more:hover::after {
            transform: translateX(5px);
        }

        /* Newsletter Section */
        .newsletter-section {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 100px 0;
            position: relative;
            overflow: hidden;
        }

        .newsletter-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="%23FFD700" opacity="0.1"/></svg>');
            opacity: 0.3;
        }

        .newsletter-wrapper {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 2;
        }

        .newsletter-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 24px;
            padding: 4rem;
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
        }

        .newsletter-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }

        .newsletter-description {
            font-size: 1.1rem;
            color: #cccccc;
            margin-bottom: 2.5rem;
            line-height: 1.6;
        }

        .newsletter-form {
            display: flex;
            max-width: 500px;
            margin: 0 auto 1rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50px;
            padding: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .newsletter-input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 1rem 1.5rem;
            color: #ffffff;
            font-size: 1rem;
            border-radius: 50px;
            outline: none;
        }

        .newsletter-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        .newsletter-btn {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #1a1a1a;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            white-space: nowrap;
        }

        .newsletter-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
        }

        .newsletter-disclaimer {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.85rem;
            max-width: 400px;
            margin: 0 auto;
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

                .newsroom-hero-title {
                font-size: 2.5rem;
            }

            .newsroom-filters {
                padding: 1rem;
            }

            .filter-btn {
                padding: 0.6rem 1.2rem;
                font-size: 0.9rem;
            }

            .featured-story-card {
                grid-template-columns: 1fr;
            }

            .featured-content {
                padding: 2rem;
            }

            .featured-title {
                font-size: 2rem;
            }

            .news-grid {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }

            .newsletter-container {
                padding: 2rem;
            }

            .newsletter-title {
                font-size: 2rem;
            }

            .newsletter-form {
                flex-direction: column;
                padding: 1rem;
            }

            .newsletter-input {
                margin-bottom: 1rem;
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

        .article-card {
            animation: fadeInUp 0.6s ease forwards;
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

# Create responsive header component (same as home)
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
                    html.A("Newsroom", href="/newsroom/", className="nav-link active"),
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
        ], className="header-container")
    ], className="main-header")

# Create footer (same as home)
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

# Create newsroom hero section
def create_newsroom_hero():
    return html.Section([
        html.Div([
            html.Div([
                html.H1("Newsroom", className="newsroom-hero-title"),
                html.P("Stay updated with the latest news, insights, and announcements from CaelumSpace", className="newsroom-hero-subtitle"),
                html.Div([
                    html.Button("All", className="filter-btn active", id="filter-all"),
                    html.Button("News", className="filter-btn", id="filter-news"),
                    html.Button("Press Releases", className="filter-btn", id="filter-press"),
                    html.Button("Industry Insights", className="filter-btn", id="filter-insights"),
                    html.Button("Company Updates", className="filter-btn", id="filter-updates")
                ], className="newsroom-filters")
            ], className="newsroom-hero-content")
        ], className="newsroom-hero-container")
    ], className="newsroom-hero-section")

# Sample data for featured story
def create_featured_story():
    featured_story = {
        "title": "CaelumSpace Expands Operations with Three New State-of-the-Art Facilities",
        "excerpt": "Our commitment to providing premium storage solutions continues as we announce the opening of three new facilities across the region, featuring advanced security systems and climate-controlled units.",
        "date": "January 22, 2025",
        "category": "Press Release",
        "image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
        "read_time": "4 min read",
        "author": "CaelumSpace Communications Team"
    }
    
    return html.Section([
        html.Div([
            html.Div([
                html.Div([
                    html.Span(featured_story['category'], className="featured-category"),
                    html.H2(featured_story['title'], className="featured-title"),
                    html.P(featured_story['excerpt'], className="featured-excerpt"),
                    html.Div([
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-calendar-alt"),
                                html.Span(featured_story['date'])
                            ], className="featured-meta-item"),
                            html.Span([
                                html.I(className="fas fa-clock"),
                                html.Span(featured_story['read_time'])
                            ], className="featured-meta-item"),
                            html.Span([
                                html.I(className="fas fa-user"),
                                html.Span(featured_story['author'])
                            ], className="featured-meta-item")
                        ], className="featured-meta")
                    ], className="featured-meta-container"),
                    html.A("Read Full Story", href="#", className="featured-cta-btn")
                ], className="featured-content"),
                html.Div([
                    html.Img(src=featured_story['image'], alt=featured_story['title'], className="featured-image")
                ], className="featured-image-container")
            ], className="featured-story-card")
        ], className="featured-story-container")
    ], className="featured-story-section")

# Sample data for blog posts and press releases
def get_news_articles():
    return [
        {
            "id": 1,
            "title": "Smart Storage: How Technology is Revolutionizing Self-Storage",
            "excerpt": "Discover how IoT devices, mobile apps, and automated systems are transforming the storage industry for better customer experience.",
            "date": "January 20, 2025",
            "category": "Industry Insights",
            "image": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "6 min read",
            "author": "Sarah Chen",
            "tags": ["Technology", "Innovation", "Customer Experience"]
        },
        {
            "id": 2,
            "title": "CaelumSpace Achieves Carbon Neutral Operations Across All Facilities",
            "excerpt": "We're proud to announce our commitment to environmental sustainability with the achievement of carbon-neutral operations.",
            "date": "January 18, 2025",
            "category": "Press Release",
            "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "3 min read",
            "author": "Environmental Team",
            "tags": ["Sustainability", "Environment", "Corporate Responsibility"]
        },
        {
            "id": 3,
            "title": "5 Essential Tips for Organizing Your Storage Unit",
            "excerpt": "Maximize your storage space efficiency with these professional organizing tips from our storage experts.",
            "date": "January 15, 2025",
            "category": "News",
            "image": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "5 min read",
            "author": "Storage Solutions Team",
            "tags": ["Tips", "Organization", "Storage"]
        },
        {
            "id": 4,
            "title": "Q4 2024 Financial Results: Record Growth and Expansion",
            "excerpt": "CaelumSpace reports strong Q4 performance with 25% year-over-year growth and plans for continued expansion in 2025.",
            "date": "January 12, 2025",
            "category": "Company Updates",
            "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "4 min read",
            "author": "Investor Relations",
            "tags": ["Financial", "Growth", "Business"]
        },
        {
            "id": 5,
            "title": "The Future of Urban Storage: Trends and Predictions for 2025",
            "excerpt": "Industry experts weigh in on emerging trends shaping the future of storage solutions in urban environments.",
            "date": "January 10, 2025",
            "category": "Industry Insights",
            "image": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "7 min read",
            "author": "Industry Research Team",
            "tags": ["Future", "Urban Planning", "Trends"]
        },
        {
            "id": 6,
            "title": "Enhanced Security Measures: New Biometric Access System Launch",
            "excerpt": "CaelumSpace introduces cutting-edge biometric access control systems across premium facilities for enhanced security.",
            "date": "January 8, 2025",
            "category": "Press Release",
            "image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "3 min read",
            "author": "Security Department",
            "tags": ["Security", "Technology", "Innovation"]
        },
        {
            "id": 7,
            "title": "Moving in Winter: Essential Tips for Cold Weather Storage",
            "excerpt": "Navigate winter moving challenges with our comprehensive guide to cold weather storage preparation and protection.",
            "date": "January 5, 2025",
            "category": "News",
            "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "4 min read",
            "author": "Customer Care Team",
            "tags": ["Winter", "Moving", "Tips"]
        },
        {
            "id": 8,
            "title": "CaelumSpace Partners with Local Charities for Community Storage Initiative",
            "excerpt": "New partnership program provides discounted storage solutions for local non-profit organizations and community groups.",
            "date": "January 3, 2025",
            "category": "Company Updates",
            "image": "https://images.unsplash.com/photo-1559513529-4e9a6c3f3e0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "3 min read",
            "author": "Community Relations",
            "tags": ["Community", "Partnership", "Social Impact"]
        },
        {
            "id": 9,
            "title": "Year in Review: 2024 Achievements and Milestones",
            "excerpt": "Celebrating a year of growth, innovation, and excellence in storage solutions as we look back at 2024's key achievements.",
            "date": "December 30, 2024",
            "category": "Company Updates",
            "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "read_time": "6 min read",
            "author": "Executive Team",
            "tags": ["Annual Review", "Achievements", "Growth"]
        }
    ]

# Create news articles grid
def create_news_grid():
    articles = get_news_articles()
    
    article_cards = []
    for article in articles:
        article_cards.append(
            html.Article([
                html.Div([
                    html.Img(src=article['image'], alt=article['title'], className="article-image")
                ], className="article-image-container"),
                html.Div([
                    html.Div([
                        html.Span(article['category'], className=f"article-category category-{article['category'].lower().replace(' ', '-')}")
                    ], className="article-category-container"),
                    html.H3([
                        html.A(article['title'], href=f"/article/{article['id']}", className="article-title-link")
                    ], className="article-title"),
                    html.P(article['excerpt'], className="article-excerpt"),
                    html.Div([
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-calendar-alt"),
                                html.Span(article['date'])
                            ], className="article-meta-item"),
                            html.Span([
                                html.I(className="fas fa-clock"),
                                html.Span(article['read_time'])
                            ], className="article-meta-item"),
                            html.Span([
                                html.I(className="fas fa-user"),
                                html.Span(article['author'])
                            ], className="article-meta-item")
                        ], className="article-meta")
                    ], className="article-meta-container"),
                    html.Div([
                        html.Span(tag, className="article-tag") for tag in article['tags']
                    ], className="article-tags"),
                    html.A("Read More", href=f"/article/{article['id']}", className="article-read-more")
                ], className="article-content")
            ], className="article-card", **{"data-category": article['category'].lower().replace(' ', '-')})
        )
    
    return html.Section([
        html.Div([
            html.Div([
                html.H2("Latest News & Updates", className="news-section-title"),
                html.P("Stay informed with our latest developments, industry insights, and company announcements", className="news-section-subtitle")
            ], className="news-section-header"),
            html.Div(article_cards, className="news-grid", id="news-grid")
        ], className="news-container")
    ], className="news-section")

# Create newsletter signup section
def create_newsletter_section():
    return html.Section([
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Stay Updated", className="newsletter-title"),
                    html.P("Subscribe to our newsletter for the latest news, insights, and storage tips delivered to your inbox.", className="newsletter-description")
                ], className="newsletter-content"),
                html.Div([
                    html.Div([
                        dcc.Input(
                            type="email",
                            placeholder="Enter your email address",
                            className="newsletter-input",
                            id="newsletter-email"
                        ),
                        html.Button([
                            html.I(className="fas fa-paper-plane"),
                            html.Span("Subscribe")
                        ], className="newsletter-btn", id="newsletter-subscribe")
                    ], className="newsletter-form"),
                    html.P("By subscribing, you agree to our Privacy Policy and Terms of Service.", className="newsletter-disclaimer")
                ], className="newsletter-signup")
            ], className="newsletter-container")
        ], className="newsletter-wrapper")
    ], className="newsletter-section")

# Create main newsroom layout
def create_newsroom_layout():
    return html.Div([
        create_header(),
        html.Main([
            create_newsroom_hero(),
            create_featured_story(),
            create_news_grid(),
            create_newsletter_section()
        ], className="newsroom-main"),
        create_footer()
    ], className="newsroom-page")


# Set the layout
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
    """Toggle mobile menu"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# Filter functionality for news articles
@app.callback(
    [Output('filter-all', 'className'),
     Output('filter-news', 'className'),
     Output('filter-press', 'className'),
     Output('filter-insights', 'className'),
     Output('filter-updates', 'className')],
    [Input('filter-all', 'n_clicks'),
     Input('filter-news', 'n_clicks'),
     Input('filter-press', 'n_clicks'),
     Input('filter-insights', 'n_clicks'),
     Input('filter-updates', 'n_clicks')],
    prevent_initial_call=True
)
def update_filter_buttons(*args):
    """Update active filter button styling"""
    ctx = dash.callback_context
    
    # Default all buttons to inactive
    button_classes = ["filter-btn"] * 5
    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'filter-all':
            button_classes[0] = "filter-btn active"
        elif button_id == 'filter-news':
            button_classes[1] = "filter-btn active"
        elif button_id == 'filter-press':
            button_classes[2] = "filter-btn active"
        elif button_id == 'filter-insights':
            button_classes[3] = "filter-btn active"
        elif button_id == 'filter-updates':
            button_classes[4] = "filter-btn active"
    else:
        button_classes[0] = "filter-btn active"  # Default to "All" active
    
    return button_classes

# Newsletter subscription callback
@app.callback(
    Output('newsletter-email', 'value'),
    [Input('newsletter-subscribe', 'n_clicks')],
    [State('newsletter-email', 'value')],
    prevent_initial_call=True
)
def handle_newsletter_subscription(n_clicks, email_value):
    """Handle newsletter subscription"""
    if n_clicks and email_value:
        # Here you would typically save the email to your database
        # For now, we'll just clear the input
        return ""
    return email_value

# URL routing callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=False
)
def display_page(pathname):
    """Handle URL routing"""
    return create_newsroom_layout()
