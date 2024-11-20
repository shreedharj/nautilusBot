from monitors.resourceUtil import parseCpu, parseMemory

def checkDeploymentViolations(deployment, deploymentAge):
    """Check violations for a deployment."""
    violations = []
    
    # Age Check
    if deploymentAge > 14:
        violations.append("Deployment older than 2 weeks")
    
    # Replicas Check
    if deployment.status.ready_replicas == 0:
        violations.append("Deployment has no ready replicas")
    
    return violations
