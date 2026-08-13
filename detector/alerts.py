"""Creates actionable alerts from high-risk threat events."""

from app import db
from models.alert import Alert


ALERT_RISK_THRESHOLD = 50


def create_alert_for_event(event):
    """Create one open alert for a high-risk event, if one does not exist."""
    if event.risk_score < ALERT_RISK_THRESHOLD:
        return None

    db.session.flush()
    existing_alert = Alert.query.filter_by(event_id=event.id).first()
    if existing_alert:
        return existing_alert

    alert = Alert(event_id=event.id)
    db.session.add(alert)
    return alert
