from datetime import datetime, timedelta

active_alerts = {}
alert_history = []

def trigger_alert(key, message):
    if key not in active_alerts:
        active_alerts[key] = {
            "message": message,
            "started_at": datetime.now().replace(microsecond=0)
        }
        alert_history.append({
            "key": key,
            "message": message,
            "started_at": datetime.now().replace(microsecond=0),
            "resolved_at": None
        })
        return message
    return None

def resolve_alert(key):
    if key in active_alerts:
        started_at = active_alerts[key]["started_at"]
        message = active_alerts[key]["message"]
        active_alerts.pop(key)

        for alert in reversed(alert_history):
            if alert["key"] == key and alert["resolved_at"] is None:
                alert["resolved_at"] = datetime.now().replace(microsecond=0)
                break

        duration = datetime.now() - started_at
        return f"✅ Solved:\n    {message}\n\n⌛ Duration:\n    {duration}"

    return None

def get_active_alerts():
    return active_alerts

def get_last_24h_alerts():
    since = datetime.now() - timedelta(hours=24)
    return [a for a in alert_history if a["started_at"] >= since]
