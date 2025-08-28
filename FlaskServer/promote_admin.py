#!/usr/bin/env python3
"""
Direct admin promotion script using Flask app context
"""

from app import app, db
from models import User

def promote_user_to_admin(email):
    """Promote a user to admin by email address"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user found with email: {email}")
            return False
        
        if user.is_admin:
            print(f"User {user.username} ({email}) is already an admin!")
            return True
        
        user.is_admin = True
        db.session.commit()
        print(f"Successfully promoted {user.username} ({email}) to admin!")
        return True

def list_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found")
            return
        
        print("\nAll users:")
        print("-" * 60)
        for user in users:
            status = "ADMIN" if user.is_admin else "USER"
            print(f"ID: {user.id} | {user.username} | {user.email} | {status}")

if __name__ == "__main__":
    print("Admin Management Tool")
    print("=" * 40)
    
    # List current users
    list_users()
    
    # Promote the most recent user (likely you) to admin
    with app.app_context():
        latest_user = User.query.order_by(User.id.desc()).first()
        if latest_user:
            print(f"\nPromoting latest user to admin: {latest_user.email}")
            promote_user_to_admin(latest_user.email)
        else:
            print("No users found to promote")