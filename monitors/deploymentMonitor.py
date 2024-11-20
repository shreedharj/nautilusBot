from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge
from checks.deploymentChecks import checkDeploymentViolations

def monitorDeployments(namespaces):
    """Monitor deployments and their resource usage."""
    loadKubeConfig()
    appsV1 = client.AppsV1Api()
    deploymentData = []

    for namespace in namespaces:
        deployments = appsV1.list_namespaced_deployment(namespace)
        for deployment in deployments.items:
            deploymentAge = calculateAge(deployment.metadata.creation_timestamp)
            requestedResources = deployment.spec.template.spec.containers[0].resources.requests or {}

            deploymentData.append(
                {
                    "namespace": namespace,
                    "name": deployment.metadata.name,
                    "age": deploymentAge,
                    "replicas": deployment.status.ready_replicas,
                    "requestedResources": requestedResources,
                    "violations": checkDeploymentViolations(deployment, deploymentAge),
                }
            )
    return deploymentData
