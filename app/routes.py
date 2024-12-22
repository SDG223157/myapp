from flask import Blueprint, jsonify, request
from app.database import add_user, get_user, get_all_users, update_user, delete_user

main = Blueprint('main', __name__)

@main.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

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
