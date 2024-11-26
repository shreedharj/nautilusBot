from utils.logger import logger

def checkJobViolations(job, jobAge):
    """Check violations for a job."""
    violations = []
    
    # Age Check
    if jobAge > 12:
        message = "Job approaching 2 weeks age. Address this soon."
        # logger.critical(f"Critical Violation for Job '{job.metadata.name}' in '{job.metadata.namespace}': {message}")
        violations.append(message)
    
    # Failed Status Check
    if job.status.failed:
        message = f"Job failed {job.status.failed} times"
        # logger.warning(f"Warning for Job '{job.metadata.name}' in '{job.metadata.namespace}': {message}")
        violations.append(message)
    
    # Cleanup Check
    if job.status.succeeded and not job.status.conditions:
        message = "Job succeeded but not cleaned up"
        # logger.warning(f"Warning for Job '{job.metadata.name}' in '{job.metadata.namespace}': {message}")
        violations.append(message)
    
    return violations
