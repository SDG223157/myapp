#!/bin/bash

# Create directories for templates and static files
mkdir -p app/templates app/static/css app/static/js

# Create index.html
cat << 'EOF' > app/templates/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Connection Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .status-card {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .connected {
            background-color: #4CAF50;
        }
        .disconnected {
            background-color: #f44336;
        }
        .loading {
            background-color: #FFA500;
        }
    </style>
</head>
<body>
    <h1>Database Connection Status</h1>
    
    <div class="status-card">
        <h2>MySQL Connection</h2>
        <p>
            <span id="statusIndicator" class="status-indicator loading"></span>
            Status: <span id="connectionStatus">Checking...</span>
        </p>
        <p>Host: <span id="dbHost">-</span></p>
        <p>Database: <span id="dbName">-</span></p>
        <p>Last Checked: <span id="lastChecked">-</span></p>
    </div>

    <div class="status-card">
        <h2>Test Database Operations</h2>
        <button onclick="testDatabaseOperations()">Run Test</button>
        <div id="testResults"></div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/db-status')
                .then(response => response.json())
                .then(data => {
                    const statusIndicator = document.getElementById('statusIndicator');
                    const connectionStatus = document.getElementById('connectionStatus');
                    const dbHost = document.getElementById('dbHost');
                    const dbName = document.getElementById('dbName');
                    const lastChecked = document.getElementById('lastChecked');

                    statusIndicator.className = 'status-indicator ' + 
                        (data.connected ? 'connected' : 'disconnected');
                    connectionStatus.textContent = data.connected ? 'Connected' : 'Disconnected';
                    dbHost.textContent = data.host;
                    dbName.textContent = data.database;
                    lastChecked.textContent = new Date().toLocaleString();

                    if (!data.connected) {
                        connectionStatus.textContent += ` (Error: ${data.error})`;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const statusIndicator = document.getElementById('statusIndicator');
                    const connectionStatus = document.getElementById('connectionStatus');
                    statusIndicator.className = 'status-indicator disconnected';
                    connectionStatus.textContent = 'Error checking connection';
                });
        }

        function testDatabaseOperations() {
            const testResults = document.getElementById('testResults');
            testResults.innerHTML = '<p>Running tests...</p>';

            fetch('/api/test-db')
                .then(response => response.json())
                .then(data => {
                    testResults.innerHTML = `
                        <h3>Test Results:</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                })
                .catch(error => {
                    testResults.innerHTML = `
                        <h3>Test Failed:</h3>
                        <p style="color: red">${error.message}</p>
                    `;
                });
        }

        // Check status immediately and every 30 seconds
        updateStatus();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
EOF

# Update routes.py
cat << 'EOF' > app/routes.py
from flask import Blueprint, jsonify, request, render_template
from app.database import add_user, get_user, get_all_users, update_user, delete_user
from app import db
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/db-status')
def db_status():
    try:
        # Try to execute a simple query to check connection
        db.session.execute('SELECT 1')
        return jsonify({
            'connected': True,
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_DATABASE'),
            'error': None
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_DATABASE'),
            'error': str(e)
        })

@main.route('/api/test-db')
def test_db():
    results = {
        'create_user': None,
        'get_user': None,
        'update_user': None,
        'delete_user': None
    }
    
    try:
        # Test create
        test_user = add_user('testuser', 'test@example.com')
        results['create_user'] = 'Success'
        
        # Test get
        user = get_user(test_user.id)
        results['get_user'] = user.to_dict() if user else 'Failed'
        
        # Test update
        updated_user = update_user(test_user.id, email='updated@example.com')
        results['update_user'] = updated_user.to_dict() if updated_user else 'Failed'
        
        # Test delete
        delete_success = delete_user(test_user.id)
        results['delete_user'] = 'Success' if delete_success else 'Failed'
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'results': results
        })

# Keep existing routes below
@main.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        user = add_user(data['username'], data['email'])
        return jsonify(user.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main.route('/users/<int:user_id>')
def get_user_by_id(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@main.route('/users')
def list_users():
    users = get_all_users()
    return jsonify([user.to_dict() for user in users])

@main.route('/users/<int:user_id>', methods=['PUT'])
def update_user_by_id(user_id):
    data = request.get_json()
    
    try:
        user = update_user(
            user_id,
            username=data.get('username'),
            email=data.get('email')
        )
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    if delete_user(user_id):
        return '', 204
    return jsonify({'error': 'User not found'}), 404
EOF

# Update __init__.py
cat << 'EOF' > app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app
EOF

# Set permissions
chmod -R 755 app/templates
chmod -R 755 app/static

echo "Frontend files have been created successfully!"
echo "The application now includes:"
echo "1. Database connection status dashboard"
echo "2. Real-time status updates"
echo "3. Database operation testing interface"
echo ""
echo "To run the application:"
echo "1. Make sure your virtual environment is activated"
echo "2. Run: python run.py"
echo "3. Visit: http://localhost:8080"