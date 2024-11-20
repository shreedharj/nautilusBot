from monitors.resourceUtil import parseCpu, parseMemory

def checkPodViolations(pod, podAge, requestedResources, utilizedResources):
    """Check violations for a pod."""
    violations = []
    
    # GPU Checks
    if "nvidia.com/gpu" in requestedResources:
        requestedGpus = int(requestedResources["nvidia.com/gpu"])
        utilizedGpus = int(utilizedResources.get("gpu", 0))  # Placeholder for GPU metric
        if utilizedGpus < 0.1 * requestedGpus:
            violations.append(f"GPU underutilized (<10% of requested)")

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
