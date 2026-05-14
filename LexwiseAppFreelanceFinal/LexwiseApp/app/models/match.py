from app import db
from datetime import datetime

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Add this!
    investor_name = db.Column(db.String(200), nullable=False)
    match_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # freelancer who owns project
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='matches')
    investor = db.relationship('User', foreign_keys=[investor_id], backref='investor_matches')
    freelancer = db.relationship('User', foreign_keys=[user_id], backref='freelancer_matches')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_title': self.project.title if self.project else '',
            'investor_id': self.investor_id,
            'investor_name': self.investor_name,
            'match_score': self.match_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }