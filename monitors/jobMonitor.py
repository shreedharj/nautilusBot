from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge
from checks.jobChecks import checkJobViolations

def monitorJobs():
    """Monitor jobs and their resource usage."""
    loadKubeConfig()
    batchV1 = client.BatchV1Api()
    jobData = []

    namespaces = ["gilpin-lab", "aiea-interns", "aiea-auditors"]
    for namespace in namespaces:
        jobs = batchV1.list_namespaced_job(namespace)
        for job in jobs.items:
            jobAge = calculateAge(job.metadata.creation_timestamp)
            jobData.append(
                {
                    "namespace": namespace,
                    "name": job.metadata.name,
                    "age": jobAge,
                    "status": job.status.conditions[0].type if job.status.conditions else "Unknown",
                    "violations": checkJobViolations(job, jobAge),
                }
            )
    return jobData
