"""
config.py
Centralized configuration for the Threat Detection System.
Loads sensitive values from environment variables (.env) — never hardcode secrets.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-production")

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'threat_detection.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Uploads ---
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"log", "txt", "csv"}
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB max upload size

    # --- Session / Auth ---
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "threat_detection_session"

    # --- Rule Engine thresholds (tunable without touching detector code) ---
    BRUTE_FORCE_THRESHOLD = 5       # failed logins before flagging
    BRUTE_FORCE_WINDOW_MIN = 10     # minutes window for brute-force check
    DDOS_REQUEST_THRESHOLD = 100    # requests from single IP
    DDOS_WINDOW_SEC = 60            # seconds window for DDoS check
    LOGIN_RATE_LIMIT = 10            # failed logins per IP before blocking


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # requires HTTPS


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
