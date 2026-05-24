import docker
import tempfile
import os
from .base import ExecutionEngine
from ..config import settings

class DockerEngine(ExecutionEngine):
    def __init__(self):
        super().__init__()
        self.client = docker.from_env()
        
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
                stdout=True
            )
            return result.decode('utf-8')
        except docker.errors.ContainerError as e:
            # Container returned non-zero exit status
            raise Exception(f"Docker Execution Failed:\\n{e.stderr.decode('utf-8')}")
        except Exception as e:
            raise Exception(f"Docker Engine Error: {str(e)}")
