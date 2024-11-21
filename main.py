from monitors.podMonitor import monitorPods
from monitors.jobMonitor import monitorJobs
from monitors.deploymentMonitor import monitorDeployments
from utils.scrapeGrafana import scrapeGpuMetrics

def main():
    print("Starting Nautilus Bot...")

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

    # Print results
    for namespace, data in output.items():
        print(f"\nNamespace: {namespace}")
        print(data) 

if __name__ == "__main__":
    main()
