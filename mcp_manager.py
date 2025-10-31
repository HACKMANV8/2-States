"""
Dynamic MCP Server Manager for TestGPT.

Launches separate Playwright MCP server instances for each viewport/browser combination.
This ensures proper device emulation from initial page load.
"""

import asyncio
import json
import os
import subprocess
from typing import Dict, Optional, List
from agno.tools.mcp import MCPTools
from models import ViewportProfile, BrowserProfile


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
        full_command = f"npx -y @playwright/mcp@latest {' '.join(mcp_args)}"

        print(f"   🔌 Connecting to MCP server for {self.viewport.name} on {self.browser.name}")
        print(f"      Command: {full_command}")

        self.mcp_tools = MCPTools(command=full_command)

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
            try:
                print(f"   🔌 Disconnecting MCP server for {self.viewport.name}")
                # Properly close the MCP connection
                # Note: This may raise RuntimeError about cancel scope if called from different task
                # We suppress this as it's expected behavior when cleaning up across task boundaries
                await self.mcp_tools.close()
                print(f"      ✅ MCP connection closed successfully")
            except RuntimeError as e:
                # Expected error when closing across task boundaries
                if "cancel scope" in str(e):
                    print(f"      ✅ MCP connection closed (cross-task cleanup)")
                else:
                    print(f"   ⚠️  Runtime error disconnecting MCP server: {e}")
            except Exception as e:
                print(f"   ⚠️  Error disconnecting MCP server: {e}")
            finally:
                self.connected = False
                self.mcp_tools = None

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()


class DynamicMCPManager:
    """
    Manages multiple Playwright MCP server instances.

    Launches separate MCP servers for each viewport/browser combination
    to ensure proper device emulation from page load.
    """

    def __init__(self):
        self.instances: Dict[str, MCPServerInstance] = {}
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
        if instance_id in self.instances:
            instance = self.instances[instance_id]
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
        self.instances[instance_id] = instance

        return mcp_tools

    async def cleanup_all(self):
        """Cleanup all MCP server instances."""
        print(f"\n🧹 Cleaning up {len(self.instances)} MCP server instances...")

        for instance_id, instance in self.instances.items():
            try:
                await instance.disconnect()
            except Exception as e:
                print(f"   ⚠️  Error cleaning up {instance_id}: {e}")

        self.instances.clear()
        print("   ✅ All MCP servers cleaned up")

    def get_active_instances(self) -> List[MCPServerInstance]:
        """Get list of currently active MCP server instances."""
        return [inst for inst in self.instances.values() if inst.connected]

    def get_instance_info(self) -> dict:
        """Get information about running instances."""
        return {
            "total_instances": len(self.instances),
            "active_instances": len(self.get_active_instances()),
            "instances": [
                {
                    "id": inst.instance_id,
                    "viewport": inst.viewport.name,
                    "browser": inst.browser.name,
                    "port": inst.port,
                    "connected": inst.connected
                }
                for inst in self.instances.values()
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
