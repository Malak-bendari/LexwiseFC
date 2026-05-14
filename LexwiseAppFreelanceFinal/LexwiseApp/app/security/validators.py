import re
from marshmallow import Schema, fields, validate, ValidationError

class ProjectSchema(Schema):
    """Validator for project data"""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200),
        error_messages={'required': 'Title is required'}
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=5000),
        error_messages={'required': 'Description is required'}
    )
    budget = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    category = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100)
    )

class ContractSchema(Schema):
    """Validator for contract data"""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200)
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=50000)
    )

class UserSchema(Schema):
    """Validator for user data"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(
        required=True,
        error_messages={'required': 'Valid email is required'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128)
    )

class LoginSchema(Schema):
    """Validator for login data"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))

def validate_project_data(data):
    """Validate project creation/update data"""
    schema = ProjectSchema()
    try:
        return schema.load(data)
    except ValidationError as e:
        return {'errors': e.messages}

def validate_contract_data(data):
    """Validate contract data"""
    schema = ContractSchema()
    try:
        return schema.load(data)
    except ValidationError as e:
        return {'errors': e.messages}

def validate_registration(data):
    """Validate user registration"""
    schema = UserSchema()
    try:
        return schema.load(data)
    except ValidationError as e:
        return {'errors': e.messages}

def validate_login(data):
    """Validate login data"""
    schema = LoginSchema()
    try:
        return schema.load(data)
    except ValidationError as e:
        return {'errors': e.messages}

def sanitize_string(value, max_length=5000):
    """Sanitize string input"""
    if not value:
        return ''
    
    # Remove control characters
    value = re.sub(r'[\x00-\x1f\x7f]', '', value)
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    if not filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in allowed_extensions

def validate_file_size(file_size, max_size_mb=5):
    """Validate file size (max 5MB default)"""
    max_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_bytes