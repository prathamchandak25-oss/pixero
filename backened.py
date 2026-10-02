from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import base64
from dotenv import load_dotenv  # Load environment variables
import logging  # Added logging

# Load environment variables
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL Configuration
db_config_creator = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'pratham@2506'),
    'database': 'creator_info'
}

db_config_review = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'pratham@2506'),
    'database': 'user_review'
}

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection(config=None):
    """Create and return a connection to the MySQL database"""
    try:
        # If no config is provided, use the creator_info database config
        if config is None:
            config = db_config_creator
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MySQL: {err}")
        print(f"Error connecting to MySQL: {err}")
        return None

@app.route('/register', methods=['POST'])
def register_creator():
    try:
        data = request.json
        logger.info(f"Received registration data: {data}")
        print(f"Received data: {data}")  # Debug print to see what data is received
        
        conn = get_db_connection(db_config_creator)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor()
        creator_query = """
        INSERT INTO Creators (creator_type, full_name, email, phone, location, experience, 
            equipment, bio, website, instagram, availability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        creator_values = (
            data['creator_type'], data['full_name'], data['email'], data['phone'],
            data['location'], data['experience'], data['equipment'], data['bio'],
            data.get('website', ''), data.get('instagram', ''), data['availability']
        )
        cursor.execute(creator_query, creator_values)
        creator_id = cursor.lastrowid
        
        # Insert services - Fix for the string indices error
        if 'services' in data and isinstance(data['services'], list) and data['services']:
            services_query = """
            INSERT INTO Services (creator_id, service_name, price, unit)
            VALUES (%s, %s, %s, %s)
            """
            services_values = []
            
            for service in data['services']:
                if isinstance(service, dict):
                    service_name = service.get('service_name', '')
                    price = service.get('price', 0)
                    unit = service.get('unit', '')
                    services_values.append((creator_id, service_name, price, unit))
            
            if services_values:
                cursor.executemany(services_query, services_values)
        
        # Insert portfolio links
        if 'portfolio' in data and isinstance(data['portfolio'], list) and data['portfolio']:
            portfolio_query = """
            INSERT INTO Portfolio (creator_id, portfolio_link)
            VALUES (%s, %s)
            """
            portfolio_values = [(creator_id, link) for link in data['portfolio'] if isinstance(link, str)]
            if portfolio_values:
                cursor.executemany(portfolio_query, portfolio_values)
        
        # Insert payment methods
        if 'payment_methods' in data and isinstance(data['payment_methods'], list) and data['payment_methods']:
            payment_query = """
            INSERT INTO PaymentMethods (creator_id, method)
            VALUES (%s, %s)
            """
            payment_values = [(creator_id, method) for method in data['payment_methods'] if isinstance(method, str)]
            if payment_values:
                cursor.executemany(payment_query, payment_values)
         
        conn.commit()
        logger.info(f"Registration successful for creator ID: {creator_id}")
        return jsonify({"success": True, "message": "Registration successful", "creator_id": creator_id}), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        print(f"Registration error: {e}")  # Debug print to see the exact error
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/get_creators', methods=['GET'])
def get_creators():
    creator_type = request.args.get('type', '')
    logger.info(f"Getting creators of type: {creator_type}")
    
    conn = get_db_connection(db_config_creator)
    if not conn:
        return jsonify({"error": "Database connection error"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, location, profile_photo FROM Creators WHERE creator_type = %s", (creator_type,))
    creators = cursor.fetchall()

    # Convert image binary data to Base64
    for creator in creators:
        if creator['profile_photo']:
            creator['profile_photo'] = base64.b64encode(creator['profile_photo']).decode('utf-8')

    cursor.close()
    conn.close()
    return jsonify({"creators": creators})

@app.route('/get_creator_details', methods=['GET'])
def get_creator_details():
    # Support both 'id' and 'creator_id' parameters for backward compatibility
    creator_id = request.args.get('id') or request.args.get('creator_id')
    
    if not creator_id:
        return jsonify({'error': 'No creator ID provided'}), 400
    
    logger.info(f"Getting details for creator ID: {creator_id}")
    
    try:
        # Connect to database using your existing configuration
        conn = get_db_connection(db_config_creator)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get creator details
        cursor.execute("SELECT * FROM Creators WHERE id = %s", (creator_id,))
        creator = cursor.fetchone()
        
        if not creator:
            return jsonify({'error': 'Creator not found'}), 404
        
        # Convert profile photo to base64 if it exists
        if creator['profile_photo']:
            creator['profile_photo'] = base64.b64encode(creator['profile_photo']).decode('utf-8')
        
        # Get services
        cursor.execute("SELECT * FROM Services WHERE creator_id = %s", (creator_id,))
        services = cursor.fetchall()
        
        # Get portfolio links
        cursor.execute("SELECT * FROM Portfolio WHERE creator_id = %s", (creator_id,))
        portfolio = cursor.fetchall()
        
        # Get payment methods
        cursor.execute("SELECT * FROM PaymentMethods WHERE creator_id = %s", (creator_id,))
        payment_methods = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'creator': creator,
            'services': services,
            'portfolio': portfolio,
            'payment_methods': payment_methods
        })
        
    except Exception as e:
        logger.error(f"Error getting creator details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'profile_photo' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['profile_photo']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    creator_id = request.form.get('creator_id')
    if not creator_id:
        return jsonify({"error": "No creator ID provided"}), 400
    
    logger.info(f"Uploading profile photo for creator ID: {creator_id}")
    
    if file and allowed_file(file.filename):
        try:
            # Read the file directly as binary data
            file_data = file.read()
            
            # Connect to the database for creator_info
            conn = get_db_connection(db_config_creator)
            if not conn:
                return jsonify({"error": "Database connection error"}), 500
            
            cursor = conn.cursor()
            
            # Update the database with the binary data
            query = "UPDATE Creators SET profile_photo = %s WHERE id = %s"
            cursor.execute(query, (file_data, creator_id))
            
            conn.commit()
            return jsonify({"success": True, "message": "Profile photo uploaded successfully"}), 200
            
        except Exception as e:
            logger.error(f"Error uploading profile photo: {e}")
            print(f"Error: {e}")
            return jsonify({"error": f"An error occurred: {e}"}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "File type not allowed"}), 400

# Route to add services for a creator separately
@app.route('/add_services', methods=['POST'])
def add_services():
    try:
        data = request.json
        creator_id = data.get('creator_id')
        services = data.get('services')
        
        if not creator_id or not services or not isinstance(services, list):
            return jsonify({"error": "Creator ID and services array are required"}), 400
        
        logger.info(f"Adding services for creator ID: {creator_id}")
        
        conn = get_db_connection(db_config_creator)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor()
        services_query = """
        INSERT INTO Services (creator_id, service_name, price, unit)
        VALUES (%s, %s, %s, %s)
        """
        services_values = []
        
        for service in services:
            if isinstance(service, dict):
                service_name = service.get('service_name', '')
                price = service.get('price', 0)
                unit = service.get('unit', '')
                services_values.append((creator_id, service_name, price, unit))
        
        if services_values:
            cursor.executemany(services_query, services_values)
            conn.commit()
        
        return jsonify({"success": True, "message": "Services added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding services: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Route to add portfolio links for a creator
@app.route('/add_portfolio', methods=['POST'])
def add_portfolio():
    try:
        data = request.json
        creator_id = data.get('creator_id')
        portfolio_links = data.get('portfolio_links')
        
        if not creator_id or not portfolio_links or not isinstance(portfolio_links, list):
            return jsonify({"error": "Creator ID and portfolio links array are required"}), 400
        
        logger.info(f"Adding portfolio links for creator ID: {creator_id}")
        
        conn = get_db_connection(db_config_creator)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor()
        portfolio_query = """
        INSERT INTO Portfolio (creator_id, portfolio_link)
        VALUES (%s, %s)
        """
        portfolio_values = [(creator_id, link) for link in portfolio_links if isinstance(link, str)]
        
        if portfolio_values:
            cursor.executemany(portfolio_query, portfolio_values)
            conn.commit()
        
        return jsonify({"success": True, "message": "Portfolio links added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding portfolio: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Route to add payment methods for a creator
@app.route('/add_payment_methods', methods=['POST'])
def add_payment_methods():
    try:
        data = request.json
        creator_id = data.get('creator_id')
        payment_methods = data.get('payment_methods')
        
        if not creator_id or not payment_methods or not isinstance(payment_methods, list):
            return jsonify({"error": "Creator ID and payment methods array are required"}), 400
        
        logger.info(f"Adding payment methods for creator ID: {creator_id}")
        
        conn = get_db_connection(db_config_creator)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor()
        payment_query = """
        INSERT INTO PaymentMethods (creator_id, method)
        VALUES (%s, %s)
        """
        payment_values = [(creator_id, method) for method in payment_methods if isinstance(method, str)]
        
        if payment_values:
            cursor.executemany(payment_query, payment_values)
            conn.commit()
        
        return jsonify({"success": True, "message": "Payment methods added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding payment methods: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Combined delete_creator function from both files - using the more comprehensive version
@app.route('/api/delete_creator', methods=['POST'])
def delete_creator():
    logger.info(f"Received delete request: {request.method} {request.path}")
    
    try:
        # Log request data for debugging
        logger.info(f"Request JSON: {request.json}")
                
        data = request.get_json()
        if not data:
            logger.error("No JSON data in request")
            return jsonify({"success": False, "message": "Invalid JSON data"}), 400
            
        creator_id = data.get('creator_id')
        
        if not creator_id:
            logger.error("No creator_id in request data")
            return jsonify({"success": False, "message": "Creator ID is required"}), 400
        
        logger.info(f"Processing deletion for creator ID: {creator_id}")
        
        connection = get_db_connection(db_config_creator)
        if not connection:
            return jsonify({"success": False, "message": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        try:
            # Start transaction
            connection.start_transaction()
            
            # First, check if the creator exists
            cursor.execute("SELECT id FROM Creators WHERE id = %s", (creator_id,))
            creator = cursor.fetchone()
            
            if not creator:
                logger.warning(f"Creator {creator_id} not found")
                return jsonify({"success": False, "message": "Creator not found"}), 404
            
            # Delete related services
            cursor.execute("DELETE FROM Services WHERE creator_id = %s", (creator_id,))
            
            # Delete related portfolio items
            cursor.execute("DELETE FROM Portfolio WHERE creator_id = %s", (creator_id,))
            
            # Delete related payment methods
            cursor.execute("DELETE FROM PaymentMethods WHERE creator_id = %s", (creator_id,))
            
            # Finally, delete the creator
            cursor.execute("DELETE FROM Creators WHERE id = %s", (creator_id,))
            
            # Commit the transaction
            connection.commit()
            
            logger.info(f"Creator {creator_id} and all related data deleted successfully")
            return jsonify({"success": True, "message": "Creator and all related data deleted successfully"})
            
        except Error as e:
            # Rollback in case of error
            connection.rollback()
            logger.error(f"Database error during deletion: {e}")
            return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        logger.error(f"Server error during deletion: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# Route to handle review submission
@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    name = data.get('name')
    message = data.get('message')

    if not name or not message:
        return jsonify({"message": "Both name and message are required!"}), 400

    logger.info(f"Submitting review from: {name}")
    
    try:
        # Connect to the database for user_review
        conn = get_db_connection(db_config_review)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (name, message) VALUES (%s, %s)", (name, message))
        conn.commit()
        return jsonify({"message": "Review submitted successfully! Thank you for your review!"})
    except Exception as e:
        logger.error(f"Error submitting review: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Route to fetch all reviews
@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    logger.info("Getting all reviews")
    
    try:
        # Connect to the database for user_review
        conn = get_db_connection(db_config_review)
        if not conn:
            return jsonify({"error": "Database connection error"}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
        reviews = cursor.fetchall()
        return jsonify({"reviews": reviews})
    except Exception as e:
        logger.error(f"Error getting reviews: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Route to search for a creator by email
@app.route('/api/search', methods=['POST']) 
def search():
    data = request.get_json()
    email = data.get('email') if data else None
    
    if not email:
        return jsonify({'error': 'Please provide an email address'}), 400
    
    logger.info(f"Searching for creator with email: {email}")
    
    connection = get_db_connection(db_config_creator)
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get creator info
        cursor.execute("""
            SELECT * FROM Creators 
            WHERE email = %s
        """, (email,))
        
        creator = cursor.fetchone()
        
        if not creator:
            logger.warning(f"No creator found with email: {email}")
            return jsonify({'error': 'No creator found with this email address'}), 404
        
        # Convert binary profile photo to base64 if exists
        if creator.get('profile_photo'):
            creator['profile_photo'] = base64.b64encode(creator['profile_photo']).decode('utf-8')
        
        # Get services
        cursor.execute("""
            SELECT * FROM Services 
            WHERE creator_id = %s
        """, (creator['id'],))
        services = cursor.fetchall()
        
        # Get portfolio links
        cursor.execute("""
            SELECT * FROM Portfolio 
            WHERE creator_id = %s
        """, (creator['id'],))
        portfolio = cursor.fetchall()
        
        # Get payment methods
        cursor.execute("""
            SELECT * FROM PaymentMethods 
            WHERE creator_id = %s
        """, (creator['id'],))
        payment_methods = cursor.fetchall()
        
        # Prepare response
        result = {
            'creator': creator,
            'services': services,
            'portfolio': portfolio,
            'payment_methods': payment_methods
        }
        
        return jsonify(result)
    
    except Error as e:
        logger.error(f"Database error during search: {e}")
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/test', methods=['GET'])
def test():
    """Simple endpoint to test if the API is working"""
    logger.info("Test endpoint called")
    return jsonify({'status': 'API is running'})

# --- Serve static frontend files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve any static file (HTML, CSS, JS, images) from the project root"""
    return send_from_directory(BASE_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)