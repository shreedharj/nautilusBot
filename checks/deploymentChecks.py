from utils.resourceUtil import parseCpu, parseMemory
from utils.logger import logger

def checkDeploymentViolations(deployment, deploymentAge):
    """Check violations for a deployment."""
    violations = []
    
    # Age Check
    if deploymentAge > 12:
        message = "Deployment approaching 2 weeks age. Address this soon."
        # logger.critical(f"Critical Violation for Deployment '{job.metadata.name}' in '{job.metadata.namespace}': {message}")
        violations.append(message)
    
    # Replicas Check
    if deployment.status.ready_replicas == 0:
        message = "Deployment has no ready replicas"
        # logger.warning(f"Warning for Deployment '{job.metadata.name}' in '{job.metadata.namespace}': {message}")
    
    return violations
