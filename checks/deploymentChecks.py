from utils.resourceUtil import parseCpu, parseMemory

def checkDeploymentViolations(deployment, deploymentAge):
    """Check violations for a deployment."""
    violations = []
    
    # Age Check
    if deploymentAge > 12:
        violations.append("Deployment approaching 2 weeks age. Address this soon.")
    
    # Replicas Check
    if deployment.status.ready_replicas == 0:
        violations.append("Deployment has no ready replicas")
    
    return violations
