# RecoVer - Lost and Found Application
Note: This file is for technical documentation. To find out how to use our website, please see the User Manual.

## Project Overview
A comprehensive Flask-based lost and found web application that connects users through Google-only authentication. Students can post, search, and manage lost and found items with admin oversight.

**Current Status**: Google OAuth integration implemented, working on admin privileges setup

## Key Technologies
- Flask web framework
- PostgreSQL database  
- Google OAuth authentication (Google-only, no traditional signup)
- Bootstrap CSS with Replit dark theme
- SQLAlchemy ORM

## Architecture
- **Authentication**: Google OAuth only - no traditional user registration
- **Database**: PostgreSQL with User, LostItem, FoundItem, ItemCategory, Notification, Match models
- **Frontend**: Bootstrap-styled templates with responsive design
- **Admin System**: Role-based access with is_admin flag in User model

## Recent Changes
- **2025-07-04**: Cleared all existing lost and found items for fresh start
- **2025-07-04**: Updated contact information preferences to prioritize email for privacy
- **2025-07-04**: Completed "I Found This Item" functionality with notification system
- **2025-07-04**: Added notification counter in navigation and notifications page
- **2025-06-30**: Implemented Google OAuth integration with OAUTHLIB_INSECURE_TRANSPORT for development
- **2025-06-30**: Fixed HTTP/HTTPS redirect issues in OAuth callback
- **2025-06-30**: Updated user session handling to support Google authentication

## User Preferences
- Prefers Google-only authentication for students
- Wants admin dashboard capabilities for managing items and users
- Focuses on clean, functional design over complex features
- Prefers email contact information for privacy over phone numbers
- Wants to start with empty database for fresh launch

## Current Tasks
- Database is now empty and ready for new lost/found items
- Contact information forms now prioritize email for privacy while keeping phone as option

## Google OAuth Configuration
- Redirect URL: https://3ad3fd2d-b22a-4bca-aa0d-1547fb6a0c7b-00-et7pux4h84dz.picard.replit.dev/google_login/callback
- Environment variables: GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET
- Insecure transport enabled for development environment
