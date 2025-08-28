import os
import uuid
import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, LostItem, FoundItem, ItemCategory, Notification, Match
from forms import LostItemForm, FoundItemForm, SearchForm, AdminItemStatusForm, NewCategoryForm
from utils import find_potential_matches, allowed_file

def register_routes(app):
    
    @app.route('/')
    def index():
        # Debug info
        print(f"Index route accessed. User authenticated: {current_user.is_authenticated}")
        if current_user.is_authenticated:
            print(f"Current user: {current_user.username} (ID: {current_user.id})")
        
        recent_lost = LostItem.query.filter_by(is_resolved=False).order_by(LostItem.created_at.desc()).limit(6).all()
        recent_found = FoundItem.query.filter_by(is_claimed=False).order_by(FoundItem.created_at.desc()).limit(6).all()
        
        # Pass debug info to template
        debug_info = {
            'is_authenticated': current_user.is_authenticated,
            'user_data': current_user.username if current_user.is_authenticated else None
        }
        
        return render_template('index.html', 
                              lost_items=recent_lost, 
                              found_items=recent_found, 
                              title='Home',
                              debug_info=debug_info)

    @app.route('/lost/new', methods=['GET', 'POST'])
    @login_required
    def new_lost_item():
        form = LostItemForm()
        # Populate category choices
        form.category.choices = [(c.id, c.name) for c in ItemCategory.query.order_by(ItemCategory.name).all()]
        
        if form.validate_on_submit():
            filename = None
            if form.image.data:
                if allowed_file(form.image.data.filename):
                    # Generate a unique filename
                    original_filename = secure_filename(form.image.data.filename)
                    extension = original_filename.rsplit('.', 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{extension}"
                    
                    # Save the file
                    form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Invalid file format. Please use jpg, jpeg, or png.', 'danger')
                    return render_template('lost_form.html', form=form, title='Report Lost Item')
            
            # Create new lost item
            lost_item = LostItem(
                title=form.title.data,
                description=form.description.data,
                date_lost=form.date_lost.data,
                location_lost=form.location_lost.data,
                image_filename=filename,
                contact_info=form.contact_info.data,
                reward=form.reward.data,
                user_id=current_user.id,
                category_id=form.category.data,
                color=form.color.data,
                brand=form.brand.data
            )
            
            db.session.add(lost_item)
            db.session.commit()
            
            # Find potential matches
            matches = find_potential_matches(lost_item, 'lost')
            
            if matches:
                # Create notifications for potential matches
                for match in matches:
                    # Notify the founder
                    founder_notification = Notification(
                        message=f"Your found item '{match.found_item.title}' might match a recently reported lost item: '{lost_item.title}'",
                        user_id=match.found_item.user_id,
                        lost_item_id=lost_item.id,
                        found_item_id=match.found_item.id
                    )
                    db.session.add(founder_notification)
                    
                    # Notify the owner
                    owner_notification = Notification(
                        message=f"Your lost item '{lost_item.title}' might match a found item: '{match.found_item.title}'",
                        user_id=current_user.id,
                        lost_item_id=lost_item.id,
                        found_item_id=match.found_item.id
                    )
                    db.session.add(owner_notification)
                
                db.session.commit()
                flash('Item reported as lost and potential matches have been found!', 'success')
            else:
                flash('Item successfully reported as lost. No matches found yet.', 'success')
            
            return redirect(url_for('index'))
        
        return render_template('lost_form.html', form=form, title='Report Lost Item')

    @app.route('/found/new', methods=['GET', 'POST'])
    @login_required
    def new_found_item():
        form = FoundItemForm()
        # Populate category choices
        form.category.choices = [(c.id, c.name) for c in ItemCategory.query.order_by(ItemCategory.name).all()]
        
        if form.validate_on_submit():
            filename = None
            if form.image.data:
                if allowed_file(form.image.data.filename):
                    # Generate a unique filename
                    original_filename = secure_filename(form.image.data.filename)
                    extension = original_filename.rsplit('.', 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{extension}"
                    
                    # Save the file
                    form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Invalid file format. Please use jpg, jpeg, or png.', 'danger')
                    return render_template('found_form.html', form=form, title='Report Found Item')
            
            # Create new found item
            found_item = FoundItem(
                title=form.title.data,
                description=form.description.data,
                date_found=form.date_found.data,
                location_found=form.location_found.data,
                image_filename=filename,
                contact_info=form.contact_info.data,
                user_id=current_user.id,
                category_id=form.category.data,
                color=form.color.data,
                brand=form.brand.data
            )
            
            db.session.add(found_item)
            db.session.commit()
            
            # Find potential matches
            matches = find_potential_matches(found_item, 'found')
            
            if matches:
                # Create notifications for potential matches
                for match in matches:
                    # Notify the owner of the lost item
                    owner_notification = Notification(
                        message=f"Your lost item '{match.lost_item.title}' might match a recently reported found item: '{found_item.title}'",
                        user_id=match.lost_item.user_id,
                        lost_item_id=match.lost_item.id,
                        found_item_id=found_item.id
                    )
                    db.session.add(owner_notification)
                    
                    # Notify the finder
                    finder_notification = Notification(
                        message=f"Your found item '{found_item.title}' might match a lost item: '{match.lost_item.title}'",
                        user_id=current_user.id,
                        lost_item_id=match.lost_item.id,
                        found_item_id=found_item.id
                    )
                    db.session.add(finder_notification)
                
                db.session.commit()
                flash('Item reported as found and potential matches have been notified!', 'success')
            else:
                flash('Item successfully reported as found. No matches found yet.', 'success')
            
            return redirect(url_for('index'))
        
        return render_template('found_form.html', form=form, title='Report Found Item')

    @app.route('/lost/<int:item_id>')
    def lost_item_detail(item_id):
        item = LostItem.query.get_or_404(item_id)
        return render_template('item_detail.html', item=item, item_type='lost', title=item.title)

    @app.route('/found/<int:item_id>')
    def found_item_detail(item_id):
        item = FoundItem.query.get_or_404(item_id)
        return render_template('item_detail.html', item=item, item_type='found', title=item.title)

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        form = SearchForm()
        form.category.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in ItemCategory.query.order_by(ItemCategory.name).all()]
        
        results = {'lost': [], 'found': []}
        
        if request.method == 'POST' and form.validate():
            query = form.query.data
            category_id = form.category.data if form.category.data != 0 else None
            date_from = form.date_from.data
            date_to = form.date_to.data
            location = form.location.data
            item_type = form.item_type.data
            
            # Build base queries
            lost_query = LostItem.query.filter_by(is_resolved=False)
            found_query = FoundItem.query.filter_by(is_claimed=False)
            
            # Apply filters
            if query:
                lost_query = lost_query.filter(
                    (LostItem.title.ilike(f'%{query}%')) | 
                    (LostItem.description.ilike(f'%{query}%')) |
                    (LostItem.color.ilike(f'%{query}%')) |
                    (LostItem.brand.ilike(f'%{query}%'))
                )
                found_query = found_query.filter(
                    (FoundItem.title.ilike(f'%{query}%')) | 
                    (FoundItem.description.ilike(f'%{query}%')) |
                    (FoundItem.color.ilike(f'%{query}%')) |
                    (FoundItem.brand.ilike(f'%{query}%'))
                )
            
            if category_id:
                lost_query = lost_query.filter(LostItem.category_id == category_id)
                found_query = found_query.filter(FoundItem.category_id == category_id)
            
            if date_from:
                lost_query = lost_query.filter(LostItem.date_lost >= date_from)
                found_query = found_query.filter(FoundItem.date_found >= date_from)
            
            if date_to:
                lost_query = lost_query.filter(LostItem.date_lost <= date_to)
                found_query = found_query.filter(FoundItem.date_found <= date_to)
            
            if location:
                lost_query = lost_query.filter(LostItem.location_lost.ilike(f'%{location}%'))
                found_query = found_query.filter(FoundItem.location_found.ilike(f'%{location}%'))
            
            # Get results based on item type
            if item_type == 'all' or item_type == 'lost':
                results['lost'] = lost_query.order_by(LostItem.created_at.desc()).all()
            
            if item_type == 'all' or item_type == 'found':
                results['found'] = found_query.order_by(FoundItem.created_at.desc()).all()
        
        return render_template('search.html', form=form, results=results, title='Search Items')

    @app.route('/notifications')
    @login_required
    def notifications():
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        
        # Mark all as read
        for notification in notifications:
            if not notification.is_read:
                notification.is_read = True
        
        db.session.commit()
        
        return render_template('notifications.html', notifications=notifications, title='Notifications')

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin dashboard.', 'danger')
            return redirect(url_for('index'))
        
        lost_items = LostItem.query.order_by(LostItem.created_at.desc()).all()
        found_items = FoundItem.query.order_by(FoundItem.created_at.desc()).all()
        users = User.query.all()
        categories = ItemCategory.query.all()
        
        category_form = NewCategoryForm()
        
        return render_template(
            'admin.html', 
            lost_items=lost_items, 
            found_items=found_items, 
            users=users, 
            categories=categories,
            category_form=category_form,
            title='Admin Dashboard'
        )

    @app.route('/admin/category/new', methods=['POST'])
    @login_required
    def new_category():
        if not current_user.is_admin:
            abort(403)
        
        form = NewCategoryForm()
        if form.validate_on_submit():
            # Check if category already exists
            existing_category = ItemCategory.query.filter_by(name=form.name.data).first()
            if existing_category:
                flash(f'Category "{form.name.data}" already exists.', 'warning')
            else:
                category = ItemCategory(name=form.name.data)
                db.session.add(category)
                db.session.commit()
                flash(f'Category "{form.name.data}" has been added.', 'success')
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/lost/<int:item_id>/status', methods=['POST'])
    @login_required
    def update_lost_status(item_id):
        if not current_user.is_admin:
            abort(403)
        
        item = LostItem.query.get_or_404(item_id)
        form = AdminItemStatusForm()
        
        if form.validate_on_submit():
            item.is_resolved = form.is_resolved.data
            db.session.commit()
            flash(f'Status for "{item.title}" has been updated.', 'success')
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/found/<int:item_id>/status', methods=['POST'])
    @login_required
    def update_found_status(item_id):
        if not current_user.is_admin:
            abort(403)
        
        item = FoundItem.query.get_or_404(item_id)
        form = AdminItemStatusForm()
        
        if form.validate_on_submit():
            item.is_claimed = form.is_resolved.data
            db.session.commit()
            flash(f'Status for "{item.title}" has been updated.', 'success')
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/make_admin/<int:user_id>', methods=['POST'])
    @login_required
    def make_admin(user_id):
        if not current_user.is_admin:
            abort(403)
        
        user = User.query.get_or_404(user_id)
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = "admin" if user.is_admin else "regular user"
        flash(f'User "{user.username}" is now a {status}.', 'success')
        
        return redirect(url_for('admin_dashboard'))

    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            notification_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            return {'notification_count': notification_count}
        return {'notification_count': 0}
        
    @app.context_processor
    def inject_datetime():
        return {'now': datetime.datetime.now()}

    # Initialize categories if they don't exist
    with app.app_context():
        if ItemCategory.query.count() == 0:
            default_categories = [
                'Electronics', 'Jewelry', 'Clothing', 'Documents', 
                'Keys', 'Wallet/Purse', 'Bag/Backpack', 'Other'
            ]
            for category_name in default_categories:
                category = ItemCategory(name=category_name)
                db.session.add(category)
            db.session.commit()
