import docker
import tempfile
import os
from typing import Dict, Any
from .pool_manager import PoolManager

class DockerExecutor:
    def __init__(self):
        self.client = docker.from_env()
        self.pool_manager = PoolManager()
        self._create_base_images()
        self.pool_manager.initialize()

    def _create_base_images(self):
        """Create base images for Python and JavaScript functions"""
        # Python base image
        python_dockerfile = """
        FROM python:3.9-slim
        WORKDIR /app
        COPY function.py .
        CMD ["python", "function.py"]
        """
        
        # JavaScript base image
        js_dockerfile = """
        FROM node:16-slim
        WORKDIR /app
        COPY function.js .
        CMD ["node", "function.js"]
        """
        
        # Build base images
        with tempfile.TemporaryDirectory() as tmpdir:
            # Python
            with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
                f.write(python_dockerfile)
            self.client.images.build(path=tmpdir, tag="serverless-python:latest")
            
            # JavaScript
            with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
                f.write(js_dockerfile)
            self.client.images.build(path=tmpdir, tag="serverless-js:latest")

    def execute(self, code: str, runtime: str, timeout: float) -> Dict[str, Any]:
        """Execute function code in a Docker container"""
        pool = self.pool_manager.get_pool(runtime)
        container_id = pool.acquire()
        
        if not container_id:
            return {
                "status": "error",
                "output": "No available containers in pool",
                "exit_code": -1
            }
            
        try:
            container = self.client.containers.get(container_id)
            
            # Create temporary directory for function code
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write function code to file
                filename = "function.py" if runtime == "python" else "function.js"
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, "w") as f:
                    f.write(code)
                
                # Copy code to container
                with open(filepath, "rb") as f:
                    container.exec_run(f"rm -f /app/{filename}")
                    container.put_archive("/app", f.read())
                
                # Execute function
                result = container.exec_run(
                    cmd=f"python {filename}" if runtime == "python" else f"node {filename}",
                    workdir="/app",
                    demux=True
                )
                
                stdout = result.output[0].decode() if result.output[0] else ""
                stderr = result.output[1].decode() if result.output[1] else ""
                
                return {
                    "status": "success" if result.exit_code == 0 else "error",
                    "output": stdout,
                    "error": stderr,
                    "exit_code": result.exit_code
                }
                
        except Exception as e:
            return {
                "status": "error",
                "output": str(e),
                "exit_code": -1
            }
        finally:
            pool.release(container_id)

    def cleanup(self):
        """Cleanup all container pools"""
        self.pool_manager.cleanup()
