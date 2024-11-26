from utils.resourceUtil import parseCpu, parseMemory
from utils.logger import logger

def checkPodViolations(pod, podAge, requestedResources, utilizedResources):
    """Check violations for a pod."""
    violations = []
    
    # GPU Check: Requesting more than 2 GPUs
    if "nvidia.com/gpu" in requestedResources:
        requestedGpus = int(requestedResources["nvidia.com/gpu"])
        if requestedGpus > 2:
            message = f"Requested GPUs exceed 2 (requested: {requestedGpus})"
            # logger.critical(f"Critical Violation for Pod '{pod.metadata.name}' in '{pod.metadata.namespace}': {message}")
            violations.append(message)

    # GPU Checks
    if "gpuUtilizationPercentage" in utilizedResources:
        gpuUtilizationPercentage = float(utilizedResources["gpuUtilizationPercentage"].replace("%", ""))
        if gpuUtilizationPercentage < 10: 
            message = "GPU underutilized (<10% of capacity)"
            # logger.warning(f"Warning for Pod '{pod.metadata.name}' in '{pod.metadata.namespace}': {message}")
            violations.append(message)

    # CPU Checks
    if "cpu" in requestedResources and "cpu" in utilizedResources:
        requestedCpu = parseCpu(requestedResources["cpu"])
        utilizedCpu = parseCpu(utilizedResources["cpu"])
        if utilizedCpu < 0.1 * requestedCpu:
            message = "CPU underutilized (<10% of requested)"
            # logger.warning(f"Warning for Pod '{pod.metadata.name}' in '{pod.metadata.namespace}': {message}")
            violations.append(message)

    # Memory Checks
    if "memory" in requestedResources and "memory" in utilizedResources:
        requestedMemory = parseMemory(requestedResources["memory"])
        utilizedMemory = parseMemory(utilizedResources["memory"])
        if utilizedMemory < 0.1 * requestedMemory:
            message = "Memory underutilized (<10% of requested)"
            # logger.warning(f"Warning for Pod '{pod.metadata.name}' in '{pod.metadata.namespace}': {message}")
            violations.append(message)

    return violations
