#!/usr/bin/env python3
"""
Script to promote a user to admin status by email address.
This is useful for Google OAuth users who don't have traditional accounts.
"""

import sys
from app import app, db
from models import User

def make_user_admin(email):
    """Make a user admin by their email address."""
    with app.app_context():
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"No user found with email: {email}")
            print("Note: For Google OAuth users, they need to sign in at least once first.")
            return False
        
        if user.is_admin:
            print(f"User {user.username} ({email}) is already an admin!")
            return True
        
        # Make user admin
        user.is_admin = True
        db.session.commit()
        
        print(f"Successfully promoted {user.username} ({email}) to admin!")
        return True

def list_all_users():
    """List all users in the system."""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the system.")
            return
        
        print("\nAll users in the system:")
        print("-" * 50)
        for user in users:
            admin_status = "ADMIN" if user.is_admin else "USER"
            print(f"ID: {user.id} | {user.username} | {user.email} | {admin_status}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_admin.py <email>           - Make user admin")
        print("  python make_admin.py --list           - List all users")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_all_users()
    else:
        email = sys.argv[1]
        make_user_admin(email)