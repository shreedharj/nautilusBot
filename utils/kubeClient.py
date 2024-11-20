from kubernetes import config

def loadKubeConfig():
    """Load Kubernetes configuration."""
    config.load_kube_config()

