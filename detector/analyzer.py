from collections import defaultdict


def analyze_login_events(events, db):

    created_alerts = []

    failed_attempts = defaultdict(list)


    # collect failed logins
    for event in events:

        event_type = (
            event.event_type or ""
        ).lower()

        description = (
            event.description or ""
        ).lower()


        if (
            "failed" in event_type
            or "failed" in description
            or "failure" in description
        ):

            ip = event.ip_address or "unknown"

            failed_attempts[ip].append(event)



    # detect brute force
    for ip, attempts in failed_attempts.items():

        if len(attempts) >= 3:

            # upgrade event risk
            for event in attempts:

                event.risk_score = 90
                event.severity = "high"



            created_alerts.append(
                {
                    "type": "Brute Force Attack",
                    "ip": ip,
                    "count": len(attempts),
                    "severity": "high",
                    "risk_score": 90,
                    "description":
                    f"{len(attempts)} failed login attempts detected from IP {ip}"
                }
            )


    db.session.commit()


    return created_alerts