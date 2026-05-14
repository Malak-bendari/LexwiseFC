from app import db
from datetime import datetime
import json

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)
    fairness_score = db.Column(db.Integer, default=0)
    dangerous_clauses = db.Column(db.Text, nullable=True)
    negotiation_script = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_dangerous_clauses(self):
        if self.dangerous_clauses:
            return json.loads(self.dangerous_clauses)
        return []
    
    def set_dangerous_clauses(self, clauses):
        self.dangerous_clauses = json.dumps(clauses)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'fairness_score': self.fairness_score,
            'dangerous_clauses': self.get_dangerous_clauses(),
            'negotiation_script': self.negotiation_script,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }