from datetime import datetime, timezone
from app.database.db import db


class AIProfile(db.Model):
    __tablename__ = "ai_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    financial_goal = db.Column(db.String(255), nullable=True)
    risk_level = db.Column(db.String(50), default="medium")
    spending_behavior = db.Column(db.String(100), default="unknown")
    preferred_coaching_style = db.Column(db.String(100), default="balanced")

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )