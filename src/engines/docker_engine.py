import docker
import tempfile
import os
import sys
import time
import subprocess
import logging
from .base import ExecutionEngine
from ..config import settings

logger = logging.getLogger(__name__)

class DockerEngine(ExecutionEngine):
    def __init__(self):
        super().__init__()
        self.client = self._connect_or_start_docker()
        
    def _connect_or_start_docker(self):
        try:
            return docker.from_env()
        except docker.errors.DockerException as e:
            logger.info(f"Docker daemon not found ({sys.platform}). Attempting to start Docker...")
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", "-a", "Docker"], check=True)
                elif sys.platform == "win32":
                    import os
                    docker_path = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Docker", "Docker", "Docker Desktop.exe")
                    if os.path.exists(docker_path):
                        # Popen used so it runs detached without blocking
                        subprocess.Popen([docker_path])
                    else:
                        raise Exception("Docker Desktop executable not found at default path.")
                elif sys.platform == "linux":
                    # Attempt to start the docker service on linux (may require passwordless sudo)
                    subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
                else:
                    raise Exception(f"Auto-start not implemented for OS: {sys.platform}")
            except Exception as open_err:
                raise Exception(f"Failed to start Docker automatically: {open_err}. Original error: {e}")
            
            # Poll until Docker is ready
            max_retries = 30
            for i in range(max_retries):
                try:
                    logger.info(f"Waiting for Docker to start... ({i+1}/{max_retries})")
                    client = docker.from_env()
                    client.ping()  # Verify connection is actually working
                    logger.info("Successfully connected to Docker!")
                    return client
                except docker.errors.DockerException:
                    time.sleep(2)
            raise Exception("Timed out waiting for Docker to start.")
        
    def execute(self, script_content: str) -> str:
        """
        Executes a python script inside an ephemeral docker container.
        Provides strong sandboxing:
        - read_only root filesystem
        - only `./workspace` is mounted (read/write)
        """
        # We need a way to pass the script to the container.
        # We can either mount a temp file, or pass it via command.
        # Passing via command is safer as it avoids creating host files outside workspace.
        
        container_workspace = "/workspace"
        volumes = {
            str(self.workspace_dir): {
                'bind': container_workspace,
                'mode': 'rw'
            }
        }
        
        try:
            # We use `python -c` to run the code.
            result = self.client.containers.run(
                image=settings.docker_image,
                command=["python", "-c", script_content],
                volumes=volumes,
                working_dir=container_workspace,
                read_only=True,
                network_disabled=True,
                remove=True,
                stderr=True,
                stdout=True,
                cap_drop=['ALL'],
                security_opt=['no-new-privileges']
            )
            return result.decode('utf-8')
        except docker.errors.ContainerError as e:
            # Container returned non-zero exit status
            raise Exception(f"Docker Execution Failed:\\n{e.stderr.decode('utf-8')}")
        except Exception as e:
            raise Exception(f"Docker Engine Error: {str(e)}")
