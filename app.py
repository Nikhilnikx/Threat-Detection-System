"""
app.py
Application factory for the Threat Detection System.

Phase 1 scope:
- Flask app factory pattern (scales cleanly as blueprints are added in later phases)
- SQLAlchemy + Flask-Login initialized (wired up fully in Phase 2 - Auth)
- Config loaded from environment via config.py
- Health-check route to verify the server boots correctly

Run with:
    flask --app app run --debug
or:
    python app.py
"""

import os
from flask import Flask, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFError, CSRFProtect, generate_csrf

from monitoring import configure_monitoring

from config import config_map
load_dotenv()  # loads variables from a .env file if present

# --- Extensions instantiated here, bound to the app in create_app() ---
# This pattern avoids circular imports when models/ and routes/ need `db` or `login_manager`.
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(env=None):
    app = Flask(__name__, instance_relative_config=True)

    env = env or os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config_map.get(env, config_map["default"]))
    if env == "production" and not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY must be set when FLASK_ENV is production")

    # Ensure instance/ and uploads/ folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Initialize extensions ---
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "dashboard.login_page"
    login_manager.login_message_category = "warning"

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.accept_mimetypes.accept_html:
            return redirect(url_for("dashboard.login_page"))
        return jsonify(error="authentication is required"), 401

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return jsonify(error="CSRF token is missing or invalid"), 400

    configure_monitoring(app)

    @app.after_request
    def add_security_headers(response):
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # --- Register blueprints (uncommented incrementally in later phases) ---
    from routes.auth_routes import auth_bp
    from routes.alert_routes import alerts_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.event_routes import events_bp
    from routes.upload_routes import upload_bp
    # from routes.dashboard_routes import dashboard_bp
    # from routes.upload_routes import upload_bp
    # from routes.report_routes import report_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(upload_bp)
    # app.register_blueprint(dashboard_bp)
    # app.register_blueprint(upload_bp)
    # app.register_blueprint(report_bp)

    # --- Import models so SQLAlchemy is aware of them before create_all() ---
    from models import alert, event, log_entry, user
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return db.session.get(User, int(user_id))

    @app.route("/health")
    def health():
        """Simple readiness probe used for Phase 1 testing."""
        return jsonify(status="ok", service="threat-detection-system", phase=1)

    @app.route("/api/csrf-token")
    def csrf_token():
        return jsonify(csrf_token=generate_csrf())

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # safe no-op until models exist; wired fully in Phase 2/6
    app.run(debug=True)
