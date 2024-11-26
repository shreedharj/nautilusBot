import json
import os
from datetime import datetime
from utils.logger import logger

LOG_FILE = "logs/violations/violationsByUid.json"

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

def updateUidViolationLog(uid, namespace, name, violations):
    # logger.info(f"Tracking violations for UID '{uid}' in namespace '{namespace}', name '{name}'...")
    """Update violations log for a UID."""
    if not violations:
        return

    data = loadViolations()
    if uid not in data:
        data[uid] = {"namespace": namespace, "name": name, "violations": []}

    timestamp = datetime.utcnow().isoformat()
    for violation in violations:
        data[uid]["violations"].append({"timestamp": timestamp, "type": violation})

    saveViolations(data)