from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class LostItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date_lost = DateField('Date Lost', validators=[DataRequired()])
    location_lost = StringField('Location Lost', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    contact_info = StringField('Contact Information', validators=[DataRequired(), Length(max=100)])
    reward = StringField('Reward (Optional)', validators=[Optional(), Length(max=100)])
    color = StringField('Color (Optional)', validators=[Optional(), Length(max=50)])
    brand = StringField('Brand (Optional)', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Submit')


class FoundItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date_found = DateField('Date Found', validators=[DataRequired()])
    location_found = StringField('Location Found', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Image (Optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    contact_info = StringField('Contact Information', validators=[DataRequired(), Length(max=100)])
    color = StringField('Color (Optional)', validators=[Optional(), Length(max=50)])
    brand = StringField('Brand (Optional)', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    query = StringField('Search Term', validators=[Optional()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    date_from = DateField('Date From', validators=[Optional()])
    date_to = DateField('Date To', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    item_type = SelectField('Item Type', choices=[('all', 'All'), ('lost', 'Lost'), ('found', 'Found')], default='all')
    submit = SubmitField('Search')


class AdminItemStatusForm(FlaskForm):
    is_resolved = BooleanField('Mark as Resolved/Claimed')
    submit = SubmitField('Update Status')


class NewCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Add Category')
