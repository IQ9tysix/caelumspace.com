import logging
from flask import redirect, request
from server import server

# Register Dash apps
import signup               # registers at /signup
import login                # registers at /login
import logout               # registers at /logout
import user_dashboard       # registers at /user_dashboard
import home                 # registers at /home
import activate_account     # registers at /activate_account
import user_complaints      # registers at /user_complaints
import book_now            # registers at /book_unit
import user_payment         # registers at /user_payment
import manage_bookings     # registers at /manage_bookings
import units               # registers at /units
import about_us            # registers at /about_us
import newsroom            # registers at /newsroom
import contact             # registers at /contact
import unit_details        # registers at /unit_details

# Admin modules
from admin import analytics        # registers at /admin/analytics
from admin import units_creation   # registers at /admin/units_creation
from admin import cso             # registers at /admin/cso
from admin import complaints             # registers at /admin/complaints
from admin import payments             # registers at /admin/complaints


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Root redirect to /home
@server.route('/')
def redirectto_home():
    """Redirect root URL to home page."""
    logger.info("Root URL accessed, redirecting to /home")
    return redirect('/home', code=302)

# Optional: Add a quick logout route that immediately redirects
@server.route('/quick-logout')
def quick_logout():
    """Quick logout route that clears session and redirects to login."""
    from flask import session
    
    # Log the logout attempt
    user_email = session.get('email', 'Unknown')
    user_type = session.get('user_type', 'Unknown')
    logger.info(f"Quick logout: {user_type} - {user_email}")
    
    # Clear session
    session.clear()
    
    # Redirect to login with logout message
    return redirect('/login?message=logged_out', code=302)

# Health check endpoint
@server.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy', 'message': 'Warehouse Management System is running'}, 200

# API endpoint to check authentication status
@server.route('/api/auth/status')
def auth_status():
    """API endpoint to check if user is authenticated."""
    from flask import session, jsonify
    
    authenticated = session.get('authenticated', False)
    user_type = session.get('user_type')
    
    if authenticated:
        return jsonify({
            'authenticated': True,
            'user_type': user_type,
            'email': session.get('email')
        })
    else:
        return jsonify({'authenticated': False})

if __name__ == '__main__':
    logger.info("Starting Warehouse Management System server...")
    logger.info("Available routes:")
    logger.info("  / -> /home (redirect)")
    logger.info("  /home -> Home page")
    logger.info("  /login -> Login page") 
    logger.info("  /logout -> Logout page")
    logger.info("  /signup -> Signup page")
    logger.info("  /user_dashboard -> User dashboard")
    logger.info("  /activate_account -> Account activation")
    logger.info("  /user_complaints -> User complaints")
    logger.info("  /book_now -> Book unit")
    logger.info("  /user_payment -> User payment")
    logger.info("  /manage_bookings -> Manage bookings")
    logger.info("  /units -> Units listing")
    logger.info("  /about_us -> About us page")
    logger.info("  /newsroom -> Newsroom")
    logger.info("  /contact -> Contact page")
    logger.info("  /unit_details -> Unit details")
    logger.info("  /admin/analytics -> Admin analytics")
    logger.info("  /admin/complaints -> User complaints")
    logger.info("  /admin/units_creation -> Admin units creation")
    logger.info("  /admin/cso -> Admin CSO management")
    logger.info("  /quick-logout -> Quick logout (server route)")
    logger.info("  /health -> Health check")
    logger.info("  /api/auth/status -> Authentication status API")
    
    server.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))