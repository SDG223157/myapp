from app import db
from app.models import User

def add_user(username, email):
    try:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def get_user(user_id):
    return User.query.get(user_id)

def get_all_users():
    return User.query.all()

def update_user(user_id, username=None, email=None):
    user = User.query.get(user_id)
    if not user:
        return None
    
    if username:
        user.username = username
    if email:
        user.email = email
    
    try:
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    
    try:
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e
