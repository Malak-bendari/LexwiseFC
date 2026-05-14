from app import db
from datetime import datetime

class Offer(db.Model):
    __tablename__ = 'offers'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.String(100), nullable=False)
    equity = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    offer_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='offers')
    investor = db.relationship('User', foreign_keys=[investor_id], backref='offers_made')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_title': self.project.title if self.project else '',
            'investor_name': self.investor.username if self.investor else '',
            'amount': self.amount,
            'equity': self.equity,
            'message': self.message,
            'status': self.status,
            'offer_score': self.offer_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }