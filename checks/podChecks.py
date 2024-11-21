from utils.resourceUtil import parseCpu, parseMemory

def checkPodViolations(pod, podAge, requestedResources, utilizedResources):
    """Check violations for a pod."""
    violations = []
    
    # GPU Checks
    if "gpuUtilizationPercentage" in utilizedResources:
        gpuUtilizationPercentage = int(utilizedResources["gpuUtilizationPercentage"].replace("%", ""))
        if gpuUtilizationPercentage < 10: 
            violations.append(f"GPU underutilized (<10% of capacity)")

    # CPU Checks
    if "cpu" in requestedResources and "cpu" in utilizedResources:
        requestedCpu = parseCpu(requestedResources["cpu"])
        utilizedCpu = parseCpu(utilizedResources["cpu"])
        if utilizedCpu < 0.1 * requestedCpu:
            violations.append(f"CPU underutilized (<10% of requested)")

    # Memory Checks
    if "memory" in requestedResources and "memory" in utilizedResources:
        requestedMemory = parseMemory(requestedResources["memory"])
        utilizedMemory = parseMemory(utilizedResources["memory"])
        if utilizedMemory < 0.1 * requestedMemory:
            violations.append(f"Memory underutilized (<10% of requested)")

    return violations
