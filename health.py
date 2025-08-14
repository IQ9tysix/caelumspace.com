import time
import psutil
import mysql.connector
from mysql.connector import Error
from flask import jsonify, request
from datetime import datetime, timedelta
import logging
import os
import socket
import requests
from functools import wraps

# Configure logging for health checks
logging.basicConfig(level=logging.INFO)
health_logger = logging.getLogger('health_check')

# Database configuration (same as your app)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',           
    'database': 'warehouse_db',
    'charset': 'utf8mb4',
    'raise_on_warnings': True
}

class HealthChecker:
    """Comprehensive health check system for the warehouse management app."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.checks = {
            'database': self.check_database,
            'memory': self.check_memory,
            'disk': self.check_disk,
            'cpu': self.check_cpu,
            'network': self.check_network,
            'dependencies': self.check_dependencies
        }
    
    def get_uptime(self):
        """Get application uptime."""
        uptime = datetime.now() - self.start_time
        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0],
            'started_at': self.start_time.isoformat()
        }
    
    def check_database(self):
        """Check database connectivity and basic operations."""
        try:
            start_time = time.time()
            
            # Test connection
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # Test critical tables exist
            critical_tables = ['users', 'cso_officers', 'functions']
            table_status = {}
            
            for table in critical_tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                table_exists = cursor.fetchone() is not None
                table_status[table] = table_exists
            
            # Get database stats
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cso_officers WHERE is_active = 1")
            active_cso_count = cursor.fetchone()[0]
            
            conn.close()
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2),
                'tables': table_status,
                'stats': {
                    'total_users': user_count,
                    'active_cso_officers': active_cso_count
                },
                'connection': 'successful'
            }
            
        except Error as e:
            health_logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed'
            }
        except Exception as e:
            health_logger.error(f"Database health check error: {e}")
            return {
                'status': 'unhealthy',
                'error': f"Unexpected error: {str(e)}",
                'connection': 'failed'
            }
    
    def check_memory(self):
        """Check system memory usage."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Consider unhealthy if memory usage > 90%
            status = 'healthy' if memory.percent < 90 else 'warning' if memory.percent < 95 else 'critical'
            
            return {
                'status': status,
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent,
                'swap_used_percent': swap.percent
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_disk(self):
        """Check disk space usage."""
        try:
            disk = psutil.disk_usage('/')
            
            # Consider unhealthy if disk usage > 85%
            status = 'healthy' if disk.percent < 85 else 'warning' if disk.percent < 95 else 'critical'
            
            return {
                'status': status,
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'used_percent': disk.percent
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_cpu(self):
        """Check CPU usage."""
        try:
            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            
            # Consider unhealthy if CPU usage > 80%
            status = 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
            
            result = {
                'status': status,
                'usage_percent': cpu_percent,
                'cpu_count': cpu_count
            }
            
            if load_avg:
                result['load_average'] = {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                }
            
            return result
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_network(self):
        """Check network connectivity."""
        try:
            # Test internet connectivity
            start_time = time.time()
            response = requests.get('https://www.google.com', timeout=5)
            internet_response_time = time.time() - start_time
            
            # Test local network
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                'status': 'healthy',
                'internet_connectivity': response.status_code == 200,
                'internet_response_time_ms': round(internet_response_time * 1000, 2),
                'hostname': hostname,
                'local_ip': local_ip
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'internet_connectivity': False
            }
    
    def check_dependencies(self):
        """Check critical Python dependencies."""
        try:
            dependencies = {
                'dash': None,
                'mysql-connector-python': None,
                'bcrypt': None,
                'psutil': None,
                'flask': None
            }
            
            # Check if dependencies are importable
            import dash
            dependencies['dash'] = dash.__version__
            
            import mysql.connector
            dependencies['mysql-connector-python'] = mysql.connector.__version__
            
            import bcrypt
            dependencies['bcrypt'] = bcrypt.__version__
            
            import psutil
            dependencies['psutil'] = psutil.__version__
            
            import flask
            dependencies['flask'] = flask.__version__
            
            return {
                'status': 'healthy',
                'versions': dependencies
            }
        except ImportError as e:
            return {
                'status': 'unhealthy',
                'error': f"Missing dependency: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def run_all_checks(self):
        """Run all health checks and return comprehensive status."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'uptime': self.get_uptime(),
            'checks': {}
        }
        
        # Run each check
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
                
                # Update overall status
                if check_result['status'] in ['unhealthy', 'critical']:
                    results['overall_status'] = 'unhealthy'
                elif check_result['status'] == 'warning' and results['overall_status'] == 'healthy':
                    results['overall_status'] = 'warning'
                    
            except Exception as e:
                health_logger.error(f"Health check {check_name} failed: {e}")
                results['checks'][check_name] = {
                    'status': 'unhealthy',
                    'error': f"Check failed: {str(e)}"
                }
                results['overall_status'] = 'unhealthy'
        
        return results

# Initialize global health checker
health_checker = HealthChecker()

def require_auth_for_detailed_health(f):
    """Decorator to require authentication for detailed health info."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        
        # Allow detailed health checks only for authenticated admin users
        if not session.get('authenticated') or session.get('user_type') != 'admin':
            return jsonify({
                'status': 'healthy',
                'message': 'Basic health check - authentication required for detailed info',
                'timestamp': datetime.now().isoformat()
            }), 200
        
        return f(*args, **kwargs)
    return decorated_function

# Health check routes for your server.py
def register_health_routes(server):
    """Register health check routes with your Flask server."""
    
    @server.route('/health')
    def basic_health():
        """Basic health check - always accessible."""
        try:
            # Just check if database is reachable
            conn = mysql.connector.connect(**DB_CONFIG)
            conn.close()
            
            return jsonify({
                'status': 'healthy',
                'message': 'Warehouse Management System is running',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected'
            }), 200
        except:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Database connection failed',
                'timestamp': datetime.now().isoformat(),
                'database': 'disconnected'
            }), 503
    
    @server.route('/health/detailed')
    @require_auth_for_detailed_health
    def detailed_health():
        """Detailed health check - requires admin authentication."""
        results = health_checker.run_all_checks()
        
        status_code = 200
        if results['overall_status'] == 'unhealthy':
            status_code = 503
        elif results['overall_status'] == 'warning':
            status_code = 200  # Still OK, but with warnings
        
        return jsonify(results), status_code
    
    @server.route('/health/database')
    def database_health():
        """Database-specific health check."""
        result = health_checker.check_database()
        status_code = 200 if result['status'] == 'healthy' else 503
        return jsonify(result), status_code
    
    @server.route('/health/system')
    @require_auth_for_detailed_health
    def system_health():
        """System resources health check."""
        results = {
            'memory': health_checker.check_memory(),
            'disk': health_checker.check_disk(),
            'cpu': health_checker.check_cpu()
        }
        return jsonify(results), 200

# # Usage in your main routes file
# if __name__ == '__main__':
#     # Example of how to use this in your application
#     from server import server
    
#     # Register health routes
#     register_health_routes(server)
    
#     print("Health check endpoints registered:")
#     print("  /health - Basic health check")
#     print("  /health/detailed - Comprehensive health check (admin only)")
#     print("  /health/database - Database health check")
#     print("  /health/system - System resources health check (admin only)")
    
#     server.run(debug=True)