import dash
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from server import server
from datetime import datetime, timedelta, date
import hashlib
import secrets
import pyodbc
import re
from flask import request, session
import logging
import mysql.connector
from mysql.connector import Error
import json
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/book_now/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
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
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    overflow-x: hidden;
    min-height: 100vh;
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
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
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
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
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

/* Main Content Styling */
main {
    margin-top: 80px;
    min-height: calc(100vh - 80px);
}

/* Breadcrumb */
.breadcrumb {
    background: none;
    padding: 1rem 0;
    margin-bottom: 2rem;
    font-size: 0.9rem;
}

.breadcrumb a {
    color: #666;
    text-decoration: none;
    transition: color 0.3s ease;
}

.breadcrumb a:hover {
    color: #FFD700;
}

.breadcrumb span {
    color: #999;
    margin: 0 0.5rem;
}

/* Booking Progress Steps */
.booking-progress {
    margin-bottom: 3rem;
    padding: 2rem 0;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.05) 0%, rgba(255, 255, 255, 0.8) 100%);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.progress-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    max-width: 800px;
    margin: 0 auto;
    position: relative;
}

.progress-container::before {
    content: '';
    position: absolute;
    top: 25px;
    left: 15%;
    right: 15%;
    height: 2px;
    background: linear-gradient(90deg, #FFD700 50%, #e0e0e0 50%);
    z-index: 1;
}

.progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    z-index: 2;
}

.step-number {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    border: 3px solid #e0e0e0;
    background: #fff;
    color: #999;
    transition: all 0.3s ease;
}

.step-number.completed {
    background: #FFD700;
    border-color: #FFD700;
    color: #1a1a1a;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.step-number.active {
    background: #1a1a1a;
    border-color: #1a1a1a;
    color: #fff;
    box-shadow: 0 4px 15px rgba(26, 26, 26, 0.3);
}

.progress-step small {
    font-size: 0.85rem;
    font-weight: 500;
    color: #666;
    white-space: nowrap;
}

/* Section Titles */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
    position: relative;
    padding-bottom: 0.5rem;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #FFD700, #ffd700aa);
    border-radius: 2px;
}

/* Unit Summary Card */
.unit-summary {
    margin-bottom: 2.5rem;
}

.unit-summary-card {
    background: #fff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 215, 0, 0.1);
    display: flex;
    gap: 1.5rem;
    align-items: center;
    transition: all 0.3s ease;
}

.unit-summary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.unit-image {
    width: 120px;
    height: 90px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid rgba(255, 215, 0, 0.2);
}

.unit-info h4 {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

.unit-info p {
    color: #666;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.unit-info p i {
    color: #FFD700;
}

.unit-details {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.unit-detail {
    background: rgba(255, 215, 0, 0.1);
    color: #1a1a1a;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid rgba(255, 215, 0, 0.2);
}

/* Customer Form */
.customer-form {
    background: #fff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 215, 0, 0.1);
}

.form-label {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
    display: block;
    font-size: 0.95rem;
}

.form-control {
    width: 100%;
    padding: 0.8rem 1rem;
    border: 2px solid #e8ecef;
    border-radius: 12px;
    font-size: 0.95rem;
    background: #fafbfc;
    transition: all 0.3s ease;
    outline: none;
}

.form-control:focus {
    border-color: #FFD700;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
    transform: translateY(-1px);
}

.form-control::placeholder {
    color: #a0a5ab;
    font-style: italic;
}

.mb-3 {
    margin-bottom: 1.5rem;
}

.text-danger {
    color: #dc3545;
}

.small {
    font-size: 0.85rem;
}

/* Cost Summary */
.cost-summary {
    position: sticky;
    top: 100px;
}

.cost-summary-card {
    background: linear-gradient(145deg, #fff 0%, #fafbfc 100%);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
    border: 2px solid rgba(255, 215, 0, 0.15);
}

.cost-breakdown {
    space-y: 1rem;
}

.cost-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.cost-item:last-child {
    border-bottom: none;
}

.cost-label {
    font-weight: 500;
    color: #555;
}

.cost-value {
    font-weight: 600;
    color: #1a1a1a;
}

.cost-item.subtotal {
    background: rgba(255, 215, 0, 0.08);
    margin: 0 -1rem;
    padding: 1rem;
    border-radius: 12px;
    border: none;
}

.cost-item.total {
    background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
    color: #fff;
    margin: 1rem -1rem 0;
    padding: 1.2rem;
    border-radius: 15px;
    font-size: 1.1rem;
}

.cost-item.total .cost-label,
.cost-item.total .cost-value {
    color: #fff;
}

.fw-bold {
    font-weight: 700;
}

.text-primary {
    color: #FFD700 !important;
}

/* Action Buttons */
.action-buttons {
    margin-top: 2rem;
    display: flex;
    gap: 1rem;
    justify-content: space-between;
}

.btn {
    padding: 0.8rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    min-width: 140px;
    justify-content: center;
}

.btn-secondary {
    background: #6c757d;
    color: #fff;
    border: 2px solid #6c757d;
}

.btn-secondary:hover {
    background: #5a6268;
    border-color: #5a6268;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.btn-primary {
    background: linear-gradient(135deg, #FFD700 0%, #ffc107 100%);
    color: #1a1a1a;
    border: 2px solid #FFD700;
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #ffc107 0%, #FFD700 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
}

.me-2 {
    margin-right: 1rem;
}

/* Alert Styles */
.alert {
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid transparent;
}

.alert-warning {
    background: rgba(255, 193, 7, 0.1);
    border-color: rgba(255, 193, 7, 0.2);
    color: #856404;
}

/* Footer */
.main-footer {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: white;
    padding: 4rem 2rem 2rem;
    margin-top: 4rem;
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
    position: relative;
}

.footer-section h4::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 30px;
    height: 2px;
    background: #FFD700;
    border-radius: 1px;
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

/* Responsive Design */
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

    .progress-container {
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }

    .progress-container::before {
        display: none;
    }

    .unit-summary-card {
        flex-direction: column;
        text-align: center;
    }

    .unit-image {
        width: 100%;
        max-width: 200px;
        height: 150px;
    }

    .unit-details {
        justify-content: center;
    }

    .cost-summary {
        position: static;
        margin-top: 2rem;
    }

    .action-buttons {
        flex-direction: column;
    }

    .btn {
        width: 100%;
        margin-right: 0 !important;
        margin-bottom: 0.5rem;
    }
}

@media (max-width: 576px) {
    .booking-progress {
        margin: 1rem -15px 2rem;
        border-radius: 0;
    }

    .unit-summary-card,
    .customer-form,
    .cost-summary-card {
        margin: 0 -15px;
        border-radius: 0;
    }

    .section-title {
        font-size: 1.2rem;
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

@keyframes slideInFromLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.unit-summary-card,
.customer-form,
.cost-summary-card {
    animation: fadeInUp 0.6s ease-out;
}

.progress-step {
    animation: slideInFromLeft 0.4s ease-out;
}

.progress-step:nth-child(2) {
    animation-delay: 0.1s;
}

.progress-step:nth-child(3) {
    animation-delay: 0.2s;
}

.progress-step:nth-child(4) {
    animation-delay: 0.3s;
}

/* Hover effects for interactive elements */
.unit-summary-card,
.customer-form {
    transition: all 0.3s ease;
}

.form-control,
.btn,
.cost-summary-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Focus styles for accessibility */
.btn:focus,
.form-control:focus {
    outline: 2px solid #FFD700;
    outline-offset: 2px;
}

/* Container spacing */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -15px;
}

.col-md-8 {
    flex: 0 0 66.666667%;
    max-width: 66.666667%;
    padding: 0 15px;
}

.col-md-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
    padding: 0 15px;
}

@media (max-width: 768px) {
    .col-md-8,
    .col-md-4 {
        flex: 0 0 100%;
        max-width: 100%;
    }
}

/* Page title styling */
.page-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    text-align: center;
    margin: 6rem auto 1rem;
    color: #1a1a1a;
    padding: 0 2rem;
    background: linear-gradient(135deg, #1a1a1a 0%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.page-subtitle {
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 3rem;
    color: #666;
    padding: 0 2rem;
}

/* Enhanced visual hierarchy */
.py-4 {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.py-5 {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

.mb-4 {
    margin-bottom: 1.5rem;
}

.mt-4 {
    margin-top: 1.5rem;
}

/* Glass morphism effect for cards */
.unit-summary-card,
.customer-form,
.cost-summary-card {
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #FFD700, #ffc107);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ffc107, #FFD700);
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
# Constants
INSURANCE_PLANS = {
    'basic': {'name': 'Basic Protection', 'cost': 5000},
    'premium': {'name': 'Premium Coverage', 'cost': 10000},
    'comprehensive': {'name': 'Comprehensive Shield', 'cost': 15000}
}

SERVICE_FEE_RATE = 0.05  # 5%
TAX_RATE = 0.075  # 7.5%

class DatabaseManager:
    """Centralized database operations"""
    
    @staticmethod
    def get_connection():
        """Establish MySQL database connection"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='warehouse_db',
                user='root',
                password='',
                autocommit=True
            )
            return connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False):
        """Execute database query safely"""
        connection = DatabaseManager.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            return result
        except Error as e:
            logger.error(f"Query execution error: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class BookingService:
    """Business logic for booking operations"""
    
    @staticmethod
    def get_booking_details(booking_id):
        """Fetch complete booking information"""
        if not booking_id or not str(booking_id).isdigit():
            return None
        
        query = """
        SELECT 
            b.id as booking_id,
            b.customer_name,
            b.customer_email,
            b.customer_phone,
            b.start_date,
            b.end_date,
            b.total_amount,
            b.status as booking_status,
            b.payment_status,
            b.notes,
            b.created_at,
            u.id as unit_id,
            u.name as unit_name,
            u.price as unit_price,
            u.availability,
            w.id as warehouse_id,
            w.name as warehouse_name,
            w.location as warehouse_location,
            w.capacity as warehouse_capacity,
            w.image_path as warehouse_image,
            w.status as warehouse_status
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE b.id = %s AND b.status != 'cancelled'
        """
        
        result = DatabaseManager.execute_query(query, (booking_id,), fetch_one=True)
        
        if result:
            # Convert Decimal to float for JSON serialization
            for key, value in result.items():
                if isinstance(value, Decimal):
                    result[key] = float(value)
        
        return result
    
    @staticmethod
    def parse_booking_notes(notes):
        """Extract structured data from booking notes"""
        default_details = {
            'units_count': 1,
            'duration': 1,
            'insurance_plan': None,
            'insurance_cost': 0
        }
        
        if not notes:
            return default_details
        
        try:
            # Extract units count
            units_match = re.search(r'Units:\s*(\d+)', notes)
            if units_match:
                default_details['units_count'] = int(units_match.group(1))
            
            # Extract duration
            duration_match = re.search(r'Duration:\s*(\d+)', notes)
            if duration_match:
                default_details['duration'] = int(duration_match.group(1))
            
            # Extract insurance
            insurance_match = re.search(r'Insurance:\s*([^(]+)\s*\(₦(\d+)', notes)
            if insurance_match:
                default_details['insurance_plan'] = insurance_match.group(1).strip()
                default_details['insurance_cost'] = int(insurance_match.group(2))
        
        except Exception as e:
            logger.error(f"Error parsing booking notes: {e}")
        
        return default_details
    
    @staticmethod
    def get_user_info(user_id):
        """Get user information for form pre-filling"""
        if not user_id:
            return None
        
        query = """
        SELECT 
            id, user_type,
            CASE 
                WHEN user_type = 'corporate' THEN contact_first_name
                ELSE first_name 
            END as first_name,
            CASE 
                WHEN user_type = 'corporate' THEN contact_last_name
                ELSE last_name 
            END as last_name,
            CASE 
                WHEN user_type = 'corporate' THEN contact_email
                ELSE email 
            END as email,
            CASE 
                WHEN user_type = 'corporate' THEN contact_phone
                ELSE phone 
            END as phone,
            CASE 
                WHEN user_type = 'corporate' THEN company_name
                ELSE NULL 
            END as company_name
        FROM users WHERE id = %s
        """
        
        return DatabaseManager.execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def update_customer_info(booking_id, customer_data):
        """Update booking with customer information"""
        query = """
        UPDATE bookings 
        SET customer_name = %s, customer_email = %s, customer_phone = %s,
            updated_at = NOW()
        WHERE id = %s
        """
        
        connection = DatabaseManager.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute(query, (
                customer_data['name'],
                customer_data['email'], 
                customer_data['phone'],
                booking_id
            ))
            success = cursor.rowcount > 0
            return success
        except Error as e:
            logger.error(f"Error updating customer info: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class CostCalculator:
    """Handle all cost calculations"""
    
    @staticmethod
    def calculate_costs(unit_price, units_count, duration, insurance_cost=0):
        """Calculate complete booking costs"""
        try:
            unit_price = float(unit_price or 0)
            units_count = int(units_count or 1)
            duration = int(duration or 1)
            insurance_cost = float(insurance_cost or 0)
            
            # Base calculations
            unit_cost = unit_price * units_count
            insurance_monthly = insurance_cost * units_count
            monthly_total = unit_cost + insurance_monthly
            duration_total = monthly_total * duration
            
            # Fees
            service_fee = round(duration_total * SERVICE_FEE_RATE, 2)
            tax = round(duration_total * TAX_RATE, 2)
            final_total = duration_total + service_fee + tax
            
            return {
                'unit_cost': unit_cost,
                'insurance_cost': insurance_monthly,
                'monthly_total': monthly_total,
                'duration_total': duration_total,
                'service_fee': service_fee,
                'tax': tax,
                'final_total': final_total
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Cost calculation error: {e}")
            return {key: 0 for key in ['unit_cost', 'insurance_cost', 'monthly_total', 
                                     'duration_total', 'service_fee', 'tax', 'final_total']}

class FormValidator:
    """Handle form validation"""
    
    @staticmethod
    def validate_name(name):
        """Validate customer name"""
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters"
        if len(name.strip()) > 100:
            return False, "Name is too long"
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """Validate email address"""
        if not email:
            return False, "Email is required"
        
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email.strip()):
            return False, "Please enter a valid email address"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        if not phone:
            return False, "Phone number is required"
        
        # Remove spaces and special characters for validation
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not clean_phone.replace('+', '').isdigit() or len(clean_phone) < 10:
            return False, "Please enter a valid phone number"
        
        return True, ""
    
    @staticmethod
    def validate_form(name, email, phone):
        """Validate entire form"""
        name_valid, name_msg = FormValidator.validate_name(name)
        email_valid, email_msg = FormValidator.validate_email(email)
        phone_valid, phone_msg = FormValidator.validate_phone(phone)
        
        return {
            'name_valid': name_valid,
            'name_msg': name_msg,
            'email_valid': email_valid,
            'email_msg': email_msg,
            'phone_valid': phone_valid,
            'phone_msg': phone_msg,
            'form_valid': name_valid and email_valid and phone_valid
        }

# UI Components
def create_header():
    """Create responsive header"""
    return html.Header([
        html.Div([
            html.Div([
                html.Img(src="./assets/images/logo.jpg", alt="CaelumSpace Logo", className="logo")
            ], className="logo-container"),
            
            html.Button([
                html.I(className="fas fa-bars")
            ], className="mobile-menu-toggle", id="mobile-menu-toggle"),
            
            html.Nav([
                html.Div([
                    html.A("Home", href="/home/", className="nav-link"),
                    html.A("Warehouse & Units", href="/units/", className="nav-link"),
                    html.A("About Us", href="/about/", className="nav-link"),
                    html.A("Our Services", href="/services/", className="nav-link"),
                    html.A("Contact Us", href="/contact/", className="nav-link"),
                    html.A([html.I(className="fas fa-user-plus"), " Signup"], 
                           href="/signup/", className="nav-link auth-link"),
                    html.A([html.I(className="fas fa-sign-in-alt"), " Login"], 
                           href="/login/", className="nav-link auth-link"),
                ], className="nav-links"),
                
                html.Button([html.I(className="fas fa-times")], 
                           className="mobile-menu-close", id="mobile-menu-close")
            ], className="nav-menu", id="nav-menu")
        ], className="header-container")
    ], className="main-header")

def create_footer():
    """Create footer component"""
    return html.Footer([
        html.Div([
            html.Div([
                html.Div([
                    html.H4("CaelumSpace"),
                    html.P("Premium storage solutions for modern living.")
                ], className="footer-section"),
                html.Div([
                    html.H4("Quick Links"),
                    html.Ul([
                        html.Li(html.A("Find Units", href="/units/")),
                        html.Li(html.A("About Us", href="/about/")),
                        html.Li(html.A("Contact", href="/contact/"))
                    ])
                ], className="footer-section"),
                html.Div([
                    html.H4("Contact Info"),
                    html.P("📧 info@caelumspace.com"),
                    html.P("📞 +1 (555) 123-4567")
                ], className="footer-section")
            ], className="footer-container"),
            html.Hr(),
            html.P("© 2025 CaelumSpace. All rights reserved.", className="text-center")
        ])
    ], className="main-footer")

def create_progress_steps():
    """Create booking progress indicator"""
    return html.Div([
        html.Div([
            html.Div([
                html.Span("1", className="step-number completed"),
                html.Small("Unit Selected")
            ], className="progress-step"),
            html.Div([
                html.Span("2", className="step-number active"),
                html.Small("Booking Details")
            ], className="progress-step"),
            html.Div([
                html.Span("3", className="step-number"),
                html.Small("Payment")
            ], className="progress-step"),
            html.Div([
                html.Span("4", className="step-number"),
                html.Small("Confirmation")
            ], className="progress-step")
        ], className="progress-container")
    ], className="booking-progress")

def create_unit_summary(booking_data, booking_details):
    """Create unit information summary"""
    if not booking_data:
        return html.Div("Booking information not available", className="alert alert-warning")
    
    image_src = booking_data.get('warehouse_image') or './assets/images/default-warehouse.jpg'
    
    return html.Div([
        html.H3("Selected Unit", className="section-title"),
        html.Div([
            html.Img(src=image_src, alt="Warehouse", className="unit-image"),
            html.Div([
                html.H4(booking_data.get('unit_name', 'Unit')),
                html.P([
                    html.I(className="fas fa-map-marker-alt"),
                    f" {booking_data.get('warehouse_name', 'Warehouse')} - {booking_data.get('warehouse_location', 'Location')}"
                ]),
                html.Div([
                    html.Span(f"Units: {booking_details.get('units_count', 1)}", className="unit-detail"),
                    html.Span(f"Duration: {booking_details.get('duration', 1)} month(s)", className="unit-detail"),
                    html.Span(f"Insurance: {booking_details.get('insurance_plan') or 'None'}", className="unit-detail")
                ], className="unit-details")
            ], className="unit-info")
        ], className="unit-summary-card")
    ], className="unit-summary")

def create_customer_form(booking_data, user_info):
    """Create customer information form"""
    # Pre-fill with existing data
    default_name = ""
    default_email = ""
    default_phone = ""
    
    if booking_data:
        default_name = booking_data.get('customer_name', '')
        default_email = booking_data.get('customer_email', '')  
        default_phone = booking_data.get('customer_phone', '')
    
    if user_info and not default_name:
        first_name = user_info.get('first_name', '') or ''
        last_name = user_info.get('last_name', '') or ''
        default_name = f"{first_name} {last_name}".strip()
        default_email = user_info.get('email', '') or default_email
        default_phone = user_info.get('phone', '') or default_phone
    
    return html.Div([
        html.H3("Customer Information", className="section-title"),
        html.Form([
            html.Div([
                html.Label("Full Name *", className="form-label"),
                dcc.Input(
                    id="customer-name",
                    type="text",
                    value=default_name,
                    placeholder="Enter your full name",
                    className="form-control",
                    required=True
                ),
                html.Div(id="name-error", className="text-danger small")
            ], className="mb-3"),
            
            html.Div([
                html.Label("Email Address *", className="form-label"),
                dcc.Input(
                    id="customer-email",
                    type="email",
                    value=default_email,
                    placeholder="Enter your email address",
                    className="form-control",
                    required=True
                ),
                html.Div(id="email-error", className="text-danger small")
            ], className="mb-3"),
            
            html.Div([
                html.Label("Phone Number *", className="form-label"),
                dcc.Input(
                    id="customer-phone",
                    type="tel",
                    value=default_phone,
                    placeholder="Enter your phone number",
                    className="form-control",
                    required=True
                ),
                html.Div(id="phone-error", className="text-danger small")
            ], className="mb-3"),
            
            html.Div([
                html.Label("Special Instructions (Optional)", className="form-label"),
                dcc.Textarea(
                    id="special-instructions",
                    placeholder="Any special requests or instructions...",
                    className="form-control",
                    rows=3
                )
            ], className="mb-3")
        ])
    ], className="customer-form")

def create_cost_summary(booking_data, booking_details):
    """Create cost breakdown summary"""
    if not booking_data:
        return html.Div("Cost information not available", className="alert alert-warning")
    
    costs = CostCalculator.calculate_costs(
        booking_data.get('unit_price', 0),
        booking_details.get('units_count', 1),
        booking_details.get('duration', 1),
        booking_details.get('insurance_cost', 0)
    )
    
    return html.Div([
        html.H3("Cost Summary", className="section-title"),
        html.Div([
            html.Div([
                html.Div([
                    html.Span(f"Unit Cost (×{booking_details.get('units_count', 1)})", className="cost-label"),
                    html.Span(f"₦{costs['unit_cost']:,.0f}", className="cost-value")
                ], className="cost-item"),
                
                *([html.Div([
                    html.Span(f"Insurance (×{booking_details.get('units_count', 1)})", className="cost-label"),
                    html.Span(f"₦{costs['insurance_cost']:,.0f}", className="cost-value")
                ], className="cost-item")] if costs['insurance_cost'] > 0 else []),
                
                html.Hr(),
                
                html.Div([
                    html.Span("Monthly Total", className="cost-label"),
                    html.Span(f"₦{costs['monthly_total']:,.0f}", className="cost-value")
                ], className="cost-item subtotal"),
                
                html.Div([
                    html.Span(f"Duration ({booking_details.get('duration', 1)} months)", className="cost-label"),
                    html.Span(f"₦{costs['duration_total']:,.0f}", className="cost-value")
                ], className="cost-item"),
                
                html.Div([
                    html.Span("Service Fee", className="cost-label small"),
                    html.Span(f"₦{costs['service_fee']:,.2f}", className="cost-value small")
                ], className="cost-item"),
                
                html.Div([
                    html.Span("Caution (7.5%)", className="cost-label small"),
                    html.Span(f"₦{costs['tax']:,.2f}", className="cost-value small")
                ], className="cost-item"),
                
                html.Hr(className="border-dark"),
                
                html.Div([
                    html.Span("Total Amount", className="cost-label fw-bold"),
                    html.Span(f"₦{costs['final_total']:,.2f}", className="cost-value fw-bold text-primary")
                ], className="cost-item total")
            ], className="cost-breakdown")
        ], className="cost-summary-card")
    ], className="cost-summary")

def create_action_buttons():
    """Create form action buttons"""
    return html.Div([
        html.Button([
            html.I(className="fas fa-arrow-left"),
            " Back to Units"
        ], className="btn btn-secondary me-2", id="back-btn"),
        
        html.Button([
            html.I(className="fas fa-credit-card"),
            " Proceed to Payment"
        ], className="btn btn-primary", id="proceed-btn", disabled=False)
    ], className="action-buttons justify-content-between mt-4")

def create_confirmation_modal():
    """Create booking confirmation modal"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirm Your Booking")),
        dbc.ModalBody([
            html.Div(id="confirmation-details"),
            html.Hr(),
            html.Div([
                dbc.Checklist(
                    id="terms-checkbox",
                    options=[{"label": " I agree to the Terms of Service and Privacy Policy", "value": "agreed"}],
                    value=[],
                    className="mb-2"
                ),
                html.Small([
                    html.A("Terms of Service", href="/terms/", target="_blank"),
                    " | ",
                    html.A("Privacy Policy", href="/privacy/", target="_blank")
                ])
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", color="secondary", id="modal-cancel"),
            dbc.Button("Confirm & Pay", color="primary", id="modal-confirm", disabled=True)
        ])
    ], id="confirmation-modal", is_open=False)

def create_error_page(message="Booking Not Found", description="The requested booking could not be found."):
    """Create error page"""
    return html.Div([
        create_header(),
        html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3"),
                html.H1(message),
                html.P(description, className="lead"),
                html.A("Return Home", href="/home/", className="btn btn-primary")
            ], className="text-center py-5")
        ], className="container"),
        create_footer()
    ])

def create_booking_layout(booking_id):
    """Create complete booking page layout"""
    try:
        booking_data = BookingService.get_booking_details(booking_id)
        
        if not booking_data:
            return create_error_page()
        
        booking_details = BookingService.parse_booking_notes(booking_data.get('notes', ''))
        user_id = session.get('user_id')
        user_info = BookingService.get_user_info(user_id) if user_id else None
        
        return html.Div([
            create_header(),
            
            html.Main([
                html.Div([
                    # Breadcrumb
                    html.Nav([
                        html.A("Home", href="/home/"),
                        html.Span(" > "),
                        html.A("Units", href="/units/"),
                        html.Span(" > "),
                        html.Span("Book Now")
                    ], className="breadcrumb mb-4"),
                    
                    create_progress_steps(),
                    
                    html.Div([
                        # Left column
                        html.Div([
                            create_unit_summary(booking_data, booking_details),
                            create_customer_form(booking_data, user_info)
                        ], className="col-md-8"),
                        
                        # Right column  
                        html.Div([
                            create_cost_summary(booking_data, booking_details),
                            create_action_buttons()
                        ], className="col-md-4")
                    ], className="row")
                ], className="container py-4")
            ]),
            
            create_footer(),
            create_confirmation_modal(),
            
            # Data stores
            dcc.Store(id="booking-store", data=booking_data),
            dcc.Store(id="details-store", data=booking_details),
            dcc.Store(id="user-store", data=user_info),
            dcc.Store(id="validation-store", data={'valid': False})
        ])
        
    except Exception as e:
        logger.error(f"Error creating booking layout: {e}")
        return create_error_page("System Error", "An error occurred while loading the page.")

# App layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route URLs to appropriate pages"""
    try:
        if pathname and pathname.startswith('/book_now/'):
            parts = pathname.strip('/').split('/')
            if len(parts) >= 2 and parts[-1].isdigit():
                return create_booking_layout(int(parts[-1]))
        
        return create_error_page("Invalid URL", "Please select a unit to start booking.")
    except Exception as e:
        logger.error(f"Routing error: {e}")
        return create_error_page("System Error", "Unable to process request.")

@app.callback(
    [Output('name-error', 'children'),
     Output('email-error', 'children'), 
     Output('phone-error', 'children'),
     Output('validation-store', 'data')],
    [Input('customer-name', 'value'),
     Input('customer-email', 'value'),
     Input('customer-phone', 'value')],
    prevent_initial_call=True
)
def validate_customer_form(name, email, phone):
    """Validate form inputs in real-time"""
    try:
        validation = FormValidator.validate_form(name, email, phone)
        return (
            validation['name_msg'] if not validation['name_valid'] else "",
            validation['email_msg'] if not validation['email_valid'] else "",
            validation['phone_msg'] if not validation['phone_valid'] else "",
            {'valid': validation['form_valid']}
        )
    except Exception as e:
        logger.error(f"Form validation error: {e}")
        return "", "", "", {'valid': False}

@app.callback(
    [Output('proceed-btn', 'disabled'),
     Output('proceed-btn', 'className')],
    Input('validation-store', 'data'),
    prevent_initial_call=True
)
def update_proceed_button(validation_data):
    """Enable/disable proceed button based on form validity"""
    is_valid = validation_data.get('valid', False) if validation_data else False
    base_class = "btn btn-primary"
    return not is_valid, base_class + ("" if is_valid else " disabled")

@app.callback(
    [Output('confirmation-modal', 'is_open'),
     Output('confirmation-details', 'children')],
    [Input('proceed-btn', 'n_clicks'),
     Input('modal-cancel', 'n_clicks')],
    [State('validation-store', 'data'),
     State('booking-store', 'data'),
     State('details-store', 'data'),
     State('customer-name', 'value'),
     State('customer-email', 'value'), 
     State('customer-phone', 'value')],
    prevent_initial_call=True
)
def toggle_confirmation_modal(proceed_clicks, cancel_clicks, validation_data, 
                            booking_data, booking_details, name, email, phone):
    """Show/hide confirmation modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'modal-cancel':
        return False, ""
    
    if button_id == 'proceed-btn' and proceed_clicks:
        if not validation_data or not validation_data.get('valid'):
            return False, ""
        
        try:
            costs = CostCalculator.calculate_costs(
                booking_data.get('unit_price', 0),
                booking_details.get('units_count', 1),
                booking_details.get('duration', 1),
                booking_details.get('insurance_cost', 0)
            )
            
            details = html.Div([
                html.H5(booking_data.get('unit_name', 'Unit')),
                html.P(f"{booking_data.get('warehouse_name', 'Warehouse')} - {booking_data.get('warehouse_location', 'Location')}"),
                html.Hr(),
                html.P(f"Customer: {name}"),
                html.P(f"Email: {email}"),
                html.P(f"Phone: {phone}"),
                html.P(f"Units: {booking_details.get('units_count', 1)}"),
                html.P(f"Duration: {booking_details.get('duration', 1)} month(s)"),
                html.Hr(),
                html.H5(f"Total: ₦{costs['final_total']:,.2f}", className="text-primary")
            ])
            
            return True, details
        except Exception as e:
            logger.error(f"Error creating confirmation modal: {e}")
            return False, ""
    
    return False, ""

@app.callback(
    [Output('modal-confirm', 'disabled'),
     Output('modal-confirm', 'className')],
    Input('terms-checkbox', 'value'),
    prevent_initial_call=True
)
def update_confirm_button(terms_agreed):
    """Enable confirm button when terms are agreed"""
    is_agreed = terms_agreed and 'agreed' in terms_agreed
    base_class = "btn btn-primary"
    return not is_agreed, base_class + ("" if is_agreed else " disabled")

@app.callback(
    Output('modal-confirm', 'children'),
    Input('modal-confirm', 'n_clicks'),
    [State('terms-checkbox', 'value'),
     State('booking-store', 'data'),
     State('customer-name', 'value'),
     State('customer-email', 'value'),
     State('customer-phone', 'value'),
     State('special-instructions', 'value')],
    prevent_initial_call=True
)
def confirm_booking(n_clicks, terms_agreed, booking_data, name, email, phone, instructions):
    """Handle booking confirmation and redirect to payment"""
    if not n_clicks or not terms_agreed or 'agreed' not in terms_agreed:
        return no_update
    
    try:
        customer_data = {
            'name': name.strip(),
            'email': email.strip(),
            'phone': phone.strip()
        }
        
        booking_id = booking_data.get('booking_id')
        success = BookingService.update_customer_info(booking_id, customer_data)
        
        if success:
            # Store confirmed booking for payment page
            session['confirmed_booking_id'] = booking_id
            
            # Return success indicator for client-side redirect
            return [
                html.I(className="fas fa-check-circle"),
                " Redirecting to Payment..."
            ]
        else:
            return [
                html.I(className="fas fa-exclamation-triangle"),
                " Error - Try Again"
            ]
    except Exception as e:
        logger.error(f"Booking confirmation error: {e}")
        return [
            html.I(className="fas fa-exclamation-triangle"),
            " System Error"
        ]

@app.callback(
    Output('back-btn', 'href'),
    Input('booking-store', 'data')
)
def set_back_button_link(booking_data):
    """Set back button destination"""
    if booking_data and booking_data.get('unit_id'):
        return f"/unit_details/{booking_data['unit_id']}"
    return "/units/"

@app.callback(
    Output('nav-menu', 'className'),
    [Input('mobile-menu-toggle', 'n_clicks'),
     Input('mobile-menu-close', 'n_clicks')],
    State('nav-menu', 'className'),
    prevent_initial_call=True
)
def toggle_mobile_menu(toggle_clicks, close_clicks, current_class):
    """Toggle mobile navigation menu"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_class or "nav-menu"
    
    current_class = current_class or "nav-menu"
    
    if "mobile-active" in current_class:
        return "nav-menu"
    else:
        return "nav-menu mobile-active"

# Client-side callback for payment redirect
app.clientside_callback(
    """
    function(button_content) {
        if (button_content && Array.isArray(button_content) && 
            button_content.length > 1 && 
            button_content[1] === " Redirecting to Payment...") {
            
            setTimeout(function() {
                var pathParts = window.location.pathname.split('/');
                var bookingId = pathParts[pathParts.length - 1];
                if (bookingId && !isNaN(bookingId)) {
                    window.location.href = "/pay_now/" + bookingId;
                }
            }, 2000);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('modal-confirm', 'id'),  # Dummy output
    Input('modal-confirm', 'children')
)

# Error handling wrapper
def handle_callback_errors(func):
    """Decorator to handle callback errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Callback error in {func.__name__}: {e}")
            return no_update
    return wrapper

# Apply error handling to critical callbacks
validate_customer_form = handle_callback_errors(validate_customer_form)
toggle_confirmation_modal = handle_callback_errors(toggle_confirmation_modal)
confirm_booking = handle_callback_errors(confirm_booking)

