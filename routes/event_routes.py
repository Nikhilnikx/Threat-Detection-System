from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from detector.alerts import create_alert_for_event
from models.event import ThreatEvent
from detector.risk import apply_risk_score


events_bp = Blueprint("events", __name__, url_prefix="/events")

VALID_SEVERITIES = {"low", "medium", "high", "critical"}


def event_to_dict(event):
    return {
        "id": event.id,
        "user_id": event.user_id,
        "ip_address": event.ip_address,
        "event_type": event.event_type,
        "description": event.description,
        "risk_score": event.risk_score,
        "severity": event.severity,
        "status": event.status,
        "created_at": event.created_at.isoformat(),
    }


@events_bp.route("", methods=["POST"])
@login_required
def create_event():
    data = request.get_json(silent=True) or {}

    event_type = data.get("event_type")
    description = data.get("description")
    severity = data.get("severity", "low").lower()

    if not event_type:
        return jsonify({"error": "event_type is required"}), 400

    if severity not in VALID_SEVERITIES:
        return jsonify({
            "error": "severity must be low, medium, high, or critical"
        }), 400

    event = ThreatEvent(
        user_id=current_user.id,
        ip_address=request.remote_addr,
        event_type=event_type,
        description=description,
        severity=severity,
    )
    apply_risk_score(event)
    db.session.add(event)
    create_alert_for_event(event)
    db.session.commit()

    return jsonify(event_to_dict(event)), 201


@events_bp.route("", methods=["GET"])
@login_required
def list_events():
    events = ThreatEvent.query.order_by(ThreatEvent.created_at.desc()).all()
    return jsonify([event_to_dict(event) for event in events])


@events_bp.route("/<int:event_id>", methods=["GET"])
@login_required
def get_event(event_id):
    event = db.get_or_404(ThreatEvent, event_id)
    return jsonify(event_to_dict(event))
