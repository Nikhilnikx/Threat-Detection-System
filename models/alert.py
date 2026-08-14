from datetime import datetime, timezone

from app import db


class Alert(db.Model):

    __tablename__ = "alerts"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    event_id = db.Column(
        db.Integer,
        db.ForeignKey("threat_events.id"),
        nullable=False,
        unique=True
    )


    title = db.Column(
        db.String(200),
        nullable=False
    )


    description = db.Column(
        db.Text,
        nullable=True
    )


    severity = db.Column(
        db.String(20),
        nullable=False,
        default="Low"
    )


    risk_score = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )


    status = db.Column(
        db.String(20),
        nullable=False,
        default="open"
    )


    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    event = db.relationship(
        "ThreatEvent",
        back_populates="alert"
    )