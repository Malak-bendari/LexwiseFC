from app import db
from datetime import datetime
import json

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='active')
    originality_score = db.Column(db.Integer, default=0)
    ai_analysis = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    funding_goal = db.Column(db.String(100), nullable=True)
    funding_raised = db.Column(db.String(100), default='$0')
    funding_percentage = db.Column(db.Integer, default=0)
    funding_status = db.Column(db.String(50), default='seeking')  # seeking, funded, completed
        
    def get_ai_analysis(self):
        if self.ai_analysis:
            return json.loads(self.ai_analysis)
        return {}
    
    def set_ai_analysis(self, analysis):
        self.ai_analysis = json.dumps(analysis)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description[:200],
            'budget': self.budget,
            'category': self.category,
            'status': self.status,
            'originality_score': self.originality_score,
            'ai_analysis': self.get_ai_analysis(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    