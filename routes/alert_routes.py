from flask import (
    Blueprint,
    jsonify,
    request,
    render_template
)

from flask_login import login_required

from app import db
from models.alert import Alert


alerts_bp = Blueprint(
    "alerts",
    __name__,
    url_prefix="/alerts"
)


VALID_STATUSES = {
    "open",
    "acknowledged",
    "resolved"
}


def alert_to_dict(alert):

    return {

        "id": alert.id,

        "event_id": alert.event_id,

        "title": alert.title,

        "description": alert.description,

        "severity": alert.severity,

        "risk_score": alert.risk_score,

        "status": alert.status,

        "created_at":
            alert.created_at.isoformat()
            if alert.created_at
            else None
    }



# ==================================
# Alert Investigation Page
# ==================================

@alerts_bp.route("/<int:alert_id>")
@login_required
def alert_detail(alert_id):

    alert = db.get_or_404(
        Alert,
        alert_id
    )

    return render_template(
        "alert_detail.html",
        alert=alert
    )



# ==================================
# API - Update Alert Status
# ==================================

@alerts_bp.route(
    "/api/<int:alert_id>",
    methods=["PATCH"]
)
@login_required
def update_alert_status(alert_id):

    print(
        "PATCH RECEIVED FOR ALERT:",
        alert_id
    )


    data = request.get_json(
        silent=True
    ) or {}


    status = data.get(
        "status"
    )


    print(
        "NEW STATUS:",
        status
    )


    if status not in VALID_STATUSES:

        return jsonify({

            "error":
            "status must be open, acknowledged, or resolved"

        }),400



    alert = db.get_or_404(
        Alert,
        alert_id
    )


    alert.status = status


    db.session.commit()


    return jsonify(
        alert_to_dict(alert)
    )



# ==================================
# API - List Alerts
# ==================================

@alerts_bp.route(
    "/api",
    methods=["GET"]
)
@login_required
def list_alerts():

    alerts = Alert.query.order_by(
        Alert.created_at.desc()
    ).all()


    return jsonify(
        [
            alert_to_dict(alert)
            for alert in alerts
        ]
    )