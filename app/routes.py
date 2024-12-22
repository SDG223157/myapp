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
