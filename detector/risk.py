"""Risk scoring and severity classification for threat events."""

EVENT_TYPE_SCORES = {
    "failed_login": 20,
    "brute_force_detected": 85,
}

SEVERITY_SCORES = {
    "low": 10,
    "medium": 35,
    "high": 65,
    "critical": 90,
}


def classify_risk(score):
    """Convert a score from 0 to 100 into a consistent severity label."""
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def apply_risk_score(event):
    """Calculate and attach the event's score and derived severity."""
    event_score = EVENT_TYPE_SCORES.get(event.event_type, 0)
    severity_score = SEVERITY_SCORES.get(event.severity, 0)
    event.risk_score = max(event_score, severity_score)
    event.severity = classify_risk(event.risk_score)
    return event
