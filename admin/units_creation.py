import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pymysql
from datetime import datetime
from server import server
from flask import session, request
import mysql.connector
import base64
import io
import os


# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'warehouse_db'
}

app = Dash(
    __name__,
    url_base_pathname="/admin/units_creation/",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)


class WarehouseDB:
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        return pymysql.connect(**self.config)
    
    def execute_query(self, query, params=None, fetch=True):
        try:
            with self.get_connection() as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query, params)
                    if fetch:
                        return cursor.fetchall()
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Database error: {e}")
            return [] if fetch else 0
    
    # Warehouse CRUD operations
    def get_warehouses(self):
        query = """
        SELECT w.*, 
               COUNT(u.id) as unit_count,
               COUNT(CASE WHEN u.status = 'active' THEN 1 END) as active_units
        FROM warehouses w
        LEFT JOIN units u ON w.id = u.warehouse_id
        GROUP BY w.id
        ORDER BY w.created_at DESC
        """
        return self.execute_query(query)
    
    def get_warehouse_by_id(self, warehouse_id):
        query = "SELECT * FROM warehouses WHERE id = %s"
        result = self.execute_query(query, (warehouse_id,))
        return result[0] if result else None
    
    def create_warehouse(self, name, location, capacity, status, image_path=None):
        query = """
        INSERT INTO warehouses (name, location, capacity, status, image_path, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, location, capacity, status, image_path, datetime.now())
        return self.execute_query(query, params, fetch=False)
    
    def update_warehouse(self, warehouse_id, name, location, capacity, status, image_path=None):
        if image_path:
            query = """
            UPDATE warehouses 
            SET name = %s, location = %s, capacity = %s, status = %s, image_path = %s, updated_at = %s
            WHERE id = %s
            """
            params = (name, location, capacity, status, image_path, datetime.now(), warehouse_id)
        else:
            query = """
            UPDATE warehouses 
            SET name = %s, location = %s, capacity = %s, status = %s, updated_at = %s
            WHERE id = %s
            """
            params = (name, location, capacity, status, datetime.now(), warehouse_id)
        return self.execute_query(query, params, fetch=False)
    
    def delete_warehouse(self, warehouse_id):
        # First delete all units in this warehouse
        self.execute_query("DELETE FROM units WHERE warehouse_id = %s", (warehouse_id,), fetch=False)
        # Then delete the warehouse
        query = "DELETE FROM warehouses WHERE id = %s"
        return self.execute_query(query, (warehouse_id,), fetch=False)
    
    # Unit CRUD operations
    def get_units(self, warehouse_id=None):
        if warehouse_id:
            query = """
            SELECT u.*, w.name as warehouse_name, w.capacity as warehouse_capacity
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            WHERE u.warehouse_id = %s
            ORDER BY u.name
            """
            return self.execute_query(query, (warehouse_id,))
        else:
            query = """
            SELECT u.*, w.name as warehouse_name, w.capacity as warehouse_capacity
            FROM units u
            JOIN warehouses w ON u.warehouse_id = w.id
            ORDER BY w.name, u.name
            """
            return self.execute_query(query)
    
    def get_unit_by_id(self, unit_id):
        query = """
        SELECT u.*, w.name as warehouse_name 
        FROM units u
        JOIN warehouses w ON u.warehouse_id = w.id
        WHERE u.id = %s
        """
        result = self.execute_query(query, (unit_id,))
        return result[0] if result else None
    
    def create_unit(self, warehouse_id, name, status, availability):
        query = """
        INSERT INTO units (warehouse_id, name, status, availability, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (warehouse_id, name, status, availability, datetime.now())
        return self.execute_query(query, params, fetch=False)
    
    def create_bulk_units(self, warehouse_id, count, status, availability):
        # Get current unit count for this warehouse
        current_units = self.get_units(warehouse_id)
        current_count = len(current_units)
        
        success_count = 0
        for i in range(count):
            unit_name = f"Unit {current_count + i + 1}"
            if self.create_unit(warehouse_id, unit_name, status, availability):
                success_count += 1
        
        return success_count
    
    def update_unit(self, unit_id, name, status, availability):
        query = """
        UPDATE units 
        SET name = %s, status = %s, availability = %s, updated_at = %s
        WHERE id = %s
        """
        params = (name, status, availability, datetime.now(), unit_id)
        return self.execute_query(query, params, fetch=False)
    
    def delete_unit(self, unit_id):
        query = "DELETE FROM units WHERE id = %s"
        return self.execute_query(query, (unit_id,), fetch=False)
    
    def check_warehouse_capacity(self, warehouse_id):
        warehouse = self.get_warehouse_by_id(warehouse_id)
        if not warehouse:
            return False, "Warehouse not found"
        
        units = self.get_units(warehouse_id)
        current_count = len(units)
        capacity = warehouse['capacity']
        
        if current_count >= capacity:
            return False, f"Warehouse has reached maximum capacity ({capacity} units). Please increase capacity or create a new warehouse."
        
        return True, f"Available slots: {capacity - current_count}"

# Initialize database
db = WarehouseDB()

# Custom CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
          
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
            // Ensure modals appear above sidebar
            document.addEventListener('DOMContentLoaded', function() {
                // Handle modal z-index issues
                const modals = document.querySelectorAll('.modal');
                modals.forEach(modal => {
                    modal.style.zIndex = '2000';
                });

                // Add mobile menu toggle functionality
                const sidebar = document.querySelector('.sidebar');
                const mainContent = document.querySelector('.main-content');
                
                // Create mobile menu button if screen is small
                if (window.innerWidth <= 768) {
                    const menuButton = document.createElement('button');
                    menuButton.innerHTML = '<i class="fas fa-bars"></i>';
                    menuButton.className = 'mobile-menu-btn';
                    menuButton.style.cssText = `
                        position: fixed;
                        top: 1rem;
                        left: 1rem;
                        z-index: 1001;
                        background: var(--accent-yellow);
                        border: none;
                        border-radius: 8px;
                        padding: 0.75rem;
                        color: var(--primary-black);
                        font-size: 1.2rem;
                        cursor: pointer;
                        box-shadow: 0 4px 15px var(--shadow-light);
                        transition: all 0.3s ease;
                    `;
                    
                    menuButton.addEventListener('click', function() {
                        sidebar.classList.toggle('active');
                    });
                    
                    document.body.appendChild(menuButton);
                    
                    // Close sidebar when clicking outside
                    document.addEventListener('click', function(e) {
                        if (!sidebar.contains(e.target) && !menuButton.contains(e.target)) {
                            sidebar.classList.remove('active');
                        }
                    });
                }

                // Handle window resize
                window.addEventListener('resize', function() {
                    if (window.innerWidth > 768) {
                        sidebar.classList.remove('active');
                        const mobileBtn = document.querySelector('.mobile-menu-btn');
                        if (mobileBtn) {
                            mobileBtn.remove();
                        }
                    }
                });

                // Enhanced form validation
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {
                    const inputs = form.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => {
                        input.addEventListener('invalid', function() {
                            input.style.borderColor = 'var(--danger-color)';
                            input.style.boxShadow = '0 0 0 0.2rem rgba(239, 68, 68, 0.2)';
                        });
                        
                        input.addEventListener('input', function() {
                            if (input.checkValidity()) {
                                input.style.borderColor = 'var(--success-color)';
                                input.style.boxShadow = '0 0 0 0.2rem rgba(16, 185, 129, 0.2)';
                            }
                        });
                    });
                });

                // Auto-hide notifications
                const notifications = document.querySelectorAll('.notification');
                notifications.forEach(notification => {
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.style.animation = 'slideOutRight 0.3s ease-in-out';
                            setTimeout(() => {
                                notification.remove();
                            }, 300);
                        }
                    }, 5000);
                });

                // Smooth scrolling for internal links
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        const target = document.querySelector(this.getAttribute('href'));
                        if (target) {
                            target.scrollIntoView({
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }
                    });
                });

                // Add loading states to buttons
                const buttons = document.querySelectorAll('button[type="submit"]');
                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        const originalText = button.innerHTML;
                        button.innerHTML = '<span class="loading-spinner"></span> Processing...';
                        button.disabled = true;
                        
                        // Reset after 3 seconds (adjust based on your needs)
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.disabled = false;
                        }, 3000);
                    });
                });
            });

            // Add slideOutRight animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
</html>
'''

# Layout components
def create_sidebar():
    return html.Div([
        html.Div([
            html.H3("🏢 Warehouse Admin", className="text-center mb-0"),
            html.P("Management Dashboard", className="text-center mb-0 text-muted")
        ], className="sidebar-header"),
        
        html.Div([
            html.A([
                html.I(className="fas fa-warehouse me-2"),
                "Warehouse Management"
            ], href="#", className="menu-item active"),
            html.A([
                html.I(className="fas fa-boxes me-2"),
                "Unit Management"
            ], href="#", className="menu-item"),
            html.A([
                html.I(className="fas fa-users me-2"),
                "User Management"
            ], href="#", className="menu-item"),
            html.A([
                html.I(className="fas fa-chart-bar me-2"),
                "Reports"
            ], href="#", className="menu-item"),
            html.A([
                html.I(className="fas fa-cog me-2"),
                "Settings"
            ], href="#", className="menu-item")
        ], className="sidebar-menu")
    ], className="sidebar")

def create_header():
    return html.Div([
        html.Div([
            html.H2("Warehouse & Unit Management", className="mb-0"),
            html.Div([
                dbc.Button("+ Add Warehouse", id="add-warehouse-btn", color="primary", className="me-2"),
                dbc.Button("+ Add Unit", id="add-unit-btn", color="success")
            ])
        ], className="d-flex justify-content-between align-items-center")
    ], className="header")

def create_warehouse_table():
    return html.Div([
        html.H4("Warehouse Facilities", className="mb-3"),
        html.Div(id="warehouse-table-container"),
        html.Div(id="warehouse-table-refresh", style={"display": "none"})
    ], className="card p-3")

def create_unit_table():
    return html.Div([
        html.Div([
            html.H4("Storage Units", className="mb-3"),
            html.Div([
                dcc.Dropdown(
                    id="warehouse-filter",
                    placeholder="Filter by warehouse...",
                    className="mb-3",
                    style={"width": "300px"}
                )
            ])
        ], className="d-flex justify-content-between align-items-center mb-3"),
        html.Div(id="unit-table-container"),
        html.Div(id="unit-table-refresh", style={"display": "none"})
    ], className="card p-3")

# Modals
def create_warehouse_modal():
    return dbc.Modal([
        dbc.ModalHeader("Add New Warehouse"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Warehouse Name"),
                        dbc.Input(id="warehouse-name", type="text", placeholder="Enter warehouse name")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Location"),
                        dbc.Input(id="warehouse-location", type="text", placeholder="Enter warehouse location")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Capacity"),
                        dbc.Input(id="warehouse-capacity", type="number", placeholder="Enter maximum units", min=1)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Status"),
                        dbc.Select(
                            id="warehouse-status",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ],
                            value="active"
                        )
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Warehouse Image"),
                        dcc.Upload(
                            id="warehouse-image",
                            children=dbc.Button("Upload Image", color="light", outline=True),
                            style={"width": "100%"}
                        )
                    ], width=12)
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="warehouse-cancel-btn", className="me-2"),
            dbc.Button("Save Warehouse", id="warehouse-save-btn", color="primary")
        ])
    ], id="warehouse-modal", is_open=False, size="lg")

def create_unit_modal():
    return dbc.Modal([
        dbc.ModalHeader("Add New Unit(s)"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select Warehouse"),
                        dbc.Select(id="unit-warehouse", placeholder="Choose warehouse...")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Checklist(
                            id="bulk-create-check",
                            options=[{"label": "Bulk Create Units", "value": "bulk"}],
                            value=[]
                        )
                    ], width=12)
                ], className="mb-3"),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Unit Name"),
                            dbc.Input(id="unit-name", type="text", placeholder="e.g., Unit 1")
                        ], width=12)
                    ], className="mb-3")
                ], id="single-unit-form"),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Number of Units to Create"),
                            dbc.Input(id="bulk-count", type="number", min=1, placeholder="Enter number of units")
                        ], width=12)
                    ], className="mb-3")
                ], id="bulk-unit-form", style={"display": "none"}),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Status"),
                        dbc.Select(
                            id="unit-status",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ],
                            value="active"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Availability"),
                        dbc.Select(
                            id="unit-availability",
                            options=[
                                {"label": "Not Taken", "value": "not taken"},
                                {"label": "Taken", "value": "taken"},
                                {"label": "Under Maintenance", "value": "under maintenance"},
                                {"label": "Not in Use", "value": "not in use"}
                            ],
                            value="not taken"
                        )
                    ], width=6)
                ], className="mb-3"),
                html.Div(id="capacity-warning", className="alert alert-warning", style={"display": "none"})
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="unit-cancel-btn", className="me-2"),
            dbc.Button("Save Unit(s)", id="unit-save-btn", color="primary")
        ])
    ], id="unit-modal", is_open=False, size="lg")

# Edit modals
def create_edit_warehouse_modal():
    return dbc.Modal([
        dbc.ModalHeader("Edit Warehouse"),
        dbc.ModalBody([
            dbc.Form([
                dcc.Store(id="edit-warehouse-id"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Warehouse Name"),
                        dbc.Input(id="edit-warehouse-name", type="text")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Location"),
                        dbc.Input(id="edit-warehouse-location", type="text")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Capacity"),
                        dbc.Input(id="edit-warehouse-capacity", type="number", min=1)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Status"),
                        dbc.Select(
                            id="edit-warehouse-status",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ]
                        )
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Warehouse Image"),
                        dcc.Upload(
                            id="edit-warehouse-image",
                            children=dbc.Button("Upload New Image", color="light", outline=True),
                            style={"width": "100%"}
                        )
                    ], width=12)
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="edit-warehouse-cancel-btn", className="me-2"),
            dbc.Button("Update Warehouse", id="edit-warehouse-save-btn", color="primary")
        ])
    ], id="edit-warehouse-modal", is_open=False, size="lg")

def create_edit_unit_modal():
    return dbc.Modal([
        dbc.ModalHeader("Edit Unit"),
        dbc.ModalBody([
            dbc.Form([
                dcc.Store(id="edit-unit-id"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Unit Name"),
                        dbc.Input(id="edit-unit-name", type="text")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Warehouse"),
                        dbc.Select(id="edit-unit-warehouse")
                    ], width=12)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Status"),
                        dbc.Select(
                            id="edit-unit-status",
                            options=[
                                {"label": "Active", "value": "active"},
                                {"label": "Inactive", "value": "inactive"}
                            ]
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Availability"),
                        dbc.Select(
                            id="edit-unit-availability",
                            options=[
                                {"label": "Not Taken", "value": "not taken"},
                                {"label": "Taken", "value": "taken"},
                                {"label": "Under Maintenance", "value": "under maintenance"},
                                {"label": "Not in Use", "value": "not in use"}
                            ]
                        )
                    ], width=6)
                ], className="mb-3")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="edit-unit-cancel-btn", className="me-2"),
            dbc.Button("Update Unit", id="edit-unit-save-btn", color="primary")
        ])
    ], id="edit-unit-modal", is_open=False, size="lg")

# Main layout
app.layout = html.Div([
    create_sidebar(),
    html.Div([
        create_header(),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab(label="Warehouses", tab_id="warehouses"),
            dbc.Tab(label="Units", tab_id="units")
        ], id="main-tabs", active_tab="warehouses"),
        
        # Tab content
        html.Div(id="tab-content"),
        
        # Modals
        create_warehouse_modal(),
        create_unit_modal(),
        create_edit_warehouse_modal(),
        create_edit_unit_modal(),
        
        # Notifications
        html.Div(id="notification-container"),
        
        # Interval component for auto-refresh
        dcc.Interval(id="interval-component", interval=5000, n_intervals=0, disabled=True)
        
    ], className="main-content")
])

# Callbacks
@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "warehouses":
        return create_warehouse_table()
    elif active_tab == "units":
        return create_unit_table()
    return html.Div()

@app.callback(
    Output("warehouse-table-container", "children"),
    Input("warehouse-table-refresh", "children")
)
def update_warehouse_table(refresh_trigger):
    warehouses = db.get_warehouses()
    if not warehouses:
        return dbc.Alert("No warehouses found. Create your first warehouse!", color="info")
    
    table_data = []
    for warehouse in warehouses:
        table_data.append({
            "ID": warehouse['id'],
            "Name": warehouse['name'],
            "Location": warehouse['location'],
            "Capacity": warehouse['capacity'],
            "Used Units": warehouse['unit_count'],
            "Status": warehouse['status'],
            "Actions": warehouse['id']
        })
    
    return dash_table.DataTable(
        data=table_data,
        columns=[
            {"name": "ID", "id": "ID"},
            {"name": "Name", "id": "Name"},
            {"name": "Location", "id": "Location"},
            {"name": "Capacity", "id": "Capacity"},
            {"name": "Used Units", "id": "Used Units"},
            {"name": "Status", "id": "Status", "presentation": "markdown"},
            {"name": "Actions", "id": "Actions", "presentation": "markdown"}
        ],
        style_cell={'textAlign': 'left'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{Status} = active'},
                'backgroundColor': '#d4edda',
                'color': '#155724'
            },
            {
                'if': {'filter_query': '{Status} = inactive'},
                'backgroundColor': '#f8d7da',
                'color': '#721c24'
            }
        ],
        page_size=10
    )

@app.callback(
    [Output("unit-table-container", "children"),
     Output("warehouse-filter", "options")],
    [Input("unit-table-refresh", "children"),
     Input("warehouse-filter", "value")]
)
def update_unit_table(refresh_trigger, warehouse_filter):
    warehouses = db.get_warehouses()
    warehouse_options = [{"label": "All Warehouses", "value": ""}]
    warehouse_options.extend([{"label": w['name'], "value": w['id']} for w in warehouses])
    
    units = db.get_units(warehouse_filter if warehouse_filter else None)
    if not units:
        return dbc.Alert("No units found. Create your first unit!", color="info"), warehouse_options
    
    table_data = []
    for unit in units:
        table_data.append({
            "ID": unit['id'],
            "Unit Name": unit['name'],
            "Warehouse": unit['warehouse_name'],
            "Status": unit['status'],
            "Availability": unit['availability'],
            "Actions": unit['id']
        })
    
    table = dash_table.DataTable(
        data=table_data,
        columns=[
            {"name": "ID", "id": "ID"},
            {"name": "Unit Name", "id": "Unit Name"},
            {"name": "Warehouse", "id": "Warehouse"},
            {"name": "Status", "id": "Status"},
            {"name": "Availability", "id": "Availability"},
            {"name": "Actions", "id": "Actions", "presentation": "markdown"}
        ],
        style_cell={'textAlign': 'left'},
        page_size=10
    )
    
    return table, warehouse_options

# Modal callbacks
@app.callback(
    Output("warehouse-modal", "is_open"),
    [Input("add-warehouse-btn", "n_clicks"),
     Input("warehouse-cancel-btn", "n_clicks"),
     Input("warehouse-save-btn", "n_clicks")],
    State("warehouse-modal", "is_open")
)
def toggle_warehouse_modal(add_click, cancel_click, save_click, is_open):
    if add_click or cancel_click or save_click:
        return not is_open
    return is_open

@app.callback(
    [Output("unit-modal", "is_open"),
     Output("unit-warehouse", "options")],
    [Input("add-unit-btn", "n_clicks"),
     Input("unit-cancel-btn", "n_clicks"),
     Input("unit-save-btn", "n_clicks")],
    State("unit-modal", "is_open")
)
def toggle_unit_modal(add_click, cancel_click, save_click, is_open):
    warehouses = db.get_warehouses()
    warehouse_options = [{"label": w['name'], "value": w['id']} for w in warehouses if w['status'] == 'active']
    
    if add_click or cancel_click or save_click:
        return not is_open, warehouse_options
    return is_open, warehouse_options

@app.callback(
    [Output("single-unit-form", "style"),
     Output("bulk-unit-form", "style")],
    Input("bulk-create-check", "value")
)
def toggle_bulk_form(bulk_check):
    if "bulk" in bulk_check:
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}

@app.callback(
    Output("capacity-warning", "children"),
    [Input("unit-warehouse", "value"),
     Input("bulk-count", "value")],
    State("bulk-create-check", "value")
)
def check_capacity_warning(warehouse_id, bulk_count, is_bulk):
    if not warehouse_id:
        return ""
    
    can_create, message = db.check_warehouse_capacity(warehouse_id)
    
    if not can_create:
        return dbc.Alert(message, color="danger")
    
    if "bulk" in is_bulk and bulk_count:
        warehouse = db.get_warehouse_by_id(warehouse_id)
        current_units = len(db.get_units(warehouse_id))
        if current_units + bulk_count > warehouse['capacity']:
            return dbc.Alert(f"Cannot create {bulk_count} units. Only {warehouse['capacity'] - current_units} slots available.", color="warning")
    
    return dbc.Alert(message, color="info")

# Save callbacks
@app.callback(
    [Output("warehouse-table-refresh", "children"),
     Output("notification-container", "children")],
    Input("warehouse-save-btn", "n_clicks"),
    [State("warehouse-name", "value"),
     State("warehouse-location", "value"),
     State("warehouse-capacity", "value"),
     State("warehouse-status", "value"),
     State("warehouse-image", "contents")]
)
def save_warehouse(n_clicks, name, location, capacity, status, image_contents):
    if not n_clicks:
        return "", ""
    
    if not all([name, location, capacity, status]):
        return "", dbc.Alert("Please fill all required fields", color="danger", dismissable=True, className="notification")
    
    # Handle image upload
    image_path = None
    if image_contents:
        try:
            content_type, content_string = image_contents.split(',')
            decoded = base64.b64decode(content_string)
            image_path = f"uploads/{name.replace(' ', '_')}.png"
            os.makedirs("uploads", exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(decoded)
        except Exception as e:
            print(f"Image upload error: {e}")
    
    try:
        db.create_warehouse(name, location, capacity, status, image_path)
        notification = dbc.Alert(f"Warehouse '{name}' created successfully!", color="success", dismissable=True, className="notification")
        return str(datetime.now()), notification
    except Exception as e:
        notification = dbc.Alert(f"Error creating warehouse: {str(e)}", color="danger", dismissable=True, className="notification")
        return "", notification

@app.callback(
    [Output("unit-table-refresh", "children"),
     Output("notification-container", "children", allow_duplicate=True)],
    Input("unit-save-btn", "n_clicks"),
    [State("unit-warehouse", "value"),
     State("unit-name", "value"),
     State("bulk-count", "value"),
     State("unit-status", "value"),
     State("unit-availability", "value"),
     State("bulk-create-check", "value")],
    prevent_initial_call=True
)
def save_unit(n_clicks, warehouse_id, unit_name, bulk_count, status, availability, is_bulk):
    if not n_clicks:
        return "", ""
    
    if not warehouse_id:
        return "", dbc.Alert("Please select a warehouse", color="danger", dismissable=True, className="notification")
    
    # Check warehouse capacity
    can_create, message = db.check_warehouse_capacity(warehouse_id)
    if not can_create:
        return "", dbc.Alert(message, color="danger", dismissable=True, className="notification")
    
    try:
        if "bulk" in is_bulk:
            if not bulk_count or bulk_count <= 0:
                return "", dbc.Alert("Please enter a valid number of units to create", color="danger", dismissable=True, className="notification")
            
            # Check if bulk creation exceeds capacity
            warehouse = db.get_warehouse_by_id(warehouse_id)
            current_units = len(db.get_units(warehouse_id))
            if current_units + bulk_count > warehouse['capacity']:
                return "", dbc.Alert(f"Cannot create {bulk_count} units. Only {warehouse['capacity'] - current_units} slots available.", color="danger", dismissable=True, className="notification")
            
            success_count = db.create_bulk_units(warehouse_id, bulk_count, status, availability)
            if success_count > 0:
                notification = dbc.Alert(f"Successfully created {success_count} units!", color="success", dismissable=True, className="notification")
                return str(datetime.now()), notification
            else:
                return "", dbc.Alert("Failed to create units", color="danger", dismissable=True, className="notification")
        else:
            if not unit_name:
                return "", dbc.Alert("Please enter a unit name", color="danger", dismissable=True, className="notification")
            
            if db.create_unit(warehouse_id, unit_name, status, availability):
                notification = dbc.Alert(f"Unit '{unit_name}' created successfully!", color="success", dismissable=True, className="notification")
                return str(datetime.now()), notification
            else:
                return "", dbc.Alert("Failed to create unit", color="danger", dismissable=True, className="notification")
    except Exception as e:
        notification = dbc.Alert(f"Error creating unit: {str(e)}", color="danger", dismissable=True, className="notification")
        return "", notification

# Edit warehouse callbacks
@app.callback(
    [Output("edit-warehouse-modal", "is_open"),
     Output("edit-warehouse-id", "data"),
     Output("edit-warehouse-name", "value"),
     Output("edit-warehouse-location", "value"),
     Output("edit-warehouse-capacity", "value"),
     Output("edit-warehouse-status", "value")],
    [Input("warehouse-table-container", "active_cell"),
     Input("edit-warehouse-cancel-btn", "n_clicks"),
     Input("edit-warehouse-save-btn", "n_clicks")],
    [State("edit-warehouse-modal", "is_open"),
     State("warehouse-table-container", "data")]
)
def handle_edit_warehouse(active_cell, cancel_click, save_click, is_open, table_data):
    ctx = callback_context
    if not ctx.triggered:
        return False, None, "", "", None, "active"
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "warehouse-table-container" and active_cell:
        # Check if clicked on Actions column (assuming it's the last column)
        if active_cell['column_id'] == 'Actions' and table_data:
            warehouse_id = table_data[active_cell['row']]['ID']
            warehouse = db.get_warehouse_by_id(warehouse_id)
            if warehouse:
                return True, warehouse_id, warehouse['name'], warehouse['location'], warehouse['capacity'], warehouse['status']
    
    if trigger_id in ["edit-warehouse-cancel-btn", "edit-warehouse-save-btn"]:
        return not is_open, None, "", "", None, "active"
    
    return is_open, None, "", "", None, "active"

@app.callback(
    [Output("warehouse-table-refresh", "children", allow_duplicate=True),
     Output("notification-container", "children", allow_duplicate=True)],
    Input("edit-warehouse-save-btn", "n_clicks"),
    [State("edit-warehouse-id", "data"),
     State("edit-warehouse-name", "value"),
     State("edit-warehouse-location", "value"),
     State("edit-warehouse-capacity", "value"),
     State("edit-warehouse-status", "value"),
     State("edit-warehouse-image", "contents")],
    prevent_initial_call=True
)
def update_warehouse(n_clicks, warehouse_id, name, location, capacity, status, image_contents):
    if not n_clicks or not warehouse_id:
        return "", ""
    
    if not all([name, location, capacity, status]):
        return "", dbc.Alert("Please fill all required fields", color="danger", dismissable=True, className="notification")
    
    # Handle image upload
    image_path = None
    if image_contents:
        try:
            content_type, content_string = image_contents.split(',')
            decoded = base64.b64decode(content_string)
            image_path = f"uploads/{name.replace(' ', '_')}.png"
            os.makedirs("uploads", exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(decoded)
        except Exception as e:
            print(f"Image upload error: {e}")
    
    try:
        db.update_warehouse(warehouse_id, name, location, capacity, status, image_path)
        notification = dbc.Alert(f"Warehouse '{name}' updated successfully!", color="success", dismissable=True, className="notification")
        return str(datetime.now()), notification
    except Exception as e:
        notification = dbc.Alert(f"Error updating warehouse: {str(e)}", color="danger", dismissable=True, className="notification")
        return "", notification

# Edit unit callbacks
@app.callback(
    [Output("edit-unit-modal", "is_open"),
     Output("edit-unit-warehouse", "options"),
     Output("edit-unit-id", "data"),
     Output("edit-unit-name", "value"),
     Output("edit-unit-warehouse", "value"),
     Output("edit-unit-status", "value"),
     Output("edit-unit-availability", "value")],
    [Input("unit-table-container", "active_cell"),
     Input("edit-unit-cancel-btn", "n_clicks"),
     Input("edit-unit-save-btn", "n_clicks")],
    [State("edit-unit-modal", "is_open"),
     State("unit-table-container", "data")]
)
def handle_edit_unit(active_cell, cancel_click, save_click, is_open, table_data):
    ctx = callback_context
    warehouses = db.get_warehouses()
    warehouse_options = [{"label": w['name'], "value": w['id']} for w in warehouses if w['status'] == 'active']
    
    if not ctx.triggered:
        return False, warehouse_options, None, "", None, "active", "not taken"
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "unit-table-container" and active_cell:
        # Check if clicked on Actions column
        if active_cell['column_id'] == 'Actions' and table_data:
            unit_id = table_data[active_cell['row']]['ID']
            unit = db.get_unit_by_id(unit_id)
            if unit:
                return True, warehouse_options, unit_id, unit['name'], unit['warehouse_id'], unit['status'], unit['availability']
    
    if trigger_id in ["edit-unit-cancel-btn", "edit-unit-save-btn"]:
        return not is_open, warehouse_options, None, "", None, "active", "not taken"
    
    return is_open, warehouse_options, None, "", None, "active", "not taken"

@app.callback(
    [Output("unit-table-refresh", "children", allow_duplicate=True),
     Output("notification-container", "children", allow_duplicate=True)],
    Input("edit-unit-save-btn", "n_clicks"),
    [State("edit-unit-id", "data"),
     State("edit-unit-name", "value"),
     State("edit-unit-status", "value"),
     State("edit-unit-availability", "value")],
    prevent_initial_call=True
)
def update_unit(n_clicks, unit_id, name, status, availability):
    if not n_clicks or not unit_id:
        return "", ""
    
    if not all([name, status, availability]):
        return "", dbc.Alert("Please fill all required fields", color="danger", dismissable=True, className="notification")
    
    try:
        db.update_unit(unit_id, name, status, availability)
        notification = dbc.Alert(f"Unit '{name}' updated successfully!", color="success", dismissable=True, className="notification")
        return str(datetime.now()), notification
    except Exception as e:
        notification = dbc.Alert(f"Error updating unit: {str(e)}", color="danger", dismissable=True, className="notification")
        return "", notification

# Delete callbacks (you can add confirmation modals for these)
@app.callback(
    [Output("warehouse-table-refresh", "children", allow_duplicate=True),
     Output("notification-container", "children", allow_duplicate=True)],
    Input("warehouse-table-container", "active_cell"),
    [State("warehouse-table-container", "data")],
    prevent_initial_call=True
)
def delete_warehouse(active_cell, table_data):
    if not active_cell or not table_data:
        return "", ""
    
    # You can add a confirmation modal here
    # For now, this is just a placeholder for delete functionality
    return "", ""
