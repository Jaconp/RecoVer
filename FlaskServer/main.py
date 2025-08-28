import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Import Google OAuth blueprint
from google_oauth import google_auth

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "recover-secret-key")

# Register Google Auth blueprint
app.register_blueprint(google_auth)

# Configure uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sample data for demo
# Categories
categories = [
    {'id': 1, 'name': 'Electronics'},
    {'id': 2, 'name': 'Clothing'},
    {'id': 3, 'name': 'Accessories'},
    {'id': 4, 'name': 'Documents'},
    {'id': 5, 'name': 'Keys'},
    {'id': 6, 'name': 'Wallet/Purse'},
    {'id': 7, 'name': 'Other'}
]

# Users
users = {
    1: {
        'id': 1,
        'username': 'admin',
        'email': 'admin@recover.com',
        'password': 'admin123',  # In a real app, this would be hashed
        'is_admin': True,
        'created_at': datetime(2023, 1, 1)
    },
    2: {
        'id': 2,
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123',
        'is_admin': False,
        'created_at': datetime(2023, 1, 10)
    }
}

# Lost items - starting empty
lost_items = []

# Notifications
notifications = []

# Found items - starting empty
found_items = []

# Helper function to get next ID for items
def get_next_lost_id():
    return max([item['id'] for item in lost_items], default=0) + 1

def get_next_found_id():
    return max([item['id'] for item in found_items], default=0) + 1

# User management functions
def authenticate_user(email, password):
    for user_id, user in users.items():
        if user['email'] == email and user['password'] == password:
            return user
    return None

def get_user_by_id(user_id):
    return users.get(int(user_id))

def create_user(username, email, password):
    user_id = max(users.keys(), default=0) + 1
    users[user_id] = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': password,
        'is_admin': False,
        'created_at': datetime.now()
    }
    return users[user_id]

# Item management functions
def get_category_by_id(category_id):
    for category in categories:
        if category['id'] == int(category_id):
            return category
    return None

def get_lost_item_by_id(item_id):
    for item in lost_items:
        if item['id'] == int(item_id):
            return item
    return None

def get_found_item_by_id(item_id):
    for item in found_items:
        if item['id'] == int(item_id):
            return item
    return None

def get_user_lost_items(user_id):
    return [item for item in lost_items if item['user_id'] == int(user_id)]

def get_user_found_items(user_id):
    return [item for item in found_items if item['user_id'] == int(user_id)]

def search_lost_items(query=None, category_id=None, date_from=None, date_to=None, location=None):
    results = []
    for item in lost_items:
        if item['is_resolved']:
            continue
            
        if query and not (query.lower() in item['title'].lower() or query.lower() in item['description'].lower()):
            continue
            
        if category_id and item['category_id'] != int(category_id):
            continue
            
        if date_from and item['date_lost'] < datetime.strptime(date_from, '%Y-%m-%d').date():
            continue
            
        if date_to and item['date_lost'] > datetime.strptime(date_to, '%Y-%m-%d').date():
            continue
            
        if location and location.lower() not in item['location_lost'].lower():
            continue
            
        results.append(item)
        
    return results

def search_found_items(query=None, category_id=None, date_from=None, date_to=None, location=None):
    results = []
    for item in found_items:
        if item['is_claimed']:
            continue
            
        if query and not (query.lower() in item['title'].lower() or query.lower() in item['description'].lower()):
            continue
            
        if category_id and item['category_id'] != int(category_id):
            continue
            
        if date_from and item['date_found'] < datetime.strptime(date_from, '%Y-%m-%d').date():
            continue
            
        if date_to and item['date_found'] > datetime.strptime(date_to, '%Y-%m-%d').date():
            continue
            
        if location and location.lower() not in item['location_found'].lower():
            continue
            
        results.append(item)
        
    return results

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User session helper
def get_current_user():
    if 'user_id' in session:
        from auth_utils import get_user_by_id
        return get_user_by_id(session['user_id'])
    return None

def get_user_notifications(user_id):
    """Get notifications for a specific user"""
    return [n for n in notifications if n['user_id'] == user_id]

def get_unread_notification_count(user_id):
    """Get count of unread notifications for a user"""
    return len([n for n in notifications if n['user_id'] == user_id and not n['is_read']])

# Context processor for templates
@app.context_processor
def inject_user():
    user = get_current_user()
    notification_count = 0
    if user:
        notification_count = get_unread_notification_count(user['id'])
    return {
        'current_user': user,
        'notification_count': notification_count,
        'now': datetime.now()
    }

# Home page
@app.route('/')
def index():
    # Get recent items that aren't resolved/claimed
    recent_lost = [item for item in lost_items if not item['is_resolved']]
    recent_lost.sort(key=lambda x: x['created_at'], reverse=True)
    recent_lost = recent_lost[:5]  # Get most recent 5
    
    recent_found = [item for item in found_items if not item['is_claimed']]
    recent_found.sort(key=lambda x: x['created_at'], reverse=True)
    recent_found = recent_found[:5]  # Get most recent 5
    
    return render_template('index.html', 
                          title="RecoVer - Lost & Found",
                          recent_lost=recent_lost,
                          recent_found=recent_found)

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        # Validate form data
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
            
        # Check if user already exists
        for _, user in users.items():
            if user['username'] == username:
                flash('Username already exists.', 'danger')
                return redirect(url_for('register'))
                
            if user['email'] == email:
                flash('Email already registered.', 'danger')
                return redirect(url_for('register'))
        
        # Create new user
        user = create_user(username, email, password)
        
        # Log in the new user
        session['user_id'] = user['id']
        flash(f'Welcome, {username}! Your account has been created successfully.', 'success')
        return redirect(url_for('index'))
        
    return render_template('register.html', title="Register - RecoVer")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('login'))
        
        # Authenticate user
        user = authenticate_user(email, password)
        
        if not user:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
        
        # Log in user
        session['user_id'] = user['id']
        flash(f'Welcome back, {user["username"]}!', 'success')
        return redirect(url_for('index'))
        
    return render_template('login.html', title="Login - RecoVer")

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# Browse all items
@app.route('/items')
def browse_items():
    active_lost = [item for item in lost_items if not item['is_resolved']]
    active_found = [item for item in found_items if not item['is_claimed']]
    
    return render_template('browse.html', 
                          title="Browse Items - RecoVer",
                          lost_items=active_lost, 
                          found_items=active_found)

# Report lost item
@app.route('/report/lost', methods=['GET', 'POST'])
def report_lost():
    # Require login
    if 'user_id' not in session:
        flash('Please log in to report a lost item.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        date_lost = request.form.get('date_lost')
        location = request.form.get('location_lost')
        category_id = request.form.get('category')
        color = request.form.get('color')
        brand = request.form.get('brand')
        contact = request.form.get('contact_info')
        reward = request.form.get('reward')
        
        # Validate required fields
        if not title or not description or not date_lost or not location or not category_id or not contact:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('report_lost'))
        
        # Get category name
        category = get_category_by_id(int(category_id))
        category_name = category['name'] if category else 'Unknown'
        
        # Create new lost item
        new_item = {
            'id': get_next_lost_id(),
            'title': title,
            'description': description,
            'date_lost': datetime.strptime(date_lost, '%Y-%m-%d').date(),
            'location_lost': location,
            'image_filename': None,
            'color': color,
            'brand': brand,
            'contact_info': contact,
            'reward': reward,
            'is_resolved': False,
            'created_at': datetime.now(),
            'user_id': session['user_id'],
            'category_id': int(category_id),
            'category_name': category_name
        }
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = f"lost_{new_item['id']}_{file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_item['image_filename'] = filename
        
        # Add to lost items
        lost_items.append(new_item)
        
        flash('Your lost item has been reported successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('report_lost.html', 
                          title="Report Lost Item - RecoVer", 
                          categories=categories)

# Report found item
@app.route('/report/found', methods=['GET', 'POST'])
def report_found():
    # Require login
    if 'user_id' not in session:
        flash('Please log in to report a found item.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        date_found = request.form.get('date_found')
        location = request.form.get('location_found')
        category_id = request.form.get('category')
        color = request.form.get('color')
        brand = request.form.get('brand')
        contact = request.form.get('contact_info')
        
        # Validate required fields
        if not title or not description or not date_found or not location or not category_id or not contact:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('report_found'))
        
        # Get category name
        category = get_category_by_id(int(category_id))
        category_name = category['name'] if category else 'Unknown'
        
        # Create new found item
        new_item = {
            'id': get_next_found_id(),
            'title': title,
            'description': description,
            'date_found': datetime.strptime(date_found, '%Y-%m-%d').date(),
            'location_found': location,
            'image_filename': None,
            'color': color,
            'brand': brand,
            'contact_info': contact,
            'is_claimed': False,
            'created_at': datetime.now(),
            'user_id': session['user_id'],
            'category_id': int(category_id),
            'category_name': category_name
        }
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = f"found_{new_item['id']}_{file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_item['image_filename'] = filename
        
        # Add to found items
        found_items.append(new_item)
        
        flash('Your found item has been reported successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('report_found.html', 
                          title="Report Found Item - RecoVer", 
                          categories=categories)

# View lost item details
@app.route('/item/lost/<int:item_id>')
def view_lost_item(item_id):
    item = get_lost_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('browse_items'))
        
    return render_template('item_detail.html', 
                          title=f"{item['title']} - RecoVer",
                          item=item, 
                          item_type='lost')

# View found item details
@app.route('/item/found/<int:item_id>')
def view_found_item(item_id):
    item = get_found_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('browse_items'))
        
    return render_template('item_detail.html', 
                          title=f"{item['title']} - RecoVer",
                          item=item, 
                          item_type='found')

# Claim found item
@app.route('/claim/<int:item_id>', methods=['POST'])
def claim_item(item_id):
    # Require login
    if 'user_id' not in session:
        flash('Please log in to claim an item.', 'warning')
        return redirect(url_for('login'))
    
    item = get_found_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('browse_items'))
    
    # Mark item as claimed
    item['is_claimed'] = True
    
    flash('You have successfully claimed this item. Please contact the finder to arrange pickup.', 'success')
    return redirect(url_for('view_found_item', item_id=item_id))

# Search items
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = {'lost': [], 'found': []}
    
    if request.method == 'POST':
        # Get search parameters
        query = request.form.get('query', '')
        category_id = request.form.get('category')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        location = request.form.get('location', '')
        item_type = request.form.get('item_type', 'all')
        
        # Convert category_id to int if provided
        category_id = int(category_id) if category_id and category_id.isdigit() else None
        
        # Search based on item type
        if item_type == 'all' or item_type == 'lost':
            results['lost'] = search_lost_items(query, category_id, date_from, date_to, location)
        
        if item_type == 'all' or item_type == 'found':
            results['found'] = search_found_items(query, category_id, date_from, date_to, location)
    
    return render_template('search.html', 
                          title="Search - RecoVer",
                          categories=categories,
                          results=results)

# User profile
@app.route('/profile')
def profile():
    # Require login
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('login'))
    
    user = get_current_user()
    if user:
        # Handle both database and session users
        try:
            user_lost_items = get_user_lost_items(user['id'])
            user_found_items = get_user_found_items(user['id'])
        except:
            # For temporary session users, return empty lists for now
            user_lost_items = []
            user_found_items = []
    else:
        # Handle case where user ID is in session but user not found
        flash('User profile not found.', 'danger')
        session.pop('user_id', None)
        return redirect(url_for('login'))
    
    return render_template('profile.html',
                          title="My Profile - RecoVer",
                          user=user,
                          lost_items=user_lost_items,
                          found_items=user_found_items)

# Mark lost item as resolved
@app.route('/resolve/lost/<int:item_id>', methods=['POST'])
def resolve_lost(item_id):
    # Require login
    if 'user_id' not in session:
        flash('Please log in to resolve an item.', 'warning')
        return redirect(url_for('login'))
    
    item = get_lost_item_by_id(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('profile'))
    
    # Check if user owns this item
    if item['user_id'] != session['user_id']:
        flash('You can only resolve your own items.', 'danger')
        return redirect(url_for('profile'))
    
    # Mark item as resolved
    item['is_resolved'] = True
    
    flash('Your lost item has been marked as resolved.', 'success')
    return redirect(url_for('profile'))

# Demo login - for testing purposes only
@app.route('/demo_login/<int:user_id>')
def demo_login(user_id):
    # Ensure the user ID exists in our test data
    user = get_user_by_id(user_id)
    if user:
        session['user_id'] = user['id']
        flash(f'Welcome, {user["username"]}! You are signed in as a demo user.', 'success')
    else:
        flash('Invalid demo user.', 'danger')
    return redirect(url_for('index'))

@app.route('/promote_to_admin')
def promote_to_admin():
    """Promote current user to admin (one-time setup)"""
    if 'user_id' not in session:
        flash('You must be logged in to access this feature', 'warning')
        return redirect(url_for('index'))
    
    from auth_utils import promote_user_to_admin
    user = get_current_user()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    if user.get('is_admin'):
        flash(f'You are already an admin, {user["username"]}!', 'info')
    else:
        success = promote_user_to_admin(session['user_id'])
        if success:
            flash(f'Successfully promoted {user["username"]} to admin!', 'success')
            # Update session info
            if 'user_info' in session:
                session['user_info']['is_admin'] = True
        else:
            flash('Error promoting user to admin', 'danger')
    
    return redirect(url_for('index'))

@app.route('/found_for_lost/<int:item_id>', methods=['POST'])
def report_found_for_lost(item_id):
    """Handle when someone reports they found a lost item"""
    if 'user_id' not in session:
        flash('You must be logged in to report a found item', 'warning')
        return redirect(url_for('view_lost_item', item_id=item_id))
    
    # Get the lost item
    lost_item = get_lost_item_by_id(item_id)
    if not lost_item:
        flash('Lost item not found', 'danger')
        return redirect(url_for('index'))
    
    if lost_item['is_resolved']:
        flash('This item has already been resolved', 'info')
        return redirect(url_for('view_lost_item', item_id=item_id))
    
    # Get form data
    date_found = request.form.get('date_found')
    location_found = request.form.get('location_found')
    description = request.form.get('description')
    contact_info = request.form.get('contact_info')
    current_location = request.form.get('current_location')
    
    # Validate required fields
    if not date_found or not location_found or not description or not contact_info or not current_location:
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('view_lost_item', item_id=item_id))
    
    # Create a found item report linked to the lost item
    found_report = {
        'id': get_next_found_id(),
        'title': f"Found: {lost_item['title']}",
        'description': f"Found item matching: {lost_item['title']}\n\nDetails: {description}\n\nItem location: {current_location}",
        'date_found': datetime.strptime(date_found, '%Y-%m-%d').date(),
        'location_found': location_found,
        'image_filename': None,
        'color': lost_item.get('color', ''),
        'brand': lost_item.get('brand', ''),
        'contact_info': contact_info,
        'is_claimed': False,
        'created_at': datetime.now(),
        'user_id': session['user_id'],
        'category_id': lost_item['category_id'],
        'category_name': lost_item.get('category_name', 'Unknown'),
        'linked_lost_item_id': item_id  # Link to the original lost item
    }
    
    # Add to found items
    found_items.append(found_report)
    
    # Create a notification for the owner of the lost item
    notification_message = f"Good news! Someone found an item matching your lost '{lost_item['title']}'. Contact: {contact_info}. Location: {current_location}"
    
    # Add notification (simplified for now)
    notifications.append({
        'id': len(notifications) + 1,
        'user_id': lost_item['user_id'],
        'message': notification_message,
        'created_at': datetime.now(),
        'is_read': False,
        'lost_item_id': item_id,
        'found_item_id': found_report['id']
    })
    
    flash(f'Thank you! Your found item report has been sent to the owner of the lost {lost_item["title"]}', 'success')
    return redirect(url_for('view_lost_item', item_id=item_id))

@app.route('/notifications')
def view_notifications():
    """View user notifications"""
    if 'user_id' not in session:
        flash('Please log in to view notifications', 'warning')
        return redirect(url_for('index'))
    
    user = get_current_user()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    user_notifications = get_user_notifications(user['id'])
    user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Mark all notifications as read when viewing
    for notification in user_notifications:
        notification['is_read'] = True
    
    return render_template('notifications.html',
                          title="Notifications - RecoVer",
                          notifications=user_notifications)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
