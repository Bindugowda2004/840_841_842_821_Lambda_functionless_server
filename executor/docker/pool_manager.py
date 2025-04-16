import docker
import threading
import time
from typing import Dict, List, Optional
from queue import Queue

class ContainerPool:
    def __init__(self, runtime: str, pool_size: int = 3):
        self.runtime = runtime
        self.pool_size = pool_size
        self.available: Queue[str] = Queue()
        self.in_use: Dict[str, float] = {}
        self.client = docker.from_env()
        self.lock = threading.Lock()
        
    def initialize(self):
        """Initialize the pool with warm containers"""
        for _ in range(self.pool_size):
            container = self._create_container()
            self.available.put(container.id)
            
    def _create_container(self):
        """Create a new container in a stopped state"""
        return self.client.containers.create(
            f"serverless-{self.runtime}:latest",
            command="tail -f /dev/null",  # Keep container running
            detach=True
        )
        
    def acquire(self) -> Optional[str]:
        """Get a container from the pool"""
        try:
            container_id = self.available.get_nowait()
            with self.lock:
                self.in_use[container_id] = time.time()
            return container_id
        except:
            return None
            
    def release(self, container_id: str):
        """Return a container to the pool"""
        with self.lock:
            if container_id in self.in_use:
                del self.in_use[container_id]
                self.available.put(container_id)
                
    def cleanup(self):
        """Remove all containers in the pool"""
        while not self.available.empty():
            container_id = self.available.get()
            try:
                container = self.client.containers.get(container_id)
                container.remove(force=True)
            except:
                pass
                
        with self.lock:
            for container_id in list(self.in_use.keys()):
                try:
                    container = self.client.containers.get(container_id)
                    container.remove(force=True)
                except:
                    pass
            self.in_use.clear()

class PoolManager:
    def __init__(self):
        self.pools: Dict[str, ContainerPool] = {
            "python": ContainerPool("python"),
            "javascript": ContainerPool("javascript")
        }
        
    def initialize(self):
        """Initialize all pools"""
        for pool in self.pools.values():
            pool.initialize()
            
    def get_pool(self, runtime: str) -> ContainerPool:
        """Get pool for specific runtime"""
        return self.pools.get(runtime)
        
    def cleanup(self):
        """Cleanup all pools"""
        for pool in self.pools.values():
            pool.cleanup()
