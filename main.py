from monitors.podMonitor import monitorPods
from monitors.jobMonitor import monitorJobs
from monitors.deploymentMonitor import monitorDeployments

def main():
    print("Starting Nautilus Bot...")

    namespaces = ["gilpin-lab", "aiea-interns", "aiea-auditors"]
    
    # Monitor resources
    podData = monitorPods(namespaces)
    jobData = monitorJobs(namespaces)
    deploymentData = monitorDeployments(namespaces)

    # Print results
    print("Pods:", podData)
    print("Jobs:", jobData)
    print("Deployments:", deploymentData)

if __name__ == "__main__":
    main()
