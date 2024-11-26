from monitors.podMonitor import monitorPods
from monitors.jobMonitor import monitorJobs
from monitors.deploymentMonitor import monitorDeployments
from utils.scrapeGrafana import scrapeGpuMetrics
from utils.trackViolations import updateUidViolationLog
from utils.logger import logger
import json

def formatResourceOutput(resources, resourceType):
    """Format resource output for better readability."""
    formattedOutput = []
    for resource in resources:
        updateUidViolationLog(resource["uid"], resource["namespace"], resource["name"], resource["violations"])

        formattedResource = {
            "Name": resource["name"],
            "UID": resource["uid"],
            "Age": f"{resource['age']} days",
            "Status": resource.get("status", ""),
            "Requested Resources": resource["requestedResources"],
            "Utilized Resources": resource.get("utilizedResources", {}),
            "Violations": resource["violations"],
        }
        formattedOutput.append(formattedResource)
    logger.info(f"{resourceType}:")
    logger.info(json.dumps(formattedOutput, indent=4))

def main():
    logger.info("Starting Nautilus Bot...")

    # Namespaces to monitor
    namespaces = ["gilpin-lab", "aiea-auditors", "aiea-interns"]

    # Scrape GPU metrics
    gpuMetrics = scrapeGpuMetrics(namespaces)

    # Monitor resources
    podData = monitorPods(namespaces, gpuMetrics)
    jobData = monitorJobs(namespaces)
    deploymentData = monitorDeployments(namespaces)

    # Group output by namespace
    for namespace in namespaces:
        namespacePods = [pod for pod in podData if pod["namespace"] == namespace]
        namespaceJobs = [job for job in jobData if job["namespace"] == namespace]
        namespaceDeployments = [deployment for deployment in deploymentData if deployment["namespace"] == namespace]

        logger.info(f"Namespace: {namespace}")
        formatResourceOutput(namespacePods, "Pods")
        formatResourceOutput(namespaceJobs, "Jobs")
        formatResourceOutput(namespaceDeployments, "Deployments")

    logger.info("Nautilus Bot execution completed.")

if __name__ == "__main__":
    main()
