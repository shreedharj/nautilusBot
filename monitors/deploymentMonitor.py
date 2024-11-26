from kubernetes import client
from utils.kubeClient import loadKubeConfig
from utils.resourceUtil import calculateAge
from checks.deploymentChecks import checkDeploymentViolations
from utils.logger import logger

def monitorDeployments(namespaces):
    """Monitor deployments and their resource usage."""
    loadKubeConfig()
    appsV1 = client.AppsV1Api()
    deploymentData = []

    for namespace in namespaces:
        logger.info(f"Monitoring deployments in namespace '{namespace}'...")
        deployments = appsV1.list_namespaced_deployment(namespace)
        namespaceDeploymentViolationCount = 0
        
        for deployment in deployments.items:
            deploymentAge = calculateAge(deployment.metadata.creation_timestamp)
            requestedResources = deployment.spec.template.spec.containers[0].resources.requests or {}

            violations = checkDeploymentViolations(deployment, deploymentAge)

            deploymentData.append(
                {
                    "namespace": namespace,
                    "name": deployment.metadata.name,
                    "uid": deployment.metadata.uid,
                    "age": deploymentAge,
                    "replicas": deployment.status.ready_replicas,
                    "requestedResources": requestedResources,
                    "violations": checkDeploymentViolations(deployment, deploymentAge),
                }
            )

            # Log violations and count
            for violation in violations:
                namespaceDeploymentViolationCount += 1
                if "approaching 2 weeks" in violation:
                    logger.critical(f"CRITICAL: Deployment '{deployment.metadata.name}' in namespace '{namespace}' violation: {violation}")
                else:
                    logger.warning(f"WARNING: Deployment '{deployment.metadata.name}' in namespace '{namespace}' violation: {violation}")

        logger.info(f"Finished monitoring deployments in namespace '{namespace}'. Total violations: {namespaceDeploymentViolationCount}")
    return deploymentData
