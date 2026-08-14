from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app import db
from models.alert import Alert


alert_management_bp = Blueprint(
    "alert_management",
    __name__,
    url_prefix="/alerts"
)



@alert_management_bp.route("/<int:alert_id>")
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



@alert_management_bp.route(
    "/<int:alert_id>/update",
    methods=["POST"]
)
@login_required
def update_alert(alert_id):

    alert = db.get_or_404(
        Alert,
        alert_id
    )


    data = request.get_json()


    if "status" in data:
        alert.status = data["status"]


    if "notes" in data:
        alert.notes = data["notes"]


    db.session.commit()


    return jsonify({
        "message":"Alert updated",
        "status":alert.status
    })