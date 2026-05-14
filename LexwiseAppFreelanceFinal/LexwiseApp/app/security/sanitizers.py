import re
import bleach
from bleach.sanitizer import Cleaner

# Allowed HTML tags for safe rendering
ALLOWED_TAGS = ['strong', 'em', 'p', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4']

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return ''
    
    # Remove any HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove javascript: URLs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove event handlers (onclick, onload, etc.)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text[:5000]  # Limit length

def sanitize_filename(filename):
    """Sanitize uploaded filename"""
    if not filename:
        return 'file'
    
    # Remove path traversal
    filename = filename.replace('/', '').replace('\\', '')
    filename = filename.replace('..', '')
    
    # Keep only safe characters
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
    
    return filename[:100]

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, ""

def sanitize_project_description(description):
    """Sanitize project description"""
    if not description:
        return ''
    
    # Remove excessive whitespace
    description = re.sub(r'\s+', ' ', description)
    
    # Limit length
    return description[:5000]
# Allowed HTML tags for safe rendering
ALLOWED_TAGS = [
    'b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    '*': ['class', 'id']
}

# Allowed CSS classes
ALLOWED_CSS = [
    'text-teal', 'text-white', 'bg-dark', 'border', 'rounded'
]

def sanitize_html(content):
    """Sanitize HTML content to prevent XSS attacks"""
    if not content:
        return ''
    
    cleaner = Cleaner(
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return cleaner.clean(content)

def sanitize_input(text):
    """Sanitize plain text input"""
    if not text:
        return ''
    
    # Remove any HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove any script tags or javascript: URLs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text

def sanitize_filename(filename):
    """Sanitize filename for safe file upload"""
    if not filename:
        return ''
    
    # Remove path traversal attempts
    filename = filename.replace('/', '').replace('\\', '')
    filename = filename.replace('..', '')
    
    # Keep only alphanumeric, dash, dot, underscore
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
    
    # Prevent empty filename
    if not filename:
        filename = 'file'
    
    return filename

def sanitize_file_content(content, max_size=1024*1024):
    """Sanitize uploaded file content"""
    if not content:
        return ''
    
    # Truncate if too large
    if len(content) > max_size:
        content = content[:max_size] + '...[truncated]'
    
    # Remove null bytes
    content = content.replace('\x00', '')
    
    # For text files, sanitize as text
    try:
        content = content.decode('utf-8')
        content = sanitize_input(content)
    except (UnicodeDecodeError, AttributeError):
        # Binary file - keep as is but we don't display it
        pass
    
    return content

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False
    
    # At least 6 characters
    if len(password) < 6:
        return False
    
    # At least one number (optional but recommended)
    # if not re.search(r'\d', password):
    #     return False
    
    return True