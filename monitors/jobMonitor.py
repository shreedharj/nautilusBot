from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge
from checks.jobChecks import checkJobViolations
from utils.logger import logger

def monitorJobs(namespaces):
    """Monitor jobs and their resource usage."""
    loadKubeConfig()
    batchV1 = client.BatchV1Api()
    jobData = []

    for namespace in namespaces:
        logger.info(f"Monitoring jobs in namespace '{namespace}'...")
        jobs = batchV1.list_namespaced_job(namespace)
        for job in jobs.items:
            jobAge = calculateAge(job.metadata.creation_timestamp)
            jobData.append(
                {
                    "namespace": namespace,
                    "name": job.metadata.name,
                    "uid": job.metadata.uid,
                    "age": jobAge,
                    "status": job.status.conditions[0].type if job.status.conditions else "Unknown",
                    "violations": checkJobViolations(job, jobAge),
                }
            )
        logger.info(f"Finished monitoring jobs in namespace '{namespace}'.")
    return jobData
