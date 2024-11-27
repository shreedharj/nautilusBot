import os
import json
from datetime import datetime, timedelta
from utils.logger import logger

LOGS_DIR = "logs/dailyLogs"
REPORTS_DIR = "reports"

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

def loadDailyLogs():
    """Load all log files from the last 7 days."""
    log_data = []
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)

    print(f"[DEBUG] Loading logs from: {LOGS_DIR}")
    for filename in os.listdir(LOGS_DIR):
        print(f"[DEBUG] Checking file: {filename}")
        if filename.endswith(".log"):
            file_date_str = filename.split("_")[-1].replace(".log", "")
            try:
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                print(f"[DEBUG] File date: {file_date}, One week ago: {one_week_ago}")
                if file_date >= one_week_ago:
                    with open(os.path.join(LOGS_DIR, filename), "r") as log_file:
                        file_lines = log_file.readlines()
                        print(f"[DEBUG] Loaded {len(file_lines)} lines from {filename}")
                        log_data.extend(file_lines)
            except ValueError:
                logger.warning(f"Invalid date format in log filename: {filename}")
    
    print(f"[DEBUG] Total log lines loaded: {len(log_data)}")
    return log_data

def parseLogData(log_data):
    """Parse log lines into structured data."""
    summary = {}
    print(f"[DEBUG] Parsing {len(log_data)} log lines")

    for line in log_data:
        # Example format: "2024-11-26 16:00:28,194 - WARNING - WARNING: Pod ..."
        parts = line.strip().split(" - ", 2)  # Split into 3 parts: timestamp, level, message
        if len(parts) < 3:
            print(f"[DEBUG] Skipping malformed line: {line.strip()}")
            continue

        timestamp, log_level, message = parts
        namespace = None
        resource = None
        violation = None

        # Extract namespace
        if "namespace" in message:
            namespace = message.split("namespace '")[1].split("'")[0]
            print(f"[DEBUG] Extracted namespace: {namespace}")

        # Determine resource type
        if "Pod" in message:
            resource = "Pods"
        elif "Job" in message:
            resource = "Jobs"
        elif "Deployment" in message:
            resource = "Deployments"
        print(f"[DEBUG] Determined resource type: {resource}")

        # Extract violations
        if "violation" in message:
            violation = message.split("violation: ")[-1].strip()
            print(f"[DEBUG] Extracted violation: {violation}")

        # Add data to the summary
        if namespace and resource:
            if namespace not in summary:
                summary[namespace] = {"Pods": [], "Jobs": [], "Deployments": []}

            entry = {"timestamp": timestamp, "log_level": log_level, "message": message}
            if violation:
                entry["violation"] = violation

            summary[namespace][resource].append(entry)
            print(f"[DEBUG] Added entry to summary: {entry}")

    print(f"[DEBUG] Parsed summary: {json.dumps(summary, indent=4)}")
    return summary

def beautifySummary(summary):
    """Beautify the summary for the weekly report."""
    lines = ["Weekly Report Summary", "=" * 30]
    print(f"[DEBUG] Beautifying summary with namespaces: {list(summary.keys())}")

    for namespace, resources in summary.items():
        lines.append(f"\nNamespace: {namespace}")
        lines.append("-" * 30)
        for resource_type, resource_data in resources.items():
            lines.append(f"\n{resource_type}:")
            if resource_data:
                for resource in resource_data:
                    lines.append(f"  - {resource['message']}")
            else:
                lines.append("  - No violations")
    
    beautified_content = "\n".join(lines)
    print(f"[DEBUG] Beautified report content:\n{beautified_content}")
    return beautified_content

def saveReport(report_content):
    """Save the weekly report to the reports directory."""
    report_filename = f"weekly_report_{datetime.utcnow().date()}.txt"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    with open(report_path, "w") as report_file:
        report_file.write(report_content)
    
    logger.info(f"Weekly report saved at: {report_path}")
    print(f"[DEBUG] Report saved at: {report_path}")

def generateWeeklyReport():
    """Generate a weekly report based on daily logs."""
    logger.info("Generating weekly report...")
    print("[DEBUG] Starting weekly report generation")
    daily_logs = loadDailyLogs()
    if not daily_logs:
        logger.warning("No logs found for the past week.")
        print("[DEBUG] No logs found for the past week")
        return
    
    summary = parseLogData(daily_logs)
    beautified_report = beautifySummary(summary)
    saveReport(beautified_report)

if __name__ == "__main__":
    generateWeeklyReport()
