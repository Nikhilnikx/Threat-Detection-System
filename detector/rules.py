"""Rule-based threat detection used by the authentication flow."""

from datetime import datetime, timedelta, timezone

from flask import current_app

from app import db
from detector.alerts import create_alert_for_event
from detector.risk import apply_risk_score
from models.event import ThreatEvent
from models.user import User


def record_failed_login(email, ip_address):
    """Store a failed login and create one alert when the threshold is reached."""
    user = User.query.filter_by(email=email).first()
    failed_event = ThreatEvent(
        user_id=user.id if user else None,
        ip_address=ip_address or "unknown",
        event_type="failed_login",
        description="Login attempt was rejected.",
        severity="low",
    )
    apply_risk_score(failed_event)
    db.session.add(failed_event)
    db.session.flush()

    window_start = datetime.now(timezone.utc) - timedelta(
        minutes=current_app.config["BRUTE_FORCE_WINDOW_MIN"]
    )
    failed_attempts = ThreatEvent.query.filter(
        ThreatEvent.event_type == "failed_login",
        ThreatEvent.ip_address == failed_event.ip_address,
        ThreatEvent.created_at >= window_start,
    ).count()

    if failed_attempts == current_app.config["BRUTE_FORCE_THRESHOLD"]:
        alert_event = ThreatEvent(
            ip_address=failed_event.ip_address,
            event_type="brute_force_detected",
            description=(
                "Brute-force rule triggered: "
                f"{failed_attempts} failed logins within "
                f"{current_app.config['BRUTE_FORCE_WINDOW_MIN']} minutes."
            ),
            severity="high",
        )
        apply_risk_score(alert_event)
        db.session.add(alert_event)
        create_alert_for_event(alert_event)

    db.session.commit()
    return failed_attempts


def is_login_rate_limited(ip_address):
    """Block an IP after too many recorded failures in the configured window."""
    window_start = datetime.now(timezone.utc) - timedelta(
        minutes=current_app.config["BRUTE_FORCE_WINDOW_MIN"]
    )
    attempts = ThreatEvent.query.filter(
        ThreatEvent.event_type == "failed_login",
        ThreatEvent.ip_address == (ip_address or "unknown"),
        ThreatEvent.created_at >= window_start,
    ).count()
    return attempts >= current_app.config["LOGIN_RATE_LIMIT"]
