"""Application request logging and lightweight runtime monitoring."""

import logging
import os
from collections import Counter
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from time import perf_counter

from flask import g, request


def configure_monitoring(app):
    log_directory = os.path.join(app.instance_path, "logs")
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, "application.log")

    if not any(
        isinstance(handler, RotatingFileHandler)
        and handler.baseFilename == log_file
        for handler in app.logger.handlers
    ):
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s"
        ))
        app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)
    app.extensions["monitoring_stats"] = {
        "started_at": datetime.now(timezone.utc),
        "request_count": 0,
        "status_codes": Counter(),
        "log_file": log_file,
    }

    @app.before_request
    def start_request_timer():
        g.request_started_at = perf_counter()

    @app.after_request
    def log_request(response):
        stats = app.extensions["monitoring_stats"]
        stats["request_count"] += 1
        stats["status_codes"][str(response.status_code)] += 1
        duration_ms = (perf_counter() - g.request_started_at) * 1000
        app.logger.info(
            "method=%s path=%s status=%s ip=%s duration_ms=%.2f",
            request.method,
            request.path,
            response.status_code,
            request.remote_addr,
            duration_ms,
        )
        return response
