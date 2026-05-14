from app import db
from datetime import datetime
import json

class InvestorProfile(db.Model):
    __tablename__ = 'investor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Professional info
    company_name = db.Column(db.String(200))
    position = db.Column(db.String(100))
    bio = db.Column(db.Text)
    website = db.Column(db.String(200))
    location = db.Column(db.String(100))
    
    # Investment preferences
    investment_stage = db.Column(db.String(100))
    min_investment = db.Column(db.String(50))
    max_investment = db.Column(db.String(50))
    focus_areas = db.Column(db.Text)  # JSON array
    
    # Verification
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='investor_profile')
    
    def set_focus_areas(self, areas):
        self.focus_areas = json.dumps(areas)
    
    def get_focus_areas(self):
        return json.loads(self.focus_areas) if self.focus_areas else []
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'position': self.position,
            'bio': self.bio,
            'website': self.website,
            'location': self.location,
            'investment_stage': self.investment_stage,
            'min_investment': self.min_investment,
            'max_investment': self.max_investment,
            'focus_areas': self.get_focus_areas(),
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }