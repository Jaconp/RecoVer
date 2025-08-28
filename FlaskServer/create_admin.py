import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime

# Set up Flask app context
from app import app, db
from models import User

def create_admin_user(username, email, password):
    """Create an admin user with the specified credentials."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully with ID: {admin_user.id}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_admin_user(username, email, password)