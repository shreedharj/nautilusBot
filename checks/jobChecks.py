def checkJobViolations(job, jobAge):
    """Check violations for a job."""
    violations = []
    
    # Age Check
    if jobAge > 12:
        violations.append("Job approaching 2 weeks age. Address this soon.")
    
    # Failed Status Check
    if job.status.failed:
        violations.append(f"Job failed {job.status.failed} times")
    
    # Cleanup Check
    if job.status.succeeded and not job.status.conditions:
        violations.append("Job succeeded but not cleaned up")
    
    return violations
