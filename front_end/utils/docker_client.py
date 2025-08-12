import docker


def get_client():
    try:
        return docker.from_env()
    except docker.errors.DockerException:
        return None
