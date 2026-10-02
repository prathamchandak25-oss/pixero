from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes and all origins
CORS(app)

# Database configuration - update with your actual credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pratham@2506',  # Update with your actual password
    'database': 'creator_info'
}

@app.route('/api/delete_creator', methods=['POST'])
def delete_creator():
    """Handle creator deletion requests"""
    logger.info(f"Received delete request: {request.method} {request.path}")
    
    try:
        # Log request data for debugging
        logger.info(f"Request JSON: {request.json}")
        
        # Get creator ID from request
        data = request.json
        if not data:
            logger.error("No JSON data in request")
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        creator_id = data.get('creator_id')
        if not creator_id:
            logger.error("No creator_id in request data")
            return jsonify({'success': False, 'message': 'Creator ID is required'}), 400
        
        logger.info(f"Processing deletion for creator ID: {creator_id}")
        
        # Connect to database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Delete creator record
            cursor.execute("DELETE FROM Creators WHERE id = %s", (creator_id,))
            
            # Check if any records were deleted
            rows_affected = cursor.rowcount
            conn.commit()
            
            logger.info(f"Deletion result: {rows_affected} rows affected")
            
            if rows_affected > 0:
                return jsonify({'success': True, 'message': f'Account {creator_id} deleted successfully'})
            else:
                return jsonify({'success': False, 'message': f'Creator {creator_id} not found'}), 404
                
        except mysql.connector.Error as db_err:
            logger.error(f"Database error: {db_err}")
            return jsonify({'success': False, 'message': f'Database error: {str(db_err)}'}), 500
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                
    except Exception as e:
        logger.error(f"Server error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/test', methods=['GET'])
def test():
    """Simple endpoint to test if the API is working"""
    return jsonify({'status': 'API is running'})

if __name__ == '__main__':
    logger.info("Starting Flask application on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)