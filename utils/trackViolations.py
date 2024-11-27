import json
import os
from datetime import datetime, timedelta
from logger import logger

LOG_FILE = "logs/violations/violationsByUid.json"

ONE_WEEK_AGO = datetime.utcnow() - timedelta(weeks=1)

def loadViolations():
    """Load existing violations from file."""
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as file:
        return json.load(file)

def saveViolations(data):
    """Save violations to file."""
    with open(LOG_FILE, "w") as file:
        json.dump(data, file, indent=4)

def cleanOldViolations(violations):
    """Remove violations older than a week."""
    return [
        v for v in violations
        if datetime.fromisoformat(v["timestamp"]) >= ONE_WEEK_AGO
    ]

def updateUidViolationLog(uid, namespace, name, violations):
    """Update violations log for a UID."""
    if not violations:
        return

    data = loadViolations()
    if uid not in data:
        data[uid] = {
            "namespace": namespace,
            "name": name,
            "violations": [],
            "weeklyCounts": {},
            "totalCounts": {},
        }

    data[uid]["violations"] = cleanOldViolations(data[uid]["violations"])
    timestamp = datetime.utcnow().isoformat()

    for violation in violations:
        data[uid]["violations"].append({"timestamp": timestamp, "type": violation})

        # Update counts
        data[uid]["weeklyCounts"][violation] = data[uid]["weeklyCounts"].get(violation, 0) + 1
        data[uid]["totalCounts"][violation] = data[uid]["totalCounts"].get(violation, 0) + 1

        # Check for critical thresholds
        if data[uid]["weeklyCounts"][violation] >= 3:
            logger.critical(
                f"CRITICAL ALERT: User '{name}' (UID: {uid}) in namespace '{namespace}' "
                f"has exceeded 3 violations of type '{violation}' this week."
            )

    saveViolations(data)

def resetWeeklyCounts():
    """Reset weekly counts at the end of the week."""
    data = loadViolations()
    for uid in data:
        data[uid]["weeklyCounts"] = {}
    saveViolations(data)
