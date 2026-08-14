"""Creates actionable alerts from high-risk threat events."""

from app import db
from models.alert import Alert


ALERT_RISK_THRESHOLD = 50


def create_alert_for_event(event):
    """
    Create one alert for a high-risk threat event.
    Avoid duplicate alerts.
    """

    if event.risk_score < ALERT_RISK_THRESHOLD:
        return None


    existing_alert = Alert.query.filter_by(
        event_id=event.id
    ).first()


    if existing_alert:
        return existing_alert



    alert = Alert(
        event_id=event.id,
        title=f"{event.event_type} detected",
        description=event.description,
        severity=event.severity,
        risk_score=event.risk_score,
        status="open"
    )


    db.session.add(alert)

    return alert