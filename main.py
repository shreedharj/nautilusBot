from monitors.podMonitor import monitorPods
from monitors.jobMonitor import monitorJobs
from monitors.deploymentMonitor import monitorDeployments
from utils.scrapeGrafana import scrapeGpuMetrics
from utils.trackViolations import updateUidViolationLog
from utils.logger import logger

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
    output = {}
    for namespace in namespaces:
        output[namespace] = {
            "pods": [pod for pod in podData if pod["namespace"] == namespace],
            "jobs": [job for job in jobData if job["namespace"] == namespace],
            "deployments": [deployment for deployment in deploymentData if deployment["namespace"] == namespace]
        }

    # Add violations to violations json and the daily log
    for namespace, data in output.items():
        for pod in data["pods"]:
            updateUidViolationLog(pod["uid"], pod["namespace"], pod["name"], pod["violations"])
            for violation in pod["violations"]:
                if "requesting more than 2 GPUs" in violation:
                    logger.critical(f"Pod '{pod['name']}' in namespace '{pod['namespace']}' violation: {violation}")
                else:
                    logger.warning(f"Pod '{pod['name']}' in namespace '{pod['namespace']}' violation: {violation}")

        for job in data["jobs"]:
            updateUidViolationLog(job["uid"], job["namespace"], job["name"], job["violations"])
            for violation in job["violations"]:
                if "approaching 2 weeks" in violation:
                    logger.critical( f"Job '{job['name']}' in namespace '{job['namespace']}' violation: {violation}")
                else:
                    logger.warning(f"Job '{job['name']}' in namespace '{job['namespace']}' violation: {violation}")

        for deployment in data["deployments"]:
            updateUidViolationLog(deployment["uid"], deployment["namespace"], deployment["name"], deployment["violations"])
            for violation in deployment["violations"]:
                if "approaching 2 weeks" in violation:
                    logger.critical(f"Deployment '{deployment['name']}' in namespace '{deployment['namespace']}' violation: {violation}")
                else:
                    logger.warning(f"Deployment '{deployment['name']}' in namespace '{deployment['namespace']}' violation: {violation}")

    # Log final structured output
    for namespace, data in output.items():
        logger.info(f"Namespace: {namespace}")
        logger.info(f"Pods: {data['pods']}")
        logger.info(f"Jobs: {data['jobs']}")
        logger.info(f"Deployments: {data['deployments']}")

    # Print results
    # for namespace, data in output.items():
    #     print(f"\nNamespace: {namespace}")
    #     print(data) 

    logger.info("Nautilus Bot execution completed.")

if __name__ == "__main__":
    main()
