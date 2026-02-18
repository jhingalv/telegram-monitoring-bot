import psutil
import docker

docker_client = docker.from_env()

def get_server_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
    }

def get_container_status():
    containers = docker_client.containers.list(all=True)
    data = []

    for c in containers:
        data.append({
            "name": c.name,
            "status": c.status
        })

    return data
