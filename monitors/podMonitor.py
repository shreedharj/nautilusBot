from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge, getPodUtilization
from checks.podChecks import checkPodViolations
from utils.logger import logger

def getDeploymentForReplicaSet(replicaSetName, namespace):
    """Retrieve the Deployment managing a given ReplicaSet."""
    loadKubeConfig()
    apps_v1 = client.AppsV1Api()
    deployments = apps_v1.list_namespaced_deployment(namespace)
    for deployment in deployments.items:
        if deployment.metadata.name in replicaSetName:
            return deployment.metadata.name
    return None

def monitorPods(namespaces, gpuMetrics):
    """Monitor pods and their resource usage."""
    loadKubeConfig()
    v1 = client.CoreV1Api()
    podData = []

    for namespace in namespaces:
        logger.info(f"Monitoring pods in namespace '{namespace}'...")
        pods = v1.list_namespaced_pod(namespace)
        namesapceGpuMetrics = gpuMetrics.get(namespace, {}).get("gpuMetrics", [])
        namespacePodViolationCount = 0

        for pod in pods.items:
            podStatus = pod.status.phase

            # Skip non-Running pods
            if podStatus not in ["Running"]:
                logger.error(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' as it is not running (state: {podStatus})")
                continue

            # Skip pods in Error state
            if podStatus == "Error":
                logger.error(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' as it is in Error state")
                continue

            # Check for Owner References
            owner = pod.metadata.owner_references[0] if pod.metadata.owner_references else None
            # ownerInfo = f"managed by {owner.kind} '{owner.name}'" if owner else "independent"
            ownerInfo = "independent"
            if owner:
                if owner.kind == "ReplicaSet":
                    deploymentName = getDeploymentForReplicaSet(owner.name, namespace)
                    if deploymentName:
                        ownerInfo = f"managed by Deployment '{deploymentName}'"
                    else:
                        ownerInfo = f"managed by ReplicaSet '{owner.name}'"
                else:
                    ownerInfo = f"managed by {owner.kind} '{owner.name}'"

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
                logger.error(f"Skipping pod '{pod.metadata.name}' in namespace '{namespace}' due to missing utilization data")
                continue

            violations = checkPodViolations(pod, podAge, requestedResources, utilizedResources)

            podData.append(
                {
                    "namespace": namespace,
                    "name": pod.metadata.name,
                    "uid": pod.metadata.uid,
                    "age": podAge,
                    "status": pod.status.phase,
                    "requestedResources": requestedResources,
                    "utilizedResources": utilizedResources,
                    "violations": checkPodViolations(
                        pod, podAge, requestedResources, utilizedResources
                    ),
                }
            )

            # Log violations and count
            for violation in violations:
                namespacePodViolationCount += 1
                if "requesting more than 2 GPUs" in violation:
                    logger.critical(f"CRITICAL: Pod '{pod.metadata.name}' in namespace '{namespace}' ({ownerInfo}) violation: {violation}")
                else:
                    logger.warning(f"WARNING: Pod '{pod.metadata.name}' in namespace '{namespace}' ({ownerInfo}) violation: {violation}")

        logger.info(f"Finished monitoring pods in namespace '{namespace}'. Total violations: {namespacePodViolationCount}")
    return podData
