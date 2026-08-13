from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db
from models.alert import Alert


alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

VALID_STATUSES = {"open", "acknowledged", "resolved"}


def alert_to_dict(alert):
    return {
        "id": alert.id,
        "event_id": alert.event_id,
        "event_type": alert.event.event_type,
        "risk_score": alert.event.risk_score,
        "severity": alert.event.severity,
        "status": alert.status,
        "created_at": alert.created_at.isoformat(),
        "acknowledged_at": (
            alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        ),
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
    }


@alerts_bp.route("", methods=["GET"])
@login_required
def list_alerts():
    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return jsonify({"error": "invalid alert status"}), 400

    query = Alert.query.order_by(Alert.created_at.desc())
    if status:
        query = query.filter_by(status=status)

    return jsonify([alert_to_dict(alert) for alert in query.all()])


@alerts_bp.route("/<int:alert_id>", methods=["GET"])
@login_required
def get_alert(alert_id):
    return jsonify(alert_to_dict(db.get_or_404(Alert, alert_id)))


@alerts_bp.route("/<int:alert_id>", methods=["PATCH"])
@login_required
def update_alert_status(alert_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "status must be open, acknowledged, or resolved"
        }), 400

    alert = db.get_or_404(Alert, alert_id)
    alert.status = status
    now = datetime.now(timezone.utc)
    if status == "acknowledged" and not alert.acknowledged_at:
        alert.acknowledged_at = now
    if status == "resolved" and not alert.resolved_at:
        alert.resolved_at = now

    db.session.commit()
    return jsonify(alert_to_dict(alert))
