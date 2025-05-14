import re

def validate_instagram_username(username: str) -> bool:
    """Validate Instagram username format"""
    # Instagram username rules:
    # - 1-30 characters
    # - Only letters, numbers, periods, and underscores
    # - No consecutive periods
    # - No period at beginning or end
    
    if not username or len(username) > 30:
        return False
    
    if username.startswith('.') or username.endswith('.'):
        return False
    
    if '..' in username:
        return False
    
    pattern = r'^[a-zA-Z0-9._]+$'
    return bool(re.match(pattern, username))