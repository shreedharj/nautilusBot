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
        namespaceJobViolationCount = 0

        for job in jobs.items:
            jobAge = calculateAge(job.metadata.creation_timestamp)

            violations = checkJobViolations(job, jobAge, requestedResources)
            
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

            # Log violations and count
            for violation in violations:
                namespaceJobViolationCount += 1
                if "approaching 2 weeks" in violation:
                    logger.critical(f"CRITICAL: Job '{job.metadata.name}' in namespace '{namespace}' violation: {violation}")
                else:
                    logger.warning(f"WARNING: Job '{job.metadata.name}' in namespace '{namespace}' violation: {violation}")

        logger.info(f"Finished monitoring jobs in namespace '{namespace}'. Total violations: {namespaceJobViolationCount}")
    return jobData
