from flask import Blueprint, jsonify, request, render_template
from app.database import add_user, get_user, get_all_users, update_user, delete_user
from app import db
from sqlalchemy import text
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/db-status')
def db_status():
    try:
        # Use sqlalchemy.text for raw SQL queries
        db.session.execute(text('SELECT 1'))
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