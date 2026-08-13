from datetime import datetime, timezone

from app import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("threat_events.id"),
        unique=True,
        nullable=False,
    )
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    event = db.relationship("ThreatEvent", back_populates="alert")
