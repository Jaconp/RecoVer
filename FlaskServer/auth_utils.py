"""
Authentication utilities to avoid circular imports
"""
import os
from flask import session, flash

def create_or_get_user(email, username, google_id):
    """Create or get user from database, handling errors gracefully"""
    try:
        # Import here to avoid circular imports
        from app import app, db
        from models import User
        
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create new user
                user = User()
                user.username = username
                user.email = email
                user.is_admin = False
                db.session.add(user)
                db.session.commit()
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'google_id': google_id
            }
    except Exception as e:
        print(f"Database error in create_or_get_user: {e}")
        # Return session-based user info as fallback
        return {
            'id': f"temp_{google_id}",
            'username': username,
            'email': email,
            'is_admin': False,
            'google_id': google_id,
            'temp_user': True
        }

def get_user_by_id(user_id):
    """Get user by ID, handling both database and session users"""
    try:
        # Handle temporary session users
        if isinstance(user_id, str) and user_id.startswith('temp_'):
            return session.get('user_info')
            
        # Import here to avoid circular imports
        from app import app, db
        from models import User
        
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
    except Exception as e:
        print(f"Database error in get_user_by_id: {e}")
        return session.get('user_info')
    
    return None

def promote_user_to_admin(user_id):
    """Promote user to admin status"""
    try:
        # Handle temporary session users
        if isinstance(user_id, str) and user_id.startswith('temp_'):
            if 'user_info' in session:
                session['user_info']['is_admin'] = True
                return True
            return False
            
        # Import here to avoid circular imports
        from app import app, db
        from models import User
        
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                user.is_admin = True
                db.session.commit()
                return True
    except Exception as e:
        print(f"Database error in promote_user_to_admin: {e}")
        return False
    
    return False