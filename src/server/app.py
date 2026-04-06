"""
Lock In Backend Server
Main entry point for the Flask application.
"""
from flask import Flask, jsonify
from database.db_manager import init_db

from api.user_routes import user_api 
from api.session_routes import session_api 

app = Flask(__name__)

# Initialize the database when the server starts
init_db()

# Register the blueprints
app.register_blueprint(user_api)
app.register_blueprint(session_api) 

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint to verify the server is running."""
    return jsonify({
        "status": "success",
        "message": "Lock In Server is running and Database is connected!"
    }), 200

if __name__ == '__main__':
    print("[Server] Starting up on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)