import docker
import tempfile
import os
import time
from typing import Dict, Any

class DockerExecutor:
    def __init__(self):
        try:
            # Try different Docker connection methods
            try:
                # First try environment-based connection
                self.client = docker.from_env()
            except:
                try:
                    # Then try Windows named pipe
                    self.client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                except:
                    # Finally try TCP
                    self.client = docker.DockerClient(base_url='tcp://localhost:2375')
            
            # Test connection
            self.client.ping()
            print("Docker connection successful")
            self._create_base_images()
        except Exception as e:
            print(f"Docker initialization failed: {str(e)}")
            self.client = None

    def execute(self, code: str, runtime: str, timeout: float) -> Dict[str, Any]:
        """Execute function code in a Docker container or locally"""
        if not self.client:
            # Enhanced local execution for Python functions
            if runtime == "python":
                try:
                    start_time = time.time()
                    # Create a local Python environment to execute the code
                    local_globals = {}
                    exec(code, local_globals)
                    if "handler" in local_globals and callable(local_globals["handler"]):
                        result = local_globals["handler"]()
                        execution_time = time.time() - start_time
                        return {
                            "status": "success",
                            "output": str(result),
                            "exit_code": 0,
                            "execution_time": execution_time
                        }
                except Exception as e:
                    return {
                        "status": "error",
                        "output": f"Local execution failed: {str(e)}",
                        "exit_code": -1,
                        "execution_time": 0
                    }
            return {
                "status": "error",
                "output": "Docker is not available and function cannot be executed locally",
                "exit_code": -1,
                "execution_time": 0
            }
            
        # Create temporary directory for function code
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write function code to file
            filename = "function.py" if runtime == "python" else "function.js"
            filepath = os.path.join(tmpdir, filename)
            
            # For Python functions, add a print statement to capture the return value
            if runtime == "python":
                code_with_print = code + "\n\nif __name__ == '__main__':\n    result = handler()\n    print(result)"
            else:
                code_with_print = code
                
            with open(filepath, "w") as f:
                f.write(code_with_print)
            
            try:
                start_time = time.time()
                # Use pre-built images
                image_name = "python:3.9-slim" if runtime == "python" else "node:16-slim"
                
                # Run container with mounted code
                container = self.client.containers.run(
                    image_name,
                    command=[runtime, f"/code/{filename}"],
                    volumes={
                        os.path.abspath(tmpdir): {
                            "bind": "/code",
                            "mode": "ro"
                        }
                    },
                    working_dir="/code",
                    detach=True,
                    remove=True
                )
                
                try:
                    # Wait for result with timeout
                    result = container.wait(timeout=timeout)
                    logs = container.logs().decode().strip()
                    execution_time = time.time() - start_time
                    
                    return {
                        "status": "success" if result["StatusCode"] == 0 else "error",
                        "output": logs,
                        "exit_code": result["StatusCode"],
                        "execution_time": execution_time
                    }
                except Exception as e:
                    # Make sure to cleanup container
                    try:
                        container.remove(force=True)
                    except:
                        pass
                    return {
                        "status": "error",
                        "output": f"Container execution failed: {str(e)}",
                        "exit_code": -1,
                        "execution_time": time.time() - start_time
                    }
                    
            except Exception as e:
                return {
                    "status": "error",
                    "output": f"Docker execution failed: {str(e)}",
                    "exit_code": -1,
                    "execution_time": 0
                }

    def _create_base_images(self):
        """Pull base images for Python and JavaScript functions"""
        if not self.client:
            return
            
        try:
            print("Pulling Python base image...")
            self.client.images.pull("python:3.9-slim")
            print("Python image pulled successfully")
            
            print("Pulling Node.js base image...")
            self.client.images.pull("node:16-slim")
            print("Node.js image pulled successfully")
        except Exception as e:
            print(f"Error pulling base images: {str(e)}")
