from sqlalchemy import and_, or_
from app import db
from models import LostItem, FoundItem, Match
import re
from datetime import timedelta

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def find_potential_matches(item, item_type):
    """
    Find potential matches between lost and found items.
    
    Args:
        item: Either a LostItem or FoundItem object
        item_type: Either 'lost' or 'found'
    
    Returns:
        A list of Match objects
    """
    matches = []
    
    if item_type == 'lost':
        # This is a newly reported lost item, find matching found items
        found_items = FoundItem.query.filter_by(is_claimed=False).all()
        
        for found_item in found_items:
            score = calculate_match_score(item, found_item)
            if score > 0.3:  # Minimum match threshold
                match = Match(
                    lost_item_id=item.id,
                    found_item_id=found_item.id,
                    match_score=score
                )
                db.session.add(match)
                matches.append(match)
    
    elif item_type == 'found':
        # This is a newly reported found item, find matching lost items
        lost_items = LostItem.query.filter_by(is_resolved=False).all()
        
        for lost_item in lost_items:
            score = calculate_match_score(lost_item, item)
            if score > 0.3:  # Minimum match threshold
                match = Match(
                    lost_item_id=lost_item.id,
                    found_item_id=item.id,
                    match_score=score
                )
                db.session.add(match)
                matches.append(match)
    
    if matches:
        db.session.commit()
    
    return matches

def calculate_match_score(lost_item, found_item):
    """
    Calculate a match score between a lost item and a found item.
    Score is between 0 and 1, with 1 being a perfect match.
    """
    score = 0.0
    total_weight = 0.0
    
    # Category match (high weight)
    category_weight = 0.3
    if lost_item.category_id and found_item.category_id and lost_item.category_id == found_item.category_id:
        score += category_weight
    total_weight += category_weight
    
    # Date proximity (medium weight)
    date_weight = 0.2
    if lost_item.date_lost and found_item.date_found:
        # If found date is after lost date, and within 30 days
        if found_item.date_found >= lost_item.date_lost:
            days_diff = (found_item.date_found - lost_item.date_lost).days
            if days_diff <= 30:
                date_score = 1.0 - (days_diff / 30.0)
                score += date_weight * date_score
            # else date is too far apart
        # else found date is before lost date (unlikely to be a match)
    total_weight += date_weight
    
    # Text similarity in title and description (high weight)
    text_weight = 0.3
    
    # Get keywords from titles and descriptions
    lost_keywords = extract_keywords(lost_item.title + " " + lost_item.description)
    found_keywords = extract_keywords(found_item.title + " " + found_item.description)
    
    # Calculate Jaccard similarity
    if lost_keywords and found_keywords:
        intersection = len(set(lost_keywords).intersection(set(found_keywords)))
        union = len(set(lost_keywords).union(set(found_keywords)))
        
        if union > 0:
            text_score = intersection / union
            score += text_weight * text_score
    
    total_weight += text_weight
    
    # Color match (medium weight)
    color_weight = 0.1
    if lost_item.color and found_item.color:
        lost_colors = extract_keywords(lost_item.color.lower())
        found_colors = extract_keywords(found_item.color.lower())
        
        if lost_colors and found_colors:
            color_intersection = len(set(lost_colors).intersection(set(found_colors)))
            if color_intersection > 0:
                score += color_weight
    total_weight += color_weight
    
    # Brand match (medium weight)
    brand_weight = 0.1
    if lost_item.brand and found_item.brand:
        if lost_item.brand.lower() == found_item.brand.lower():
            score += brand_weight
    total_weight += brand_weight
    
    # Normalize score
    if total_weight > 0:
        normalized_score = score / total_weight
    else:
        normalized_score = 0.0
    
    return normalized_score

def extract_keywords(text):
    """Extract keywords from text by removing common words and punctuation"""
    if not text:
        return []
    
    # Convert to lowercase and split by non-alphanumeric characters
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Common words to filter out
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
        'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 
        'from', 'of', 'that', 'this', 'these', 'those', 'it', 'its', 
        'have', 'has', 'had', 'been', 'be', 'am', 'is', 'are', 'was', 'were',
        'i', 'you', 'he', 'she', 'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their'
    }
    
    # Filter out common words and words with fewer than 3 characters
    keywords = [word for word in words if word not in stop_words and len(word) >= 3]
    
    return keywords
