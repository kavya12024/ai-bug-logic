"""
Docker execution module
Runs code in isolated Docker containers and captures output
"""
import docker
import io
import tarfile
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)

class DockerRunner:
    """Execute code in Docker containers"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def run_python_code(self, code: str, timeout: int = None) -> Tuple[int, str, str]:
        """
        Run Python code in a container
        
        Args:
            code: Python code to execute
            timeout: Timeout in seconds (defaults to Config.TIMEOUT_SECONDS)
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if timeout is None:
            timeout = Config.TIMEOUT_SECONDS
            
        try:
            logger.info("Running Python code in container")
            
            # Create a temporary file in memory
            container = self.client.containers.run(
                "python:3.11-slim",
                f"python -c {repr(code)}",
                stdout=True,
                stderr=True,
                detach=True
            )
            
            exit_code = container.wait()
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
            
            container.remove()
            
            logger.info(f"Python execution completed with exit code: {exit_code['StatusCode']}")
            return exit_code['StatusCode'], stdout, stderr
            
        except Exception as e:
            logger.error(f"Error running Python code: {e}")
            raise
    
    def run_nodejs_code(self, code: str, timeout: int = None) -> Tuple[int, str, str]:
        """
        Run Node.js code in a container
        
        Args:
            code: JavaScript code to execute
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if timeout is None:
            timeout = Config.TIMEOUT_SECONDS
        
        try:
            logger.info("Running Node.js code in container")
            
            container = self.client.containers.run(
                "node:18-alpine",
                f"node -e {repr(code)}",
                stdout=True,
                stderr=True,
                detach=True
            )
            
            exit_code = container.wait()
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
            
            container.remove()
            
            logger.info(f"Node.js execution completed with exit code: {exit_code['StatusCode']}")
            return exit_code['StatusCode'], stdout, stderr
            
        except Exception as e:
            logger.error(f"Error running Node.js code: {e}")
            raise
    
    def run_cpp_code(self, code: str, timeout: int = None) -> Tuple[int, str, str]:
        """
        Run C++ code in a container
        
        Args:
            code: C++ code to execute
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if timeout is None:
            timeout = Config.TIMEOUT_SECONDS
        
        try:
            logger.info("Running C++ code in container")
            
            # Create a simple compilation and execution script
            compile_and_run = f"""
cat > /tmp/main.cpp << 'EOF'
{code}
EOF
g++ -o /tmp/main /tmp/main.cpp && /tmp/main
"""
            
            container = self.client.containers.run(
                "gcc:latest",
                ["sh", "-c", compile_and_run],
                stdout=True,
                stderr=True,
                detach=True
            )
            
            exit_code = container.wait()
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
            
            container.remove()
            
            logger.info(f"C++ execution completed with exit code: {exit_code['StatusCode']}")
            return exit_code['StatusCode'], stdout, stderr
            
        except Exception as e:
            logger.error(f"Error running C++ code: {e}")
            raise
    
    def run_file(self, file_path: Path, language: str, timeout: int = None) -> Tuple[int, str, str]:
        """
        Run code from a file in Docker
        
        Args:
            file_path: Path to the code file
            language: Programming language ('python', 'nodejs', 'cpp')
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        if language.lower() == 'python':
            return self.run_python_code(code, timeout)
        elif language.lower() in ['nodejs', 'javascript', 'js']:
            return self.run_nodejs_code(code, timeout)
        elif language.lower() in ['cpp', 'c++']:
            return self.run_cpp_code(code, timeout)
        else:
            raise ValueError(f"Unsupported language: {language}")
