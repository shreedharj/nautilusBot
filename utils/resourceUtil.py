from datetime import datetime, timezone
import subprocess
from utils.logger import logger

def calculateAge(startTime):
    """Calculate the age of a resource."""
    now = datetime.now(timezone.utc)
    return (now - startTime).days if startTime else "Unknown"

def getPodUtilization(namespace, podName):
    """Fetch pod resource utilization using 'kubectl top'."""
    try:
        output = subprocess.check_output(
            ["kubectl", "top", "pod", podName, "-n", namespace],
            universal_newlines=True,
        )
        lines = output.splitlines()
        if len(lines) > 1:
            _, cpuUsage, memoryUsage = lines[1].split()
            return {"cpu": cpuUsage, "memory": memoryUsage}
    except subprocess.CalledProcessError as e:
        logger.error(f"Warning: Pod '{podName}' not found in namespace '{namespace}'")
        return {"cpu": "Unknown", "memory": "Unknown"}
    except ValueError:
        logger.error(f"Error parsing utilization for pod '{podName}' in namespace '{namespace}'")
        return {"cpu": "Unknown", "memory": "Unknown"}


def parseCpu(cpuStr):
    """Parse CPU requests/usage (e.g., '500m' to 0.5 cores)."""
    if cpuStr == "Unknown":
        return 0  # Default to 0 if usage is unknown
    if cpuStr.endswith("m"):
        return int(cpuStr[:-1]) / 1000
    return int(cpuStr)

def parseMemory(memoryStr):
    """Parse memory requests/usage (e.g., '128Mi', '1Gi', '100G')."""
    if memoryStr.endswith("Mi"):
        return int(memoryStr[:-2]) * 1024 * 1024  # Convert Mi to bytes
    elif memoryStr.endswith("Gi"):
        return int(memoryStr[:-2]) * 1024 * 1024 * 1024  # Convert Gi to bytes
    elif memoryStr.endswith("G"):
        return int(memoryStr[:-1]) * 1024 * 1024 * 1024  # Convert G to bytes
    elif memoryStr.isdigit():
        return int(memoryStr)  # Treat as bytes if no unit is provided
    else:
        raise ValueError(f"Unsupported memory format: {memoryStr}")
        logger.error(f"Unsupported memory format: {memoryStr}")

