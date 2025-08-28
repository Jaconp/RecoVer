import json
import os

# Important: Set environment variable for insecure transport
# This is necessary for development environments where we can't use HTTPS
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import requests
from flask import Blueprint, redirect, request, url_for, flash, session
from oauthlib.oauth2 import WebApplicationClient

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the Replit domain for the redirect URL
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "")
REDIRECT_URL = f"https://{REPLIT_DOMAIN}/google_login/callback"

print(f"""
==== GOOGLE OAUTH CONFIGURATION ====
Redirect URL: {REDIRECT_URL}
Make sure to add this URL to your Google OAuth authorized redirect URIs
=============================
""")

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Blueprint for Google authentication
google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/google_login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URL,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@google_auth.route("/google_login/callback")
def callback():
        
    # Get authorization code Google sent back
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    # Make sure we're using HTTPS for the authorization response URL
    authorization_response = request.url
    if authorization_response.startswith('http:'):
        authorization_response = authorization_response.replace('http:', 'https:', 1)
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=authorization_response,
        redirect_url=REDIRECT_URL,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID or "", GOOGLE_CLIENT_SECRET or ""),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Verify the user's email is verified by Google
    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        flash("User email not verified by Google", "danger")
        return redirect("/")

    # Get user info
    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("given_name", "").strip() or email.split("@")[0]
    
    # Create or get user from database using utility function
    from auth_utils import create_or_get_user
    
    user_info = create_or_get_user(email, name, google_id)
    
    # Store user info in session
    session['user_info'] = {
        'id': user_info['id'],
        'username': user_info['username'],
        'email': user_info['email'],
        'google_id': google_id,
        'picture': userinfo.get("picture", ""),
        'is_admin': user_info['is_admin']
    }
    
    # Save a session variable to indicate the user is logged in
    session['user_id'] = user_info['id']
    
    flash(f"Successfully signed in as {name}", "success")
    return redirect("/")

@google_auth.route("/google_login_demo")
def demo_login_page():
    """Demo login page for when OAuth credentials aren't configured"""
    from flask import render_template
    return render_template('google_login.html', title="Sign in with Google - RecoVer")

@google_auth.route("/logout")
def logout():
    # Clear session
    session.clear()
    flash("You have been logged out", "success")
    return redirect("/")