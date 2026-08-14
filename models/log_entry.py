"""
models/log_entry.py
Stores normalized events parsed from uploaded .log/.txt/.csv files.

Design notes:
- raw_line is always preserved (audit trail + fallback for unparsed lines).
- parsed flags whether structured fields were extracted.
- Alerts are linked to LogEntry after detection.
"""

from datetime import datetime

from app import db


class LogEntry(db.Model):
    __tablename__ = "log_entries"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Provenance
    uploaded_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    source_file = db.Column(
        db.String(255),
        nullable=False
    )


    # Parsed fields
    timestamp = db.Column(
        db.DateTime,
        nullable=True,
        index=True
    )

    source_ip = db.Column(
        db.String(45),
        nullable=True,
        index=True
    )

    username = db.Column(
        db.String(120),
        nullable=True
    )

    action = db.Column(
        db.String(120),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=True
    )


    # Raw data + parser information
    raw_line = db.Column(
        db.Text,
        nullable=False
    )

    parsed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


    # Detection fields
    severity = db.Column(
        db.String(10),
        nullable=True
    )

    is_flagged = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )


    def __repr__(self):
        return f"<LogEntry {self.id} ip={self.source_ip} action={self.action}>"


    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp else None
            ),
            "source_ip": self.source_ip,
            "username": self.username,
            "action": self.action,
            "status": self.status,
            "parsed": self.parsed,
            "severity": self.severity,
            "is_flagged": self.is_flagged,
            "source_file": self.source_file,
        }