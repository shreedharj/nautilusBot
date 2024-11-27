import os
import json
import re
from datetime import datetime, timedelta
from kubernetes import client, config
from utils.logger import logger

LOGS_DIR = "logs/dailyLogs"
VIOLATIONS_FILE = "logs/violations/violationsByUid.json"
WARNING_THRESHOLD = 3
CRITICAL_GPU_THRESHOLD = 2
AGE_THRESHOLD = 14  # days
ALERT_WARNING_AGE = 12  # days

def loadViolations():
    """Load violations from the violations JSON file."""
    if not os.path.exists(VIOLATIONS_FILE):
        return {}
    with open(VIOLATIONS_FILE, "r") as file:
        return json.load(file)

def saveViolations(data):
    """Save updated violations back to the JSON file."""
    with open(VIOLATIONS_FILE, "w") as file:
        json.dump(data, file, indent=4)

def loadLogs():
    """Load all logs from the past week."""
    logs = []
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    for filename in os.listdir(LOGS_DIR):
        if filename.startswith("daily_log_") and filename.endswith(".log"):
            file_date_str = filename.split("_")[2].replace(".log", "")
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
            if file_date >= one_week_ago:
                with open(os.path.join(LOGS_DIR, filename), "r") as log_file:
                    logs.extend(log_file.readlines())
    return logs

def parseLogs(logs):
    """Parse logs to extract violations."""
    resources = {"pods": [], "jobs": [], "deployments": []}
    for line in logs:
        if "WARNING: Pod" in line or "CRITICAL: Pod" in line:
            resources["pods"].append(line)
        elif "WARNING: Job" in line or "CRITICAL: Job" in line:
            resources["jobs"].append(line)
        elif "WARNING: Deployment" in line or "CRITICAL: Deployment" in line:
            resources["deployments"].append(line)
    return resources

def deletePod(namespace, pod_name):
    """Delete a pod."""
    config.load_kube_config()
    v1 = client.CoreV1Api()
    try:
        logger.info(f"Deleting pod '{pod_name}' in namespace '{namespace}'...")
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        logger.info(f"Pod '{pod_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete pod '{pod_name}': {e}")

def deleteJob(namespace, job_name):
    """Delete a job."""
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    try:
        logger.info(f"Deleting job '{job_name}' in namespace '{namespace}'...")
        batch_v1.delete_namespaced_job(name=job_name, namespace=namespace)
        logger.info(f"Job '{job_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete job '{job_name}': {e}")

def deleteDeployment(namespace, deployment_name):
    """Delete a deployment."""
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    try:
        logger.info(f"Deleting deployment '{deployment_name}' in namespace '{namespace}'...")
        apps_v1.delete_namespaced_deployment(name=deployment_name, namespace=namespace)
        logger.info(f"Deployment '{deployment_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete deployment '{deployment_name}': {e}")

def scaleDownDeployment(namespace, deployment_name):
    """Scale down a deployment to zero replicas."""
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    try:
        logger.info(f"Scaling down deployment '{deployment_name}' in namespace '{namespace}'...")
        patch_body = {"spec": {"replicas": 0}}
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch_body)
        logger.info(f"Deployment '{deployment_name}' scaled down successfully.")
    except Exception as e:
        logger.error(f"Failed to scale down deployment '{deployment_name}': {e}")

def processViolations(violations, parsed_logs):
    """Process violations and take action."""
    for pod in parsed_logs["pods"]:
        namespace = extractNamespace(pod)
        pod_name = extractResourceName(pod)
        if isCriticalViolation(pod):
            deletePod(namespace, pod_name)
        else:
            logger.warning(f"Pod '{pod_name}' in namespace '{namespace}' will not be deleted but needs attention.")

    for job in parsed_logs["jobs"]:
        namespace = extractNamespace(job)
        job_name = extractResourceName(job)
        if isCriticalViolation(job):
            deleteJob(namespace, job_name)
        else:
            logger.warning(f"Job '{job_name}' in namespace '{namespace}' will not be deleted but needs attention.")

    for deployment in parsed_logs["deployments"]:
        namespace = extractNamespace(deployment)
        deployment_name = extractResourceName(deployment)
        if isCriticalViolation(deployment):
            deleteDeployment(namespace, deployment_name)
        elif isApproachingThreshold(deployment):
            scaleDownDeployment(namespace, deployment_name)

def isCriticalViolation(resource_line):
    """Determine if a resource has a critical violation."""
    return "GPU underutilized" in resource_line or "exceeds threshold" in resource_line

def isApproachingThreshold(resource_line):
    """Determine if a resource is approaching critical age threshold."""
    return f"Age: {ALERT_WARNING_AGE}" in resource_line

def extractNamespace(log_line):
    """Extract namespace from log line."""
    match = re.search(r"namespace '([\w\-]+)'", log_line)
    return match.group(1) if match else None

def extractResourceName(log_line):
    """Extract resource name from log line."""
    match = re.search(r"Pod '([\w\-]+)'|Job '([\w\-]+)'|Deployment '([\w\-]+)'", log_line)
    for group in match.groups():
        if group:
            return group
    return None

def main():
    logger.info("Starting resource cleanup...")
    logs = loadLogs()
    parsed_logs = parseLogs(logs)
    violations = loadViolations()
    processViolations(violations, parsed_logs)
    logger.info("Resource cleanup completed.")

if __name__ == "__main__":
    main()
