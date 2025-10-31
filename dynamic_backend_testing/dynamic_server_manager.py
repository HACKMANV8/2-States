"""
Dynamic Server Manager for Backend API Testing

Manages the lifecycle of dynamically loaded API servers and their MCP wrappers.

This module:
- Starts user's API server (FastAPI, Flask, etc.)
- Writes generated MCP wrapper to a temporary file
- Launches FastMCP server with the wrapper
- Performs health checks on both servers
- Provides MCP command for Agno integration
- Handles graceful shutdown

All operations work with arbitrary user APIs loaded at runtime.
"""

import subprocess
import sys
import time
import tempfile
import asyncio
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging
import signal
import os

logger = logging.getLogger(__name__)


class DynamicServerManager:
    """
    Manages lifecycle of dynamically loaded API servers.

    This class:
    1. Starts user's API server (using uvicorn for ASGI or Flask's server)
    2. Writes generated MCP wrapper code to temp file
    3. Starts FastMCP server process
    4. Health checks both servers
    5. Provides MCP command for Agno MCPTools integration
    6. Handles graceful shutdown of all processes

    Example:
        manager = DynamicServerManager()

        # Start user's API
        api_process = await manager.start_user_api(
            repo_path=Path("/path/to/repo"),
            app_module="main:app",
            framework="fastapi"
        )

        # Start MCP server with generated wrapper
        mcp_path, mcp_process = await manager.start_mcp_server(
            wrapper_code=generated_code,
            api_url="http://localhost:8000"
        )

        # Get MCP command for Agno
        mcp_command = manager.get_mcp_command()

        # Cleanup when done
        await manager.stop_all()
    """

    def __init__(self):
        """Initialize the dynamic server manager."""
        self.api_process: Optional[subprocess.Popen] = None
        self.mcp_process: Optional[subprocess.Popen] = None
        self.mcp_wrapper_path: Optional[Path] = None
        self.api_host: str = "127.0.0.1"
        self.api_port: int = 8000
        self.api_url: str = f"http://{self.api_host}:{self.api_port}"

        logger.info("DynamicServerManager initialized")

    async def start_user_api(
        self,
        repo_path: Path,
        app_module: str,
        framework: str,
        host: str = "127.0.0.1",
        port: int = 8000,
        venv_path: Optional[Path] = None
    ) -> subprocess.Popen:
        """
        Start the user's API server.

        This method detects the framework and starts the appropriate server:
        - FastAPI/Starlette: Uses uvicorn
        - Flask: Uses Flask's built-in server or gunicorn
        - Django: Uses runserver

        Args:
            repo_path: Path to the repository
            app_module: Module path to app (e.g., "main:app")
            framework: Detected framework ("fastapi", "flask", "django")
            host: Host to bind to
            port: Port to bind to
            venv_path: Optional path to virtual environment

        Returns:
            Process handle for the API server

        Raises:
            RuntimeError: If server fails to start
        """
        logger.info(f"Starting {framework} API server on {host}:{port}")

        self.api_host = host
        self.api_port = port
        self.api_url = f"http://{host}:{port}"

        # Determine Python executable (use venv if available)
        if venv_path:
            if os.name == "nt":  # Windows
                python_path = venv_path / "Scripts" / "python"
            else:  # Unix-like
                python_path = venv_path / "bin" / "python"
        else:
            python_path = sys.executable

        # Build server command based on framework
        if framework in ["fastapi", "starlette"]:
            # Use uvicorn for ASGI applications
            cmd = [
                str(python_path),
                "-m", "uvicorn",
                app_module,
                "--host", host,
                "--port", str(port),
                "--log-level", "info"
            ]

        elif framework == "flask":
            # Use Flask's built-in server (for development)
            # In production, would use gunicorn or similar
            cmd = [
                str(python_path),
                "-m", "flask",
                "run",
                "--host", host,
                "--port", str(port)
            ]

            # Set FLASK_APP environment variable
            env = os.environ.copy()
            env["FLASK_APP"] = app_module.replace(":", ".")

        elif framework == "django":
            # Use Django's runserver
            cmd = [
                str(python_path),
                "manage.py",
                "runserver",
                f"{host}:{port}"
            ]

        else:
            # Generic Python server
            # Try uvicorn as default
            cmd = [
                str(python_path),
                "-m", "uvicorn",
                app_module,
                "--host", host,
                "--port", str(port)
            ]

        logger.debug(f"Server command: {' '.join(cmd)}")

        try:
            # Start the server process
            env = os.environ.copy() if framework != "flask" else env
            env["PYTHONPATH"] = str(repo_path) + os.pathsep + env.get("PYTHONPATH", "")

            self.api_process = subprocess.Popen(
                cmd,
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env
            )

            # Wait for server to be ready
            logger.info("Waiting for API server to be ready...")
            if await self._wait_for_api_ready(timeout=30):
                logger.info(f"✅ API server started successfully at {self.api_url}")
                return self.api_process
            else:
                # Server failed to start
                self.api_process.terminate()
                raise RuntimeError("API server failed to start within timeout")

        except Exception as e:
            error_msg = f"Failed to start API server: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _wait_for_api_ready(self, timeout: int = 30) -> bool:
        """
        Wait for API server to be ready by checking health.

        Tries common health check endpoints:
        - /health
        - /
        - /docs (FastAPI)

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if server is ready, False if timeout
        """
        start_time = time.time()
        health_endpoints = ["/health", "/", "/docs"]

        while time.time() - start_time < timeout:
            # Check if process is still running
            if self.api_process and self.api_process.poll() is not None:
                logger.error("API server process terminated unexpectedly")
                return False

            # Try health check endpoints
            for endpoint in health_endpoints:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            f"{self.api_url}{endpoint}",
                            timeout=2.0,
                            follow_redirects=True
                        )
                        if response.status_code < 500:
                            logger.debug(f"Health check passed on {endpoint}")
                            return True
                except (httpx.ConnectError, httpx.ReadTimeout):
                    pass

            await asyncio.sleep(1)

        return False

    async def start_mcp_server(
        self,
        wrapper_code: str,
        api_url: Optional[str] = None
    ) -> Tuple[Path, subprocess.Popen]:
        """
        Start FastMCP server with generated wrapper code.

        This method:
        1. Creates a temporary file with the wrapper code
        2. Starts the file as a Python script (which runs FastMCP)
        3. Waits for the MCP server to be ready
        4. Returns the file path and process handle

        Args:
            wrapper_code: Generated MCP wrapper Python code
            api_url: Optional API URL to use (overrides default)

        Returns:
            Tuple of (wrapper_file_path, process_handle)

        Raises:
            RuntimeError: If MCP server fails to start
        """
        logger.info("Starting FastMCP server...")

        # Update API URL in wrapper code if specified
        if api_url:
            self.api_url = api_url
            wrapper_code = wrapper_code.replace(
                f'API_BASE_URL = "{self.api_url}"',
                f'API_BASE_URL = "{api_url}"'
            )

        # Create temporary file for the wrapper
        self.mcp_wrapper_path = self._create_temp_wrapper(wrapper_code)

        try:
            # Start the FastMCP server
            self.mcp_process = subprocess.Popen(
                [sys.executable, str(self.mcp_wrapper_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait for MCP server to be ready
            logger.info("Waiting for FastMCP server to be ready...")
            if await self._wait_for_mcp_ready(timeout=10):
                logger.info("✅ FastMCP server started successfully")
                return self.mcp_wrapper_path, self.mcp_process
            else:
                # Server failed to start
                self.mcp_process.terminate()
                raise RuntimeError("FastMCP server failed to start within timeout")

        except Exception as e:
            error_msg = f"Failed to start FastMCP server: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _create_temp_wrapper(self, wrapper_code: str) -> Path:
        """
        Create a temporary file with the wrapper code.

        Args:
            wrapper_code: Python code to write

        Returns:
            Path to the created file
        """
        # Create temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            prefix='mcp_wrapper_',
            delete=False
        ) as f:
            f.write(wrapper_code)
            temp_path = Path(f.name)

        logger.debug(f"Created temp wrapper at {temp_path}")
        return temp_path

    async def _wait_for_mcp_ready(self, timeout: int = 10) -> bool:
        """
        Wait for MCP server to be ready.

        The MCP server is ready when the process is running and
        hasn't crashed immediately.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if server is ready, False if timeout or crash
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if process is still running
            if self.mcp_process and self.mcp_process.poll() is not None:
                # Process terminated
                logger.error("MCP server process terminated unexpectedly")
                return False

            # MCP servers typically start quickly
            # Just wait a bit to ensure no immediate crash
            await asyncio.sleep(0.5)

            # If process is still running after a few checks, consider it ready
            if time.time() - start_time > 2:
                return True

        return False

    def get_mcp_command(self) -> str:
        """
        Get the MCP command string for use with Agno MCPTools.

        Returns:
            Command string to pass to MCPTools

        Example:
            mcp_command = manager.get_mcp_command()
            mcp_tools = MCPTools(command=mcp_command)
            await mcp_tools.connect()
        """
        if not self.mcp_wrapper_path:
            raise RuntimeError("MCP server not started yet")

        command = f"{sys.executable} {self.mcp_wrapper_path}"
        return command

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information for both servers.

        Returns:
            Dictionary with server connection details
        """
        return {
            "api_url": self.api_url,
            "api_running": self.is_api_running(),
            "mcp_command": self.get_mcp_command() if self.mcp_wrapper_path else None,
            "mcp_running": self.is_mcp_running(),
            "mcp_wrapper_path": str(self.mcp_wrapper_path) if self.mcp_wrapper_path else None
        }

    def is_api_running(self) -> bool:
        """
        Check if API server is running.

        Returns:
            True if running, False otherwise
        """
        if not self.api_process:
            return False

        # Check if process is still alive
        if self.api_process.poll() is not None:
            return False

        return True

    def is_mcp_running(self) -> bool:
        """
        Check if MCP server is running.

        Returns:
            True if running, False otherwise
        """
        if not self.mcp_process:
            return False

        # Check if process is still alive
        if self.mcp_process.poll() is not None:
            return False

        return True

    async def stop_api_server(self) -> None:
        """Stop the API server gracefully."""
        if self.api_process:
            logger.info("Stopping API server...")
            self.api_process.terminate()

            try:
                self.api_process.wait(timeout=5)
                logger.info("API server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Force killing API server...")
                self.api_process.kill()
                self.api_process.wait()

            self.api_process = None

    async def stop_mcp_server(self) -> None:
        """Stop the MCP server gracefully."""
        if self.mcp_process:
            logger.info("Stopping MCP server...")
            self.mcp_process.terminate()

            try:
                self.mcp_process.wait(timeout=5)
                logger.info("MCP server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Force killing MCP server...")
                self.mcp_process.kill()
                self.mcp_process.wait()

            self.mcp_process = None

        # Clean up temp wrapper file
        if self.mcp_wrapper_path and self.mcp_wrapper_path.exists():
            try:
                self.mcp_wrapper_path.unlink()
                logger.debug(f"Removed temp wrapper file: {self.mcp_wrapper_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")

            self.mcp_wrapper_path = None

    async def stop_all(self) -> None:
        """Stop both API and MCP servers."""
        logger.info("Stopping all servers...")
        await self.stop_mcp_server()
        await self.stop_api_server()
        logger.info("All servers stopped")

    def __del__(self):
        """Cleanup on deletion."""
        # Try to stop servers if still running
        if self.api_process or self.mcp_process:
            logger.warning("DynamicServerManager deleted with running servers")
            # Note: Can't use async in __del__, so just terminate
            if self.api_process:
                self.api_process.terminate()
            if self.mcp_process:
                self.mcp_process.terminate()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
