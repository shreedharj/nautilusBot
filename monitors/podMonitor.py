from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge, getPodUtilization
from checks.podChecks import checkPodViolations

def monitorPods():
    """Monitor pods and their resource usage."""
    loadKubeConfig()
    v1 = client.CoreV1Api()
    podData = []

    namespaces = ["gilpin-lab", "aiea-interns", "aiea-auditors"]
    for namespace in namespaces:
        pods = v1.list_namespaced_pod(namespace)
        for pod in pods.items:
            podAge = calculateAge(pod.status.start_time)
            requestedResources = pod.spec.containers[0].resources.requests or {}
            utilizedResources = getPodUtilization(namespace, pod.metadata.name)

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
