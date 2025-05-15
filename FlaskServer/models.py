import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    lost_items = db.relationship('LostItem', backref='owner', lazy='dynamic')
    found_items = db.relationship('FoundItem', backref='founder', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ItemCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_lost = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(200))
    contact_info = db.Column(db.String(100))
    reward = db.Column(db.String(100))
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('item_category.id'))
    category = db.relationship('ItemCategory', backref='lost_items')
    color = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<LostItem {self.title}>'


class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_found = db.Column(db.Date, nullable=False)
    location_found = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(200))
    contact_info = db.Column(db.String(100))
    is_claimed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('item_category.id'))
    category = db.relationship('ItemCategory', backref='found_items')
    color = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<FoundItem {self.title}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'))
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'))
    
    lost_item = db.relationship('LostItem', backref='notifications')
    found_item = db.relationship('FoundItem', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    match_score = db.Column(db.Float)  # Score of the match (0-1)
    
    lost_item = db.relationship('LostItem', backref='matches')
    found_item = db.relationship('FoundItem', backref='matches')
    
    def __repr__(self):
        return f'<Match {self.id}: Lost {self.lost_item_id} to Found {self.found_item_id}>'
