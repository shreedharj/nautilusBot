from monitors.podMonitor import monitorPods
from monitors.jobMonitor import monitorJobs
from monitors.deploymentMonitor import monitorDeployments

def main():
    print("Starting Nautilus Bot...")
    
    # Monitor resources
    podData = monitorPods()
    jobData = monitorJobs()
    deploymentData = monitorDeployments()

    # Print results
    print("Pods:", podData)
    print("Jobs:", jobData)
    print("Deployments:", deploymentData)

if __name__ == "__main__":
    main()
