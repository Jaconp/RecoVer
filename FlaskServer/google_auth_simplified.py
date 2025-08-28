import json
import os
import logging

import requests
from flask import Blueprint, redirect, request, url_for, flash
from oauthlib.oauth2 import WebApplicationClient

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Create blueprint
google_auth = Blueprint("google_auth", __name__)

# Create a logger
logger = logging.getLogger(__name__)

# Set up OAuth client
if GOOGLE_CLIENT_ID:
    client = WebApplicationClient(GOOGLE_CLIENT_ID)
    logger.info("Google OAuth client initialized")
else:
    client = None
    logger.warning("Google OAuth client ID not found in environment variables")

# Display setup instructions
print(f"""
To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add your Replit app URL + "/google_login/callback" to Authorized redirect URIs

For detailed instructions, see:
https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client
""")

@google_auth.route("/google_login")
def login():
    """Begin Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not client:
        flash("Google OAuth is not configured. Please check with the administrator.", "warning")
        return redirect(url_for("login"))
    
    try:
        # Get Google's OAuth 2.0 provider configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Create authorization URL
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            # Ensure HTTPS for external URLs to match whitelisted URIs
            redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {str(e)}")
        flash("An error occurred while connecting to Google. Please try again later.", "danger")
        return redirect(url_for("login"))

@google_auth.route("/google_login/callback")
def callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not client:
        flash("Google OAuth is not configured. Please check with the administrator.", "warning")
        return redirect(url_for("login"))
    
    try:
        # Get authorization code from callback
        code = request.args.get("code")
        if not code:
            flash("Authentication failed. Please try again.", "danger")
            return redirect(url_for("login"))
        
        # Get token endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Prepare and send token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=request.base_url.replace("http://", "https://"),
            code=code
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        )
        
        # Parse token response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        # Verify user info
        userinfo = userinfo_response.json()
        if not userinfo.get("email_verified"):
            flash("Email not verified by Google. Please use another login method.", "danger")
            return redirect(url_for("login"))
            
        # Get user details
        user_email = userinfo["email"]
        user_name = userinfo.get("given_name", user_email.split("@")[0])
        
        # Log successful login
        logger.info(f"User {user_email} successfully authenticated with Google")
        
        # In our simplified app, update the dummy user
        from main import dummy_user
        
        # Update dummy user to be authenticated
        dummy_user.is_authenticated = True
        dummy_user.username = user_name
        
        # Show success message
        flash(f"Welcome, {user_name}! You've successfully signed in with Google.", "success")
        return redirect(url_for("index"))
        
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        flash("An error occurred during Google authentication. Please try again.", "danger")
        return redirect(url_for("login"))