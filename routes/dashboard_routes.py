from flask import Blueprint, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from models.alert import Alert
from models.event import ThreatEvent
from routes.alert_routes import alert_to_dict
from routes.event_routes import event_to_dict


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return redirect(url_for("dashboard.dashboard" if current_user.is_authenticated else "dashboard.login_page"))


@dashboard_bp.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)


@dashboard_bp.route("/api/dashboard/summary")
@login_required
def dashboard_summary():
    recent_events = ThreatEvent.query.order_by(
        ThreatEvent.created_at.desc()
    ).limit(10).all()
    open_alerts = Alert.query.filter_by(status="open").order_by(
        Alert.created_at.desc()
    ).limit(10).all()

    return jsonify({
        "total_events": ThreatEvent.query.count(),
        "open_alerts": Alert.query.filter_by(status="open").count(),
        "critical_events": ThreatEvent.query.filter_by(severity="critical").count(),
        "risk_breakdown": {
            level: ThreatEvent.query.filter_by(severity=level).count()
            for level in ("low", "medium", "high", "critical")
        },
        "recent_events": [event_to_dict(event) for event in recent_events],
        "recent_open_alerts": [alert_to_dict(alert) for alert in open_alerts],
    })
