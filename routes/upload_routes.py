"""
routes/upload_routes.py

Handles:
- Uploading .log/.txt/.csv files
- Parsing security logs
- Storing LogEntry records
- Creating ThreatEvents
- Running suspicious activity detection
"""

import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db

from models.log_entry import LogEntry
from models.event import ThreatEvent

from detector.parser import parse_file
from detector.analyzer import analyze_login_events
from detector.alerts import create_alert_for_event



upload_bp = Blueprint(
    "upload",
    __name__,
    url_prefix="/upload"
)



def _allowed_file(filename):

    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()

    return ext in current_app.config["ALLOWED_EXTENSIONS"]





@upload_bp.route("/", methods=["GET", "POST"])
@login_required
def upload_file():

    if request.method == "POST":

        file = request.files.get("logfile")


        if file is None or file.filename == "":
            flash(
                "Please choose a file to upload.",
                "danger"
            )

            return redirect(
                url_for("upload.upload_file")
            )



        if not _allowed_file(file.filename):

            allowed = ", ".join(
                sorted(
                    current_app.config["ALLOWED_EXTENSIONS"]
                )
            )

            flash(
                f"Unsupported file type. Allowed: {allowed}",
                "danger"
            )

            return redirect(
                url_for("upload.upload_file")
            )



        original_name = secure_filename(
            file.filename
        )


        stored_name = (
            f"{uuid.uuid4().hex}_{original_name}"
        )


        save_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            stored_name
        )


        file.save(save_path)



        with open(save_path, "rb") as f:
            file_bytes = f.read()



        try:

            parsed_entries = parse_file(
                original_name,
                file_bytes
            )


        except Exception as exc:

            current_app.logger.exception(
                "Parsing failed"
            )

            flash(
                f"Could not parse file: {exc}",
                "danger"
            )

            return redirect(
                url_for("upload.upload_file")
            )




        if not parsed_entries:

            flash(
                "No events found in file.",
                "warning"
            )

            return redirect(
                url_for("upload.upload_file")
            )





        # =============================
        # Save LogEntry records
        # =============================

        log_rows = []


        for e in parsed_entries:

            row = LogEntry(

                uploaded_by_id=current_user.id,

                source_file=original_name,

                timestamp=e["timestamp"],

                source_ip=e["source_ip"],

                username=e["username"],

                action=e["action"],

                status=e["status"],

                raw_line=e["raw_line"],

                parsed=e["parsed"]

            )


            log_rows.append(row)



        db.session.add_all(log_rows)

        db.session.commit()






        # =============================
        # Create Threat Events
        # =============================

        threat_events = []


        for row in log_rows:


            threat_event = ThreatEvent(

                user_id=current_user.id,

                ip_address=row.source_ip,

                event_type=(
                    row.action
                    or "unknown"
                ),

                description=row.raw_line,

                risk_score=20,

                severity="low"

            )


            threat_events.append(
                threat_event
            )



        db.session.add_all(threat_events)

        db.session.commit()






        # =============================
        # Run Detection Engine
        # =============================

        detections = analyze_login_events(
            threat_events,
            db
        )



        if detections:


            current_app.logger.warning(
                "Suspicious activity detected: %s",
                detections
            )



            for detection in detections:


                matching_event = next(
                    (
                        event
                        for event in threat_events
                        if event.ip_address == detection["ip"]
                    ),
                    None
                )


                if matching_event:


                    matching_event.risk_score = (
                        detection["risk_score"]
                    )

                    matching_event.severity = (
                        detection["severity"]
                    )



                    create_alert_for_event(
                        matching_event
                    )



            db.session.commit()



        else:

            current_app.logger.info(
                "No suspicious activity detected"
            )





        structured_count = sum(
            1
            for e in parsed_entries
            if e["parsed"]
        )



        flash(
            f"Uploaded '{original_name}': "
            f"{len(parsed_entries)} events stored "
            f"({structured_count} fully parsed, "
            f"{len(parsed_entries)-structured_count} raw-only).",
            "success"
        )



        return redirect(
            url_for(
                "upload.list_events"
            )
        )





    return render_template(
        "upload.html"
    )








@upload_bp.route("/events")
@login_required
def list_events():


    page = request.args.get(
        "page",
        1,
        type=int
    )


    pagination = (
        LogEntry.query
        .order_by(
            LogEntry.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=25,
            error_out=False
        )
    )



    return render_template(
        "events.html",
        pagination=pagination,
        entries=pagination.items
    )