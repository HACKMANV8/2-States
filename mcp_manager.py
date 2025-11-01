"""
Dynamic MCP Server Manager for TestGPT.

Launches separate Playwright MCP server instances for each viewport/browser combination.
This ensures proper device emulation from initial page load.

Also manages dynamic backend testing MCP servers for API testing.
"""

import asyncio
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, List
from agno.tools.mcp import MCPTools
from models import ViewportProfile, BrowserProfile

# Add dynamic_backend_testing to path
sys.path.insert(0, str(Path(__file__).parent / "dynamic_backend_testing"))

from dynamic_backend_testing import DynamicBackendOrchestrator


class MCPServerInstance:
    """Represents a single running MCP server instance."""

    def __init__(
        self,
        instance_id: str,
        viewport: ViewportProfile,
        browser: BrowserProfile,
        port: int,
        process: Optional[subprocess.Popen] = None
    ):
        self.instance_id = instance_id
        self.viewport = viewport
        self.browser = browser
        self.port = port
        self.process = process
        self.mcp_tools: Optional[MCPTools] = None
        self.connected = False

    async def connect(self) -> MCPTools:
        """Connect to this MCP server instance."""
        if self.mcp_tools and self.connected:
            return self.mcp_tools

        # Build MCP command with viewport and browser args
        mcp_args = self._build_mcp_args()

        # Build full command string (MCPTools expects single string, not separate args)
        # Use shlex.quote to properly escape arguments with spaces
        quoted_args = ' '.join(shlex.quote(arg) for arg in mcp_args)
        full_command = f"npx -y @playwright/mcp@latest {quoted_args}"

        print(f"   🔌 Connecting to MCP server for {self.viewport.name} on {self.browser.name}")
        print(f"      Command: {full_command}")

        self.mcp_tools = MCPTools(
            command=full_command,
            exclude_tools=["browser_resize"]
        )

        await self.mcp_tools.connect()
        self.connected = True

        print(f"      ✅ Connected to MCP server (port {self.port})")

        return self.mcp_tools

    def _build_mcp_args(self) -> List[str]:
        """Build MCP launch arguments for this viewport/browser combination."""
        args = []

        # Load config for MCP args
        config = self._load_config()

        # Add viewport args
        if self.viewport.name in config.get("viewports", {}):
            viewport_config = config["viewports"][self.viewport.name]
            args.extend(viewport_config.get("mcp_launch_args", []))
        else:
            # Fallback: use viewport-size if no device preset
            args.append(f"--viewport-size={self.viewport.width}x{self.viewport.height}")

        # Add browser args
        if self.browser.name in config.get("browsers", {}):
            browser_config = config["browsers"][self.browser.name]
            args.extend(browser_config.get("mcp_launch_args", []))
        else:
            # Fallback
            args.append(f"--browser={self.browser.engine}")

        # Note: Playwright MCP uses stdio, not HTTP ports
        # Each instance is isolated via separate process/stdio connection

        return args

    def _load_config(self) -> dict:
        """Load config.json."""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    async def disconnect(self):
        """Disconnect and cleanup this MCP server instance."""
        if self.mcp_tools:
            print(f"   🔌 Disconnecting MCP server for {self.viewport.name}")
            # Note: We don't call close() because it causes RuntimeError when called across task boundaries
            # The MCP connection will be cleaned up automatically when the program exits
            # This is a known limitation with asyncio cancel scopes and stdio connections
            self.connected = False
            self.mcp_tools = None
            print(f"      ✅ MCP connection released (will cleanup on exit)")

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()


class BackendTestingMCPInstance:
    """Represents a backend API testing MCP server instance."""

    def __init__(
        self,
        instance_id: str,
        repo_url: Optional[str] = None,
        api_path: Optional[Path] = None,
        app_module: str = "main:app"
    ):
        self.instance_id = instance_id
        self.repo_url = repo_url
        self.api_path = api_path
        self.app_module = app_module
        self.mcp_tools: Optional[MCPTools] = None
        self.connected = False
        self.orchestrator: Optional[DynamicBackendOrchestrator] = None
        self.server_manager = None

    async def connect(self) -> MCPTools:
        """Connect to backend testing MCP server."""
        if self.mcp_tools and self.connected:
            return self.mcp_tools

        print(f"\n🚀 Launching dynamic backend testing MCP server")
        if self.repo_url:
            print(f"   Repository: {self.repo_url}")
        elif self.api_path:
            print(f"   Local path: {self.api_path}")

        # Initialize orchestrator
        self.orchestrator = DynamicBackendOrchestrator()

        # Start API server and generate MCP wrapper
        if self.repo_url:
            # Clone repo and discover API
            from dynamic_backend_testing.repo_manager import RepoManager
            from dynamic_backend_testing.api_discovery import APIDiscoveryService
            from dynamic_backend_testing.mcp_generator import MCPGenerator
            from dynamic_backend_testing.dynamic_server_manager import DynamicServerManager

            repo_manager = RepoManager()
            repo_path = await repo_manager.clone_repo(self.repo_url)
            await repo_manager.install_dependencies(repo_path)

            discovery = APIDiscoveryService()
            api_spec = await discovery.discover_api(
                repo_path=repo_path,
                app_module=self.app_module,
                auto_detect=True
            )

            generator = MCPGenerator()
            wrapper_code = generator.generate_mcp_wrapper(
                api_spec=api_spec,
                api_base_url=f"http://127.0.0.1:8000"
            )

            self.server_manager = DynamicServerManager()
            await self.server_manager.start_user_api(
                repo_path=repo_path,
                app_module=self.app_module,
                framework=api_spec['framework']
            )
            await self.server_manager.start_mcp_server(
                wrapper_code=wrapper_code,
                api_url="http://127.0.0.1:8000"
            )

            mcp_command = self.server_manager.get_mcp_command()

        elif self.api_path:
            # Use local API
            from dynamic_backend_testing.api_discovery import APIDiscoveryService
            from dynamic_backend_testing.mcp_generator import MCPGenerator
            from dynamic_backend_testing.dynamic_server_manager import DynamicServerManager

            discovery = APIDiscoveryService()
            api_spec = await discovery.discover_api(
                repo_path=self.api_path,
                app_module=self.app_module,
                auto_detect=True
            )

            generator = MCPGenerator()
            wrapper_code = generator.generate_mcp_wrapper(
                api_spec=api_spec,
                api_base_url=f"http://127.0.0.1:8000"
            )

            self.server_manager = DynamicServerManager()
            await self.server_manager.start_user_api(
                repo_path=self.api_path,
                app_module=self.app_module,
                framework=api_spec['framework']
            )
            await self.server_manager.start_mcp_server(
                wrapper_code=wrapper_code,
                api_url="http://127.0.0.1:8000"
            )

            mcp_command = self.server_manager.get_mcp_command()

        else:
            raise ValueError("Either repo_url or api_path must be provided")

        print(f"   🔌 Connecting to backend testing MCP server")
        print(f"      Command: {mcp_command}")

        self.mcp_tools = MCPTools(command=mcp_command)
        await self.mcp_tools.connect()
        self.connected = True

        print(f"      ✅ Backend testing MCP connected")

        return self.mcp_tools

    async def disconnect(self):
        """Disconnect and cleanup backend testing MCP server."""
        if self.mcp_tools:
            try:
                print(f"   🔌 Disconnecting backend testing MCP server")
                await self.mcp_tools.close()
                print(f"      ✅ Backend MCP connection closed")
            except Exception as e:
                print(f"   ⚠️  Error disconnecting backend MCP: {e}")
            finally:
                self.connected = False
                self.mcp_tools = None

        if self.server_manager:
            try:
                await self.server_manager.stop_all()
            except Exception as e:
                print(f"   ⚠️  Error stopping backend servers: {e}")


class DynamicMCPManager:
    """
    Manages multiple Playwright MCP server instances AND backend testing MCP servers.

    Launches separate MCP servers for:
    - Each viewport/browser combination (Playwright)
    - Dynamic backend API testing (FastMCP with auto-generated wrappers)
    """

    def __init__(self):
        self.playwright_instances: Dict[str, MCPServerInstance] = {}
        self.backend_instances: Dict[str, BackendTestingMCPInstance] = {}
        self.next_port = 8900  # Start port for MCP servers

    async def get_mcp_tools_for_cell(
        self,
        viewport: ViewportProfile,
        browser: BrowserProfile
    ) -> MCPTools:
        """
        Get or create MCP tools instance for specific viewport/browser combination.

        Args:
            viewport: ViewportProfile to emulate
            browser: BrowserProfile to use

        Returns:
            MCPTools connected to MCP server with correct viewport/browser settings
        """
        # Create instance ID
        instance_id = f"{viewport.name}_{browser.name}"

        # Return existing if already connected
        if instance_id in self.playwright_instances:
            instance = self.playwright_instances[instance_id]
            if instance.connected:
                print(f"   ♻️  Reusing existing MCP connection for {viewport.name} / {browser.name}")
                return instance.mcp_tools

        # Create new instance
        print(f"\n🚀 Launching dedicated MCP server for {viewport.display_name} / {browser.display_name}")

        port = self.next_port
        self.next_port += 1

        instance = MCPServerInstance(
            instance_id=instance_id,
            viewport=viewport,
            browser=browser,
            port=port
        )

        # Connect to MCP server
        mcp_tools = await instance.connect()

        # Store instance
        self.playwright_instances[instance_id] = instance

        return mcp_tools

    async def get_backend_mcp_tools(
        self,
        repo_url: Optional[str] = None,
        api_path: Optional[Path] = None,
        app_module: str = "main:app"
    ) -> MCPTools:
        """
        Get or create backend testing MCP instance for API testing.

        Args:
            repo_url: GitHub repository URL to clone and test
            api_path: Local path to API code
            app_module: Module path for API (e.g., "main:app")

        Returns:
            MCPTools connected to backend testing MCP server
        """
        # Create instance ID based on repo or path
        if repo_url:
            instance_id = f"backend_{repo_url.split('/')[-1]}"
        elif api_path:
            instance_id = f"backend_{api_path.name}"
        else:
            raise ValueError("Either repo_url or api_path must be provided")

        # Return existing if already connected
        if instance_id in self.backend_instances:
            instance = self.backend_instances[instance_id]
            if instance.connected:
                print(f"   ♻️  Reusing existing backend MCP connection for {instance_id}")
                return instance.mcp_tools

        # Create new instance
        print(f"\n🚀 Launching backend testing MCP server for {instance_id}")

        instance = BackendTestingMCPInstance(
            instance_id=instance_id,
            repo_url=repo_url,
            api_path=api_path,
            app_module=app_module
        )

        # Connect to backend testing MCP server
        mcp_tools = await instance.connect()

        # Store instance
        self.backend_instances[instance_id] = instance

        return mcp_tools

    async def cleanup_instance(self, viewport: ViewportProfile, browser: BrowserProfile):
        """
        Cleanup a specific MCP server instance after cell execution.

        This ensures each cell gets a fresh MCP server with correct browser/viewport config.

        Args:
            viewport: ViewportProfile of the instance to cleanup
            browser: BrowserProfile of the instance to cleanup
        """
        instance_id = f"{viewport.name}_{browser.name}"

        if instance_id in self.playwright_instances:
            instance = self.playwright_instances[instance_id]
            try:
                print(f"   🧹 Cleaning up MCP instance: {instance_id}")
                await instance.disconnect()
                del self.playwright_instances[instance_id]
                print(f"      ✅ MCP instance cleaned up")
            except Exception as e:
                print(f"      ⚠️  Error cleaning up {instance_id}: {e}")

    async def cleanup_all(self):
        """Cleanup all MCP server instances (Playwright and Backend)."""
        total_instances = len(self.playwright_instances) + len(self.backend_instances)
        print(f"\n🧹 Cleaning up {total_instances} MCP server instances...")

        # Cleanup Playwright instances
        for instance_id, instance in self.playwright_instances.items():
            try:
                await instance.disconnect()
            except Exception as e:
                print(f"   ⚠️  Error cleaning up Playwright instance {instance_id}: {e}")

        # Cleanup backend instances
        for instance_id, instance in self.backend_instances.items():
            try:
                await instance.disconnect()
            except Exception as e:
                print(f"   ⚠️  Error cleaning up backend instance {instance_id}: {e}")

        self.playwright_instances.clear()
        self.backend_instances.clear()
        print("   ✅ All MCP servers cleaned up")

    def get_active_instances(self) -> dict:
        """Get list of currently active MCP server instances."""
        return {
            "playwright": [inst for inst in self.playwright_instances.values() if inst.connected],
            "backend": [inst for inst in self.backend_instances.values() if inst.connected]
        }

    def get_instance_info(self) -> dict:
        """Get information about running instances."""
        active = self.get_active_instances()

        return {
            "total_instances": len(self.playwright_instances) + len(self.backend_instances),
            "active_playwright_instances": len(active["playwright"]),
            "active_backend_instances": len(active["backend"]),
            "playwright_instances": [
                {
                    "id": inst.instance_id,
                    "viewport": inst.viewport.name,
                    "browser": inst.browser.name,
                    "port": inst.port,
                    "connected": inst.connected
                }
                for inst in self.playwright_instances.values()
            ],
            "backend_instances": [
                {
                    "id": inst.instance_id,
                    "repo_url": inst.repo_url,
                    "api_path": str(inst.api_path) if inst.api_path else None,
                    "connected": inst.connected
                }
                for inst in self.backend_instances.values()
            ]
        }


# Global singleton instance
_mcp_manager: Optional[DynamicMCPManager] = None


def get_mcp_manager() -> DynamicMCPManager:
    """Get the global MCP manager singleton."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = DynamicMCPManager()
    return _mcp_manager
