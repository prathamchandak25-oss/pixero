from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="pratham@2506",  # Replace with your MySQL password
    database="user_review"
)
cursor = db.cursor(dictionary=True)

# Route to handle review submission
@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.json
    name = data.get('name')
    message = data.get('message')

    if not name or not message:
        return jsonify({"message": "Both name and message are required!"}), 400

    try:
        cursor.execute("INSERT INTO reviews (name, message) VALUES (%s, %s)", (name, message))
        db.commit()
        return jsonify({"message": "Review submitted successfully! Thank you for your review!"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Route to fetch all reviews
@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
    reviews = cursor.fetchall()
    return jsonify({"reviews": reviews})

if __name__ == '__main__':
    app.run(debug=True)
