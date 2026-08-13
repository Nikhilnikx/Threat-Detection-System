from flask import Blueprint, current_app, jsonify
from flask_login import login_required


monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")


@monitoring_bp.route("/metrics")
@login_required
def metrics():
    stats = current_app.extensions["monitoring_stats"]
    return jsonify({
        "started_at": stats["started_at"].isoformat(),
        "request_count": stats["request_count"],
        "status_codes": stats["status_codes"],
        "log_file": str(stats["log_file"]),
    })
