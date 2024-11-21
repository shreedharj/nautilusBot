from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge, getPodUtilization
from checks.podChecks import checkPodViolations

def monitorPods(namespaces, gpuMetrics):
    """Monitor pods and their resource usage."""
    loadKubeConfig()
    v1 = client.CoreV1Api()
    podData = []

    for namespace in namespaces:
        pods = v1.list_namespaced_pod(namespace)
        namesapceGpuMetrics = gpuMetrics.get(namespace, {}).get("gpuMetrics", [])
        for pod in pods.items:
            podStatus = pod.status.phase

            # Skip non-Running pods
            if podStatus not in ["Running"]:
                    print(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' as it is not running (state: {podStatus})")
                    continue

            # Skip pods in Error state
            if podStatus == "Error":
                print(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' as it is in Error state")
                continue

            podAge = calculateAge(pod.status.start_time)
            requestedResources = pod.spec.containers[0].resources.requests or {}
            utilizedResources = getPodUtilization(namespace, pod.metadata.name)

            # Add GPU metrics to utilized resources if available
            gpuUtilization = next(
                (gpu for gpu in namesapceGpuMetrics if gpu["podName"] == pod.metadata.name),
                None
            )
            if gpuUtilization:
                utilizedResources["gpuUtilizationPercentage"] = gpuUtilization["gpuUtilizationPercentage"]

            # Skip pods where utilization cannot be retrieved
            if utilizedResources["cpu"] == "Unknown" or utilizedResources["memory"] == "Unknown":
                print(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' due to missing utilization data")
                continue

            podData.append(
                {
                    "namespace": namespace,
                    "name": pod.metadata.name,
                    "age": podAge,
                    "status": pod.status.phase,
                    "requestedResources": requestedResources,
                    "utilizedResources": utilizedResources,
                    "violations": checkPodViolations(
                        pod, podAge, requestedResources, utilizedResources
                    ),
                }
            )
    return podData
