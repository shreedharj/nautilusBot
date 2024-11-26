import json
import os
from datetime import datetime, timedelta

LOGS_DIR = "logs"
REPORTS_DIR = os.path.join("reports")
VIOLATIONS_FILE = os.path.join(LOGS_DIR, "violations_by_uid.json")

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

def loadViolations():
    """Load violations from the JSON file."""
    if not os.path.exists(VIOLATIONS_FILE):
        return {}
    with open(VIOLATIONS_FILE, "r") as file:
        return json.load(file)

def generateWeeklyReport():
    """Generate a weekly report summarizing UID violations."""
    violations = loadViolations()
    weeklyReport = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "repeatViolators": [],
        "actions": []
    }

    # Identify repeat violators in the last 7 days
    lastWeek = datetime.utcnow() - timedelta(days=7)
    for uid, data in violations.items():
        recentViolations = [
            v for v in data["violations"] if datetime.fromisoformat(v["timestamp"]) > lastWeek
        ]
        if len(recentViolations) > 3:  # Threshold for repeat violator
            weeklyReport["repeatViolators"].append({
                "uid": uid,
                "namespace": data["namespace"],
                "violationsCount": len(recentViolations),
                "lastViolation": recentViolations[-1]["timestamp"]
            })

            # Determine actions (e.g., flag for removal)
            weeklyReport["actions"].append({
                "uid": uid,
                "namespace": data["namespace"],
                "action": "Flagged for removal"
            })

    # Save weekly report to file
    reportFile = os.path.join(REPORTS_DIR, f"weekly_report_{datetime.utcnow().date()}.json")
    with open(reportFile, "w") as file:
        json.dump(weeklyReport, file, indent=4)

    return weeklyReport
