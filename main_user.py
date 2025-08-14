import dash
from dash import dcc, html, Input, Output, State, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
from datetime import datetime, date
import uuid

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: #ffffff;
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            /* Main container */
            #react-entry-point {
                background: transparent;
                min-height: 100vh;
                padding: 0;
            }
            
            /* Header styling */
            h1 {
                background: linear-gradient(90deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.8rem;
                font-weight: 700;
                text-align: center;
                padding: 2rem 0;
                margin-bottom: 0;
                text-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
                position: relative;
            }
            
            h1::after {
                content: '';
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 3px;
                background: linear-gradient(90deg, #FFD700, #FFA500);
                border-radius: 2px;
            }
            
            /* Tab navigation styling - Modern menu design */
            .tab-container {
                background: rgba(26, 26, 26, 0.95);
                backdrop-filter: blur(10px);
                border-bottom: 2px solid #FFD700;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                position: sticky;
                top: 0;
                z-index: 1000;
                margin-bottom: 2rem;
            }
            
            ._dash-undo-redo {
                display: none;
            }
            
            .tab-container .tab {
                background: transparent !important;
                border: none !important;
                border-radius: 0 !important;
                color: #cccccc !important;
                font-weight: 500 !important;
                font-size: 1rem !important;
                padding: 1.2rem 2rem !important;
                margin: 0 !important;
                position: relative !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                cursor: pointer !important;
                overflow: hidden !important;
            }
            
            .tab-container .tab::before {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                width: 0;
                height: 3px;
                background: linear-gradient(90deg, #FFD700, #FFA500);
                transition: all 0.3s ease;
                transform: translateX(-50%);
            }
            
            .tab-container .tab:hover {
                background: rgba(255, 215, 0, 0.1) !important;
                color: #FFD700 !important;
                transform: translateY(-2px) !important;
            }
            
            .tab-container .tab:hover::before {
                width: 80%;
            }
            
            .tab-container .tab.tab--selected {
                background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.1)) !important;
                color: #FFD700 !important;
                font-weight: 600 !important;
                box-shadow: inset 0 -3px 0 #FFD700 !important;
            }
            
            .tab-container .tab.tab--selected::before {
                width: 100%;
            }
            
            /* Content area */
            #tab-content {
                padding: 2rem 3rem !important;
                max-width: 1400px;
                margin: 0 auto;
                animation: fadeIn 0.5s ease-in-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Card styling */
            .summary-card {
                background: linear-gradient(145deg, rgba(26, 26, 26, 0.9), rgba(45, 45, 45, 0.9)) !important;
                border: 1px solid rgba(255, 215, 0, 0.3) !important;
                border-radius: 16px !important;
                padding: 2rem 1.5rem !important;
                margin: 1rem !important;
                text-align: center !important;
                width: 200px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                position: relative !important;
                overflow: hidden !important;
                backdrop-filter: blur(10px) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
            }
            
            .summary-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, #FFD700, transparent);
                transition: left 0.5s ease;
            }
            
            .summary-card:hover {
                transform: translateY(-8px) scale(1.02) !important;
                border-color: #FFD700 !important;
                box-shadow: 0 20px 40px rgba(255, 215, 0, 0.2) !important;
            }
            
            .summary-card:hover::before {
                left: 100%;
            }
            
            .summary-card h3 {
                font-size: 2.5rem !important;
                font-weight: 700 !important;
                color: #FFD700 !important;
                margin-bottom: 0.5rem !important;
                text-shadow: 0 2px 4px rgba(255, 215, 0, 0.3) !important;
            }
            
            .summary-card p {
                font-size: 0.9rem !important;
                color: #cccccc !important;
                font-weight: 500 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            
            /* Section headings */
            h2 {
                color: #FFD700 !important;
                font-size: 2rem !important;
                font-weight: 600 !important;
                margin-bottom: 2rem !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                position: relative !important;
                padding-left: 1rem !important;
            }
            
            h2::before {
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 4px;
                height: 100%;
                background: linear-gradient(180deg, #FFD700, #FFA500);
                border-radius: 2px;
            }
            
            h3 {
                color: #FFD700 !important;
                font-size: 1.4rem !important;
                font-weight: 600 !important;
                margin: 1.5rem 0 1rem 0 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            
            /* Form styling */
            input[type="text"], input[type="email"], textarea, .Select-control {
                background: rgba(45, 45, 45, 0.9) !important;
                border: 2px solid rgba(255, 215, 0, 0.3) !important;
                border-radius: 8px !important;
                color: #ffffff !important;
                padding: 12px 16px !important;
                font-size: 1rem !important;
                font-family: 'Inter', sans-serif !important;
                transition: all 0.3s ease !important;
                backdrop-filter: blur(10px) !important;
            }
            
            input[type="text"]:focus, input[type="email"]:focus, textarea:focus {
                border-color: #FFD700 !important;
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.3) !important;
                outline: none !important;
                background: rgba(45, 45, 45, 1) !important;
            }
            
            input::placeholder, textarea::placeholder {
                color: #999999 !important;
            }
            
            /* Dropdown styling */
            .Select-control, .dropdown .Select-control {
                background: rgba(45, 45, 45, 0.9) !important;
                border: 2px solid rgba(255, 215, 0, 0.3) !important;
                border-radius: 8px !important;
            }
            
            .Select-control:hover {
                border-color: #FFD700 !important;
            }
            
            .Select-menu-outer {
                background: rgba(26, 26, 26, 0.95) !important;
                border: 1px solid #FFD700 !important;
                border-radius: 8px !important;
                backdrop-filter: blur(10px) !important;
            }
            
            .Select-option {
                background: transparent !important;
                color: #ffffff !important;
                padding: 12px 16px !important;
            }
            
            .Select-option:hover {
                background: rgba(255, 215, 0, 0.1) !important;
                color: #FFD700 !important;
            }
            
            .Select-value-label {
                color: #ffffff !important;
            }
            
            /* Button styling */
            button {
                background: linear-gradient(135deg, #FFD700, #FFA500) !important;
                color: #000000 !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 12px 24px !important;
                font-size: 1rem !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
                cursor: pointer !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            button::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transition: all 0.3s ease;
                transform: translate(-50%, -50%);
            }
            
            button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4) !important;
            }
            
            button:hover::before {
                width: 300px;
                height: 300px;
            }
            
            button:active {
                transform: translateY(0) !important;
            }
            
            /* DataTable styling */
            .dash-table-container {
                background: rgba(26, 26, 26, 0.9) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
                border: 1px solid rgba(255, 215, 0, 0.3) !important;
                backdrop-filter: blur(10px) !important;
                margin: 1rem 0 !important;
            }
            
            .dash-table-container .dash-spreadsheet-container {
                background: transparent !important;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner {
                background: transparent !important;
            }
            
            .dash-table-container table {
                background: transparent !important;
                font-family: 'Inter', sans-serif !important;
            }
            
            .dash-table-container th {
                background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.1)) !important;
                color: #FFD700 !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                padding: 16px 12px !important;
                border: none !important;
                font-size: 0.9rem !important;
            }
            
            .dash-table-container td {
                background: rgba(45, 45, 45, 0.5) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 215, 0, 0.1) !important;
                padding: 12px !important;
                font-size: 0.9rem !important;
                transition: background-color 0.2s ease !important;
            }
            
            .dash-table-container tr:hover td {
                background: rgba(255, 215, 0, 0.1) !important;
            }
            
            .dash-table-container .dash-selected-cell {
                background: rgba(255, 215, 0, 0.3) !important;
            }
            
            /* Date picker styling */
            .DateInput {
                background: rgba(45, 45, 45, 0.9) !important;
                border-radius: 8px !important;
            }
            
            .DateInput_input {
                background: transparent !important;
                color: #ffffff !important;
                border: 2px solid rgba(255, 215, 0, 0.3) !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
            }
            
            .DateInput_input:focus {
                border-color: #FFD700 !important;
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.3) !important;
            }
            
            /* Labels */
            label {
                color: #FFD700 !important;
                font-weight: 500 !important;
                margin: 8px 5px !important;
                display: inline-block !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                font-size: 0.9rem !important;
            }
            
            /* Paragraphs and text */
            p {
                color: #cccccc !important;
                line-height: 1.6 !important;
                margin: 8px 0 !important;
            }
            
            /* Success/Error messages */
            div[style*="color: green"] {
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.1)) !important;
                border: 1px solid rgba(34, 197, 94, 0.5) !important;
                border-radius: 8px !important;
                padding: 16px !important;
                margin: 16px 0 !important;
                backdrop-filter: blur(10px) !important;
            }
            
            div[style*="color: red"] {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1)) !important;
                border: 1px solid rgba(239, 68, 68, 0.5) !important;
                border-radius: 8px !important;
                padding: 16px !important;
                margin: 16px 0 !important;
                backdrop-filter: blur(10px) !important;
            }
            
            /* Hr styling */
            hr {
                border: none !important;
                height: 2px !important;
                background: linear-gradient(90deg, transparent, #FFD700, transparent) !important;
                margin: 2rem 0 !important;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(26, 26, 26, 0.5);
            }
            
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #FFD700, #FFA500);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(180deg, #FFA500, #FFD700);
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                h1 {
                    font-size: 2rem !important;
                }
                
                .tab-container .tab {
                    padding: 1rem !important;
                    font-size: 0.9rem !important;
                }
                
                #tab-content {
                    padding: 1rem !important;
                }
                
                .summary-card {
                    width: 160px !important;
                    margin: 0.5rem !important;
                }
                
                input[type="text"], input[type="email"], textarea {
                    width: 100% !important;
                    margin: 5px 0 !important;
                }
            }
            
            /* Loading animation */
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .loading {
                animation: pulse 2s infinite;
            }
            
            /* Glass morphism effect for containers */
            .glass-container {
                background: rgba(26, 26, 26, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 215, 0, 0.2) !important;
                border-radius: 16px !important;
                padding: 2rem !important;
                margin: 1rem 0 !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
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
        </footer>
        <script>
            // Add smooth scroll behavior
            document.addEventListener('DOMContentLoaded', function() {
                // Add glass container class to main divs
                const tabContent = document.getElementById('tab-content');
                if (tabContent) {
                    const childDivs = tabContent.querySelectorAll('div > div');
                    childDivs.forEach(div => {
                        if (div.children.length > 1) {
                            div.classList.add('glass-container');
                        }
                    });
                }
                
                // Add hover effects to cards
                const cards = document.querySelectorAll('.summary-card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-8px) scale(1.02)';
                    });
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0) scale(1)';
                    });
                });
                
                // Add loading states to buttons
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        const originalText = this.textContent;
                        this.textContent = 'Processing...';
                        this.classList.add('loading');
                        
                        setTimeout(() => {
                            this.textContent = originalText;
                            this.classList.remove('loading');
                        }, 2000);
                    });
                });
            });
            
            // Tab switching animation
            document.addEventListener('DOMContentLoaded', function() {
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList' && mutation.target.id === 'tab-content') {
                            const tabContent = document.getElementById('tab-content');
                            if (tabContent) {
                                tabContent.style.opacity = '0';
                                tabContent.style.transform = 'translateY(20px)';
                                
                                setTimeout(() => {
                                    tabContent.style.transition = 'all 0.5s ease';
                                    tabContent.style.opacity = '1';
                                    tabContent.style.transform = 'translateY(0)';
                                }, 50);
                            }
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        </script>
    </body>
</html>
'''

# Database initialization
def init_database():
    conn = sqlite3.connect('warehouse.db')
    cursor = conn.cursor()
    
    # Create warehouses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            location VARCHAR(200) NOT NULL,
            capacity INTEGER NOT NULL,
            status TEXT CHECK(status IN ('active','inactive')) DEFAULT 'active',
            image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create units table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            name VARCHAR(50) NOT NULL,
            status TEXT CHECK(status IN ('active','inactive')) DEFAULT 'active',
            availability TEXT CHECK(availability IN ('not taken','taken','under maintenance','not in use')) DEFAULT 'not taken',
            price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT CHECK(user_type IN ('individual','corporate')) NOT NULL,
            role TEXT CHECK(role IN ('individual','corporate','admin')) DEFAULT 'individual',
            status TEXT CHECK(status IN ('pending','active','suspended','deleted')) DEFAULT 'pending',
            is_verified INTEGER DEFAULT 0,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            country VARCHAR(100),
            state VARCHAR(100),
            city VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER NOT NULL,
            user_id INTEGER,
            customer_name VARCHAR(100) NOT NULL,
            customer_email VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status TEXT CHECK(status IN ('pending','confirmed','cancelled','completed')) DEFAULT 'pending',
            payment_status TEXT CHECK(payment_status IN ('pending','partial','paid','refunded')) DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_method TEXT CHECK(payment_method IN ('cash','card','transfer','online')) NOT NULL,
            transaction_reference VARCHAR(100),
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('pending','completed','failed','refunded')) DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    ''')
    
    # Create complaint categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaint_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_number VARCHAR(20) NOT NULL UNIQUE,
            user_id INTEGER,
            customer_name VARCHAR(100) NOT NULL,
            customer_email VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(20),
            category_id INTEGER NOT NULL,
            subject VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            priority TEXT CHECK(priority IN ('low','medium','high','urgent')) DEFAULT 'medium',
            status TEXT CHECK(status IN ('received','assigned','in_progress','pending_customer','resolved','closed')) DEFAULT 'received',
            booking_id INTEGER,
            payment_id INTEGER,
            assigned_to INTEGER,
            resolution_notes TEXT,
            customer_satisfaction TEXT CHECK(customer_satisfaction IN ('very_satisfied','satisfied','neutral','dissatisfied','very_dissatisfied')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            closed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES complaint_categories(id),
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (payment_id) REFERENCES payments(id)
        )
    ''')
    
    # Insert sample data
    sample_data_exists = cursor.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0]
    if sample_data_exists == 0:
        # Insert sample warehouses
        cursor.execute("INSERT INTO warehouses (name, location, capacity) VALUES (?, ?, ?)", 
                      ("Main Warehouse", "Lagos, Nigeria", 100))
        cursor.execute("INSERT INTO warehouses (name, location, capacity) VALUES (?, ?, ?)", 
                      ("Secondary Warehouse", "Abuja, Nigeria", 50))
        
        # Insert sample units
        for i in range(1, 21):
            cursor.execute("INSERT INTO units (warehouse_id, name, price) VALUES (?, ?, ?)", 
                          (1, f"Unit-A{i:02d}", 5000.00))
        
        for i in range(1, 11):
            cursor.execute("INSERT INTO units (warehouse_id, name, price) VALUES (?, ?, ?)", 
                          (2, f"Unit-B{i:02d}", 4000.00))
        
        # Insert sample complaint categories
        categories = [
            ("Billing Issues", "Problems related to billing and payments"),
            ("Service Quality", "Issues with service delivery"),
            ("Technical Issues", "Technical problems with units or systems"),
            ("Access Problems", "Issues with accessing units or facilities"),
            ("General Inquiry", "General questions and inquiries")
        ]
        for category, desc in categories:
            cursor.execute("INSERT INTO complaint_categories (category_name, description) VALUES (?, ?)", 
                          (category, desc))
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Layout
app.layout = html.Div([
    html.H1("Warehouse Management Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    dcc.Tabs(id="main-tabs", value="summary", children=[
        dcc.Tab(label="Summary", value="summary"),
        dcc.Tab(label="Units & Booking", value="units"),
        dcc.Tab(label="My Bookings", value="bookings"),
        dcc.Tab(label="Payments", value="payments"),
        dcc.Tab(label="Complaints", value="complaints"),
        dcc.Tab(label="Profile", value="profile")
    ]),
    
    html.Div(id="tab-content", style={'padding': '20px'})
])

# Summary Tab Content
def create_summary_tab():
    conn = sqlite3.connect('warehouse.db')
    
    # Get summary statistics
    total_warehouses = pd.read_sql_query("SELECT COUNT(*) as count FROM warehouses WHERE status='active'", conn).iloc[0]['count']
    total_units = pd.read_sql_query("SELECT COUNT(*) as count FROM units WHERE status='active'", conn).iloc[0]['count']
    available_units = pd.read_sql_query("SELECT COUNT(*) as count FROM units WHERE availability='not taken' AND status='active'", conn).iloc[0]['count']
    total_bookings = pd.read_sql_query("SELECT COUNT(*) as count FROM bookings", conn).iloc[0]['count']
    active_bookings = pd.read_sql_query("SELECT COUNT(*) as count FROM bookings WHERE status IN ('pending', 'confirmed')", conn).iloc[0]['count']
    total_complaints = pd.read_sql_query("SELECT COUNT(*) as count FROM complaints", conn).iloc[0]['count']
    pending_complaints = pd.read_sql_query("SELECT COUNT(*) as count FROM complaints WHERE status NOT IN ('resolved', 'closed')", conn).iloc[0]['count']
    
    # Revenue data
    revenue_data = pd.read_sql_query("""
        SELECT SUM(total_amount) as total_revenue,
               SUM(CASE WHEN payment_status = 'paid' THEN total_amount ELSE 0 END) as paid_revenue
        FROM bookings
    """, conn)
    
    total_revenue = revenue_data.iloc[0]['total_revenue'] or 0
    paid_revenue = revenue_data.iloc[0]['paid_revenue'] or 0
    
    conn.close()
    
    return html.Div([
        html.H2("Dashboard Summary"),
        html.Div([
            html.Div([
                html.H3(str(total_warehouses)),
                html.P("Active Warehouses")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
            
            html.Div([
                html.H3(f"{available_units}/{total_units}"),
                html.P("Available Units")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
            
            html.Div([
                html.H3(f"{active_bookings}/{total_bookings}"),
                html.P("Active Bookings")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
            
            html.Div([
                html.H3(f"{pending_complaints}/{total_complaints}"),
                html.P("Pending Complaints")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
            
            html.Div([
                html.H3(f"₦{paid_revenue:,.2f}"),
                html.P("Paid Revenue")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
            
            html.Div([
                html.H3(f"₦{total_revenue:,.2f}"),
                html.P("Total Revenue")
            ], className="summary-card", style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'})
        ])
    ])

# Units Tab Content
def create_units_tab():
    conn = sqlite3.connect('warehouse.db')
    
    # Get available units
    units_df = pd.read_sql_query("""
        SELECT u.id, u.name, w.name as warehouse_name, w.location, u.price, u.availability
        FROM units u
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE u.status = 'active'
        ORDER BY w.name, u.name
    """, conn)
    
    conn.close()
    
    return html.Div([
        html.H2("Units & Booking"),
        html.Div([
            html.H3("Available Units"),
            dash_table.DataTable(
                id='units-table',
                columns=[
                    {"name": "Unit ID", "id": "id"},
                    {"name": "Unit Name", "id": "name"},
                    {"name": "Warehouse", "id": "warehouse_name"},
                    {"name": "Location", "id": "location"},
                    {"name": "Price (₦)", "id": "price", "type": "numeric", "format": {"specifier": ",.0f"}},
                    {"name": "Status", "id": "availability"}
                ],
                data=units_df.to_dict('records'),
                row_selectable="single",
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{availability} = not taken'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{availability} = taken'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    }
                ]
            )
        ]),
        
        html.Hr(),
        
        html.Div([
            html.H3("Book a Unit"),
            html.Div(id="booking-form", children=[
                html.P("Please select a unit from the table above to start booking."),
                html.Div(id="selected-unit-info"),
                
                dcc.Input(id="customer-name", type="text", placeholder="Full Name", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
                dcc.Input(id="customer-email", type="email", placeholder="Email", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
                dcc.Input(id="customer-phone", type="text", placeholder="Phone Number", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
                
                html.Br(),
                html.Label("Start Date:"),
                dcc.DatePickerSingle(id="start-date", date=date.today(), style={'margin': '5px'}),
                
                html.Label("End Date:"),
                dcc.DatePickerSingle(id="end-date", date=date.today(), style={'margin': '5px'}),
                
                html.Br(),
                dcc.Textarea(id="booking-notes", placeholder="Additional notes (optional)", style={'margin': '5px', 'padding': '10px', 'width': '600px', 'height': '80px'}),
                
                html.Br(),
                html.Div(id="booking-total"),
                
                html.Br(),
                html.Button("Book Unit", id="book-unit-btn", n_clicks=0, style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
                
                html.Div(id="booking-result")
            ])
        ])
    ])

# Bookings Tab Content
def create_bookings_tab():
    conn = sqlite3.connect('warehouse.db')
    
    bookings_df = pd.read_sql_query("""
        SELECT b.id, b.customer_name, b.customer_email, u.name as unit_name, 
               w.name as warehouse_name, b.start_date, b.end_date, b.total_amount,
               b.status, b.payment_status, b.created_at
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN warehouses w ON u.warehouse_id = w.id
        ORDER BY b.created_at DESC
    """, conn)
    
    conn.close()
    
    return html.Div([
        html.H2("My Bookings"),
        dash_table.DataTable(
            id='bookings-table',
            columns=[
                {"name": "Booking ID", "id": "id"},
                {"name": "Customer", "id": "customer_name"},
                {"name": "Email", "id": "customer_email"},
                {"name": "Unit", "id": "unit_name"},
                {"name": "Warehouse", "id": "warehouse_name"},
                {"name": "Start Date", "id": "start_date"},
                {"name": "End Date", "id": "end_date"},
                {"name": "Amount (₦)", "id": "total_amount", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Status", "id": "status"},
                {"name": "Payment Status", "id": "payment_status"},
                {"name": "Created", "id": "created_at"}
            ],
            data=bookings_df.to_dict('records'),
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{status} = confirmed'},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                },
                {
                    'if': {'filter_query': '{status} = cancelled'},
                    'backgroundColor': '#f8d7da',
                    'color': 'black',
                }
            ],
            page_size=10
        )
    ])

# Payments Tab Content
def create_payments_tab():
    conn = sqlite3.connect('warehouse.db')
    
    payments_df = pd.read_sql_query("""
        SELECT p.id, p.booking_id, b.customer_name, p.amount, p.payment_method,
               p.transaction_reference, p.payment_date, p.status
        FROM payments p
        JOIN bookings b ON p.booking_id = b.id
        ORDER BY p.payment_date DESC
    """, conn)
    
    conn.close()
    
    return html.Div([
        html.H2("Payments"),
        dash_table.DataTable(
            id='payments-table',
            columns=[
                {"name": "Payment ID", "id": "id"},
                {"name": "Booking ID", "id": "booking_id"},
                {"name": "Customer", "id": "customer_name"},
                {"name": "Amount (₦)", "id": "amount", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Method", "id": "payment_method"},
                {"name": "Reference", "id": "transaction_reference"},
                {"name": "Date", "id": "payment_date"},
                {"name": "Status", "id": "status"}
            ],
            data=payments_df.to_dict('records'),
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{status} = completed'},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                },
                {
                    'if': {'filter_query': '{status} = failed'},
                    'backgroundColor': '#f8d7da',
                    'color': 'black',
                }
            ],
            page_size=10
        )
    ])

# Complaints Tab Content
def create_complaints_tab():
    conn = sqlite3.connect('warehouse.db')
    
    complaints_df = pd.read_sql_query("""
        SELECT c.id, c.complaint_number, c.customer_name, c.customer_email,
               cc.category_name, c.subject, c.priority, c.status, c.created_at
        FROM complaints c
        JOIN complaint_categories cc ON c.category_id = cc.id
        ORDER BY c.created_at DESC
    """, conn)
    
    categories_df = pd.read_sql_query("SELECT id, category_name FROM complaint_categories WHERE is_active = 1", conn)
    bookings_df = pd.read_sql_query("SELECT id FROM bookings", conn)
    
    conn.close()
    
    return html.Div([
        html.H2("Complaints"),
        
        html.Div([
            html.H3("Submit New Complaint"),
            dcc.Input(id="complaint-customer-name", type="text", placeholder="Full Name", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Input(id="complaint-customer-email", type="email", placeholder="Email", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Input(id="complaint-customer-phone", type="text", placeholder="Phone Number", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            
            html.Br(),
            dcc.Dropdown(
                id="complaint-category",
                options=[{"label": row['category_name'], "value": row['id']} for _, row in categories_df.iterrows()],
                placeholder="Select Category",
                style={'margin': '5px', 'width': '300px'}
            ),
            
            dcc.Dropdown(
                id="complaint-priority",
                options=[
                    {"label": "Low", "value": "low"},
                    {"label": "Medium", "value": "medium"},
                    {"label": "High", "value": "high"},
                    {"label": "Urgent", "value": "urgent"}
                ],
                value="medium",
                style={'margin': '5px', 'width': '300px'}
            ),
            
            dcc.Input(id="complaint-subject", type="text", placeholder="Subject", style={'margin': '5px', 'padding': '10px', 'width': '600px'}),
            
            dcc.Textarea(id="complaint-description", placeholder="Description", style={'margin': '5px', 'padding': '10px', 'width': '600px', 'height': '100px'}),
            
            dcc.Dropdown(
                id="complaint-booking-id",
                options=[{"label": f"Booking #{row['id']}", "value": row['id']} for _, row in bookings_df.iterrows()],
                placeholder="Related Booking (optional)",
                style={'margin': '5px', 'width': '300px'}
            ),
            
            html.Br(),
            html.Button("Submit Complaint", id="submit-complaint-btn", n_clicks=0, style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
            
            html.Div(id="complaint-result")
        ]),
        
        html.Hr(),
        
        html.Div([
            html.H3("My Complaints"),
            dash_table.DataTable(
                id='complaints-table',
                columns=[
                    {"name": "ID", "id": "id"},
                    {"name": "Number", "id": "complaint_number"},
                    {"name": "Customer", "id": "customer_name"},
                    {"name": "Email", "id": "customer_email"},
                    {"name": "Category", "id": "category_name"},
                    {"name": "Subject", "id": "subject"},
                    {"name": "Priority", "id": "priority"},
                    {"name": "Status", "id": "status"},
                    {"name": "Created", "id": "created_at"}
                ],
                data=complaints_df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{status} = resolved'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{priority} = urgent'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    }
                ],
                page_size=10
            )
        ])
    ])

# Profile Tab Content
def create_profile_tab():
    return html.Div([
        html.H2("User Profile"),
        html.P("Profile management functionality will be implemented here."),
        html.Div([
            dcc.Input(id="profile-first-name", type="text", placeholder="First Name", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Input(id="profile-last-name", type="text", placeholder="Last Name", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Input(id="profile-email", type="email", placeholder="Email", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Input(id="profile-phone", type="text", placeholder="Phone", style={'margin': '5px', 'padding': '10px', 'width': '300px'}),
            dcc.Textarea(id="profile-address", placeholder="Address", style={'margin': '5px', 'padding': '10px', 'width': '600px', 'height': '80px'}),
            html.Br(),
            html.Button("Update Profile", id="update-profile-btn", n_clicks=0, style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
        ])
    ])

# Main tab content callback
@app.callback(Output('tab-content', 'children'),
              Input('main-tabs', 'value'))
def render_content(active_tab):
    if active_tab == 'summary':
        return create_summary_tab()
    elif active_tab == 'units':
        return create_units_tab()
    elif active_tab == 'bookings':
        return create_bookings_tab()
    elif active_tab == 'payments':
        return create_payments_tab()
    elif active_tab == 'complaints':
        return create_complaints_tab()
    elif active_tab == 'profile':
        return create_profile_tab()

# Unit selection callback
@app.callback(
    Output('selected-unit-info', 'children'),
    Output('booking-total', 'children'),
    Input('units-table', 'selected_rows'),
    State('units-table', 'data'),
    Input('start-date', 'date'),
    Input('end-date', 'date')
)
def update_selected_unit(selected_rows, table_data, start_date, end_date):
    if not selected_rows:
        return "No unit selected.", ""
    
    selected_unit = table_data[selected_rows[0]]
    
    if selected_unit['availability'] != 'not taken':
        return html.Div([
            html.P(f"Selected Unit: {selected_unit['name']} - {selected_unit['warehouse_name']}", style={'color': 'red'}),
            html.P("This unit is not available for booking.")
        ]), ""
    
    # Calculate total amount
    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        days = (end - start).days
        if days > 0:
            total = days * selected_unit['price']
            return html.Div([
                html.P(f"Selected Unit: {selected_unit['name']} - {selected_unit['warehouse_name']}", style={'color': 'green'}),
                html.P(f"Price: ₦{selected_unit['price']:,.2f} per day")
            ]), html.P(f"Total Amount: ₦{total:,.2f} ({days} days)", style={'fontWeight': 'bold', 'fontSize': '18px'})
    
    return html.Div([
        html.P(f"Selected Unit: {selected_unit['name']} - {selected_unit['warehouse_name']}", style={'color': 'green'}),
        html.P(f"Price: ₦{selected_unit['price']:,.2f} per day")
    ]), ""

# Booking submission callback
@app.callback(
    Output('booking-result', 'children'),
    Input('book-unit-btn', 'n_clicks'),
    State('units-table', 'selected_rows'),
    State('units-table', 'data'),
    State('customer-name', 'value'),
    State('customer-email', 'value'),
    State('customer-phone', 'value'),
    State('start-date', 'date'),
    State('end-date', 'date'),
    State('booking-notes', 'value')
)
def submit_booking(n_clicks, selected_rows, table_data, customer_name, customer_email, 
                  customer_phone, start_date, end_date, notes):
    if n_clicks == 0:
        return ""
    
    if not all([selected_rows, customer_name, customer_email, customer_phone, start_date, end_date]):
        return html.Div("Please fill in all required fields and select a unit.", style={'color': 'red'})
    
    selected_unit = table_data[selected_rows[0]]
    
    if selected_unit['availability'] != 'not taken':
        return html.Div("Selected unit is not available for booking.", style={'color': 'red'})
    
    # Calculate total amount
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    days = (end - start).days
    
    if days <= 0:
        return html.Div("End date must be after start date.", style={'color': 'red'})
    
    total_amount = days * selected_unit['price']
    
    try:
        conn = sqlite3.connect('warehouse.db')
        cursor = conn.cursor()
        
        # Insert booking
        cursor.execute("""
            INSERT INTO bookings (unit_id, customer_name, customer_email, customer_phone,
                                start_date, end_date, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (selected_unit['id'], customer_name, customer_email, customer_phone,
              start_date, end_date, total_amount, notes or ''))
        
        booking_id = cursor.lastrowid
        
        # Update unit availability
        cursor.execute("UPDATE units SET availability = 'taken' WHERE id = ?", (selected_unit['id'],))
        
        # Create a payment record
        transaction_ref = f"TXN-{datetime.now().strftime('%Y%m%d')}-{booking_id:04d}"
        cursor.execute("""
            INSERT INTO payments (booking_id, amount, payment_method, transaction_reference, status)
            VALUES (?, ?, 'online', ?, 'pending')
        """, (booking_id, total_amount, transaction_ref))
        
        conn.commit()
        conn.close()
        
        return html.Div([
            html.P(f"Booking successful! Booking ID: {booking_id}", style={'color': 'green', 'fontWeight': 'bold'}),
            html.P(f"Transaction Reference: {transaction_ref}"),
            html.P(f"Total Amount: ₦{total_amount:,.2f}"),
            html.P("Payment is pending. Please proceed to payments section to complete payment.")
        ])
        
    except Exception as e:
        return html.Div(f"Error creating booking: {str(e)}", style={'color': 'red'})

# Complaint submission callback
@app.callback(
    Output('complaint-result', 'children'),
    Input('submit-complaint-btn', 'n_clicks'),
    State('complaint-customer-name', 'value'),
    State('complaint-customer-email', 'value'),
    State('complaint-customer-phone', 'value'),
    State('complaint-category', 'value'),
    State('complaint-priority', 'value'),
    State('complaint-subject', 'value'),
    State('complaint-description', 'value'),
    State('complaint-booking-id', 'value')
)
def submit_complaint(n_clicks, customer_name, customer_email, customer_phone,
                    category_id, priority, subject, description, booking_id):
    if n_clicks == 0:
        return ""
    
    if not all([customer_name, customer_email, category_id, subject, description]):
        return html.Div("Please fill in all required fields.", style={'color': 'red'})
    
    try:
        conn = sqlite3.connect('warehouse.db')
        cursor = conn.cursor()
        
        # Generate complaint number
        complaint_number = f"CMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Insert complaint
        cursor.execute("""
            INSERT INTO complaints (complaint_number, customer_name, customer_email, customer_phone,
                                  category_id, subject, description, priority, booking_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (complaint_number, customer_name, customer_email, customer_phone or '',
              category_id, subject, description, priority or 'medium', booking_id))
        
        complaint_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return html.Div([
            html.P(f"Complaint submitted successfully! Complaint ID: {complaint_id}", style={'color': 'green', 'fontWeight': 'bold'}),
            html.P(f"Complaint Number: {complaint_number}"),
            html.P("We will review your complaint and get back to you soon.")
        ])
        
    except Exception as e:
        return html.Div(f"Error submitting complaint: {str(e)}", style={'color': 'red'})

# Refresh data callbacks for dynamic updates
@app.callback(
    Output('units-table', 'data'),
    Input('main-tabs', 'value')
)
def refresh_units_data(active_tab):
    if active_tab == 'units':
        conn = sqlite3.connect('warehouse.db')
        units_df = pd.read_sql_query("""
            SELECT u.id, u.name, w.name as warehouse_name, w.location, u.price, u.availability
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            WHERE u.status = 'active'
            ORDER BY w.name, u.name
        """, conn)
        conn.close()
        return units_df.to_dict('records')
    return []

@app.callback(
    Output('bookings-table', 'data'),
    Input('main-tabs', 'value')
)
def refresh_bookings_data(active_tab):
    if active_tab == 'bookings':
        conn = sqlite3.connect('warehouse.db')
        bookings_df = pd.read_sql_query("""
            SELECT b.id, b.customer_name, b.customer_email, u.name as unit_name, 
                   w.name as warehouse_name, b.start_date, b.end_date, b.total_amount,
                   b.status, b.payment_status, b.created_at
            FROM bookings b
            JOIN units u ON b.unit_id = u.id
            JOIN warehouses w ON u.warehouse_id = w.id
            ORDER BY b.created_at DESC
        """, conn)
        conn.close()
        return bookings_df.to_dict('records')
    return []

@app.callback(
    Output('payments-table', 'data'),
    Input('main-tabs', 'value')
)
def refresh_payments_data(active_tab):
    if active_tab == 'payments':
        conn = sqlite3.connect('warehouse.db')
        payments_df = pd.read_sql_query("""
            SELECT p.id, p.booking_id, b.customer_name, p.amount, p.payment_method,
                   p.transaction_reference, p.payment_date, p.status
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            ORDER BY p.payment_date DESC
        """, conn)
        conn.close()
        return payments_df.to_dict('records')
    return []

@app.callback(
    Output('complaints-table', 'data'),
    Input('main-tabs', 'value')
)
def refresh_complaints_data(active_tab):
    if active_tab == 'complaints':
        conn = sqlite3.connect('warehouse.db')
        complaints_df = pd.read_sql_query("""
            SELECT c.id, c.complaint_number, c.customer_name, c.customer_email,
                   cc.category_name, c.subject, c.priority, c.status, c.created_at
            FROM complaints c
            JOIN complaint_categories cc ON c.category_id = cc.id
            ORDER BY c.created_at DESC
        """, conn)
        conn.close()
        return complaints_df.to_dict('records')
    return []

if __name__ == "__main__":
    app.run(debug=True)