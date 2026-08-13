from datetime import datetime, timezone

from app import db


class ThreatEvent(db.Model):
    __tablename__ = "threat_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    risk_score = db.Column(db.Integer, nullable=False, default=0)
    severity = db.Column(db.String(20), nullable=False, default="low")
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", backref="threat_events")
    alert = db.relationship("Alert", back_populates="event", uselist=False)
