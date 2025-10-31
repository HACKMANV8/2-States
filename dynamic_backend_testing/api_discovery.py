"""
API Discovery Service for Dynamic Backend Testing

Discovers and introspects backend APIs to extract:
- OpenAPI/Swagger specifications
- Available endpoints and their methods
- Request/response schemas
- API metadata

Supports:
- FastAPI (native OpenAPI support)
- Flask with Flask-RESTX or similar
- Generic Python REST frameworks

This enables automatic MCP tool generation for any API.
"""

import importlib
import importlib.util
import sys
import json
import httpx
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import inspect

logger = logging.getLogger(__name__)


class APIDiscoveryService:
    """
    Service for discovering and introspecting backend APIs.

    This service can:
    1. Dynamically import Python API applications
    2. Extract OpenAPI specifications (if available)
    3. Discover endpoints through introspection
    4. Parse request/response schemas
    5. Generate metadata for MCP tool creation

    Example:
        discovery = APIDiscoveryService()
        spec = await discovery.discover_api(
            repo_path=Path("/path/to/repo"),
            app_module="main:app"
        )
    """

    def __init__(self):
        """Initialize the API discovery service."""
        logger.info("APIDiscoveryService initialized")

    async def discover_api(
        self,
        repo_path: Path,
        app_module: str,
        app_file: Optional[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Discover an API and extract its specification.

        This method:
        1. Attempts to import the API application
        2. Detects the framework (FastAPI, Flask, etc.)
        3. Extracts OpenAPI spec if available
        4. Falls back to introspection if needed

        Args:
            repo_path: Path to the repository containing the API
            app_module: Module path to the app (e.g., "main:app")
            app_file: Specific file containing the app (optional)
            auto_detect: Whether to auto-detect app location

        Returns:
            Dictionary containing:
            - framework: Detected framework name
            - openapi_spec: OpenAPI specification dict (if available)
            - endpoints: List of discovered endpoints
            - app_instance: The loaded app instance
            - metadata: Additional metadata

        Raises:
            RuntimeError: If API discovery fails
        """
        logger.info(f"Discovering API in {repo_path}")

        # Add repo to Python path
        sys.path.insert(0, str(repo_path))

        try:
            # Step 1: Load the application
            app_instance = await self._load_app(repo_path, app_module, app_file, auto_detect)

            if not app_instance:
                raise RuntimeError("Failed to load application instance")

            # Step 2: Detect framework
            framework = self._detect_framework(app_instance)
            logger.info(f"Detected framework: {framework}")

            # Step 3: Extract OpenAPI specification
            openapi_spec = await self._extract_openapi_spec(app_instance, framework)

            # Step 4: Discover endpoints
            endpoints = await self._discover_endpoints(app_instance, framework, openapi_spec)

            # Step 5: Gather metadata
            metadata = self._extract_metadata(app_instance, framework)

            result = {
                "framework": framework,
                "openapi_spec": openapi_spec,
                "endpoints": endpoints,
                "app_instance": app_instance,
                "metadata": metadata
            }

            logger.info(f"API discovery successful: {len(endpoints)} endpoints found")
            return result

        except Exception as e:
            error_msg = f"Failed to discover API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

        finally:
            # Remove repo from Python path
            if str(repo_path) in sys.path:
                sys.path.remove(str(repo_path))

    async def _load_app(
        self,
        repo_path: Path,
        app_module: str,
        app_file: Optional[str],
        auto_detect: bool
    ) -> Any:
        """
        Load the API application instance.

        Tries multiple methods:
        1. Direct import from module path (e.g., "main:app")
        2. Import from specific file
        3. Auto-detection of common app locations

        Args:
            repo_path: Path to the repository
            app_module: Module path (e.g., "main:app")
            app_file: Specific file path
            auto_detect: Whether to auto-detect

        Returns:
            Application instance

        Raises:
            RuntimeError: If app cannot be loaded
        """
        logger.debug(f"Loading app from module: {app_module}")

        # Method 1: Try direct import from module path
        try:
            if ":" in app_module:
                module_name, app_attr = app_module.split(":", 1)
            else:
                module_name = app_module
                app_attr = "app"  # Default app name

            # Import the module
            module = importlib.import_module(module_name)

            # Get the app instance
            app_instance = getattr(module, app_attr, None)

            if app_instance:
                logger.info(f"Successfully loaded app from {module_name}:{app_attr}")
                return app_instance

        except Exception as e:
            logger.warning(f"Failed to load app from module path: {e}")

        # Method 2: Try loading from specific file
        if app_file:
            try:
                app_instance = await self._load_from_file(repo_path / app_file, app_attr)
                if app_instance:
                    logger.info(f"Successfully loaded app from file: {app_file}")
                    return app_instance
            except Exception as e:
                logger.warning(f"Failed to load app from file: {e}")

        # Method 3: Auto-detection
        if auto_detect:
            app_instance = await self._auto_detect_app(repo_path)
            if app_instance:
                logger.info("Successfully loaded app via auto-detection")
                return app_instance

        raise RuntimeError("Could not load application instance")

    async def _load_from_file(self, file_path: Path, app_attr: str = "app") -> Any:
        """
        Load app from a specific Python file.

        Args:
            file_path: Path to the Python file
            app_attr: Attribute name of the app instance

        Returns:
            Application instance or None
        """
        if not file_path.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return getattr(module, app_attr, None)

        except Exception as e:
            logger.error(f"Error loading from file {file_path}: {e}")
            return None

    async def _auto_detect_app(self, repo_path: Path) -> Any:
        """
        Auto-detect application instance in common locations.

        Searches for:
        - main.py, app.py, api.py in root
        - app/main.py, src/main.py, etc.

        Args:
            repo_path: Path to the repository

        Returns:
            Application instance or None
        """
        logger.debug("Auto-detecting application...")

        # Common file names
        common_names = ["main.py", "app.py", "api.py", "server.py", "application.py"]

        # Common directory structures
        common_paths = [
            repo_path,
            repo_path / "app",
            repo_path / "src",
            repo_path / "api",
            repo_path / "backend",
        ]

        # Try each combination
        for directory in common_paths:
            if not directory.exists():
                continue

            for filename in common_names:
                file_path = directory / filename
                if file_path.exists():
                    logger.debug(f"Trying to load from: {file_path}")

                    # Try common app attribute names
                    for app_attr in ["app", "application", "api", "create_app"]:
                        app_instance = await self._load_from_file(file_path, app_attr)

                        if app_instance:
                            # If it's a callable (factory pattern), call it
                            if callable(app_instance) and app_attr == "create_app":
                                try:
                                    app_instance = app_instance()
                                except Exception as e:
                                    logger.warning(f"Failed to call create_app(): {e}")
                                    continue

                            logger.info(f"Auto-detected app at {file_path}:{app_attr}")
                            return app_instance

        logger.warning("Auto-detection failed")
        return None

    def _detect_framework(self, app_instance: Any) -> str:
        """
        Detect the web framework used by the application.

        Args:
            app_instance: The application instance

        Returns:
            Framework name ("fastapi", "flask", "django", "unknown")
        """
        app_type = type(app_instance).__name__
        app_module = type(app_instance).__module__

        # FastAPI detection
        if "fastapi" in app_module.lower() or app_type == "FastAPI":
            return "fastapi"

        # Flask detection
        if "flask" in app_module.lower() or app_type == "Flask":
            return "flask"

        # Django detection
        if "django" in app_module.lower():
            return "django"

        # Starlette (FastAPI's base)
        if "starlette" in app_module.lower():
            return "starlette"

        logger.warning(f"Unknown framework: {app_module}.{app_type}")
        return "unknown"

    async def _extract_openapi_spec(
        self,
        app_instance: Any,
        framework: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract OpenAPI specification from the application.

        Args:
            app_instance: The application instance
            framework: Detected framework name

        Returns:
            OpenAPI specification dict, or None if not available
        """
        logger.debug("Extracting OpenAPI specification...")

        if framework == "fastapi":
            return await self._extract_fastapi_openapi(app_instance)
        elif framework == "flask":
            return await self._extract_flask_openapi(app_instance)
        else:
            logger.warning(f"OpenAPI extraction not implemented for {framework}")
            return None

    async def _extract_fastapi_openapi(self, app_instance: Any) -> Dict[str, Any]:
        """
        Extract OpenAPI spec from FastAPI application.

        FastAPI provides an openapi() method that returns the full spec.

        Args:
            app_instance: FastAPI application instance

        Returns:
            OpenAPI specification dictionary
        """
        try:
            # FastAPI provides openapi() method
            if hasattr(app_instance, "openapi"):
                openapi_spec = app_instance.openapi()
                logger.info("Successfully extracted FastAPI OpenAPI spec")
                return openapi_spec

            # Fallback: try to access openapi_schema
            if hasattr(app_instance, "openapi_schema"):
                return app_instance.openapi_schema

        except Exception as e:
            logger.error(f"Failed to extract FastAPI OpenAPI spec: {e}")

        return {}

    async def _extract_flask_openapi(self, app_instance: Any) -> Optional[Dict[str, Any]]:
        """
        Extract OpenAPI spec from Flask application.

        Tries to extract from:
        - Flask-RESTX
        - Flask-Swagger
        - Flask-OpenAPI

        Args:
            app_instance: Flask application instance

        Returns:
            OpenAPI specification dict, or None
        """
        try:
            # Flask-RESTX
            if hasattr(app_instance, "__schema__"):
                return app_instance.__schema__

            # Flask-Swagger (check for swagger decorators)
            # This would require starting the app and hitting /swagger endpoint

        except Exception as e:
            logger.error(f"Failed to extract Flask OpenAPI spec: {e}")

        return None

    async def _discover_endpoints(
        self,
        app_instance: Any,
        framework: str,
        openapi_spec: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Discover API endpoints.

        Uses OpenAPI spec if available, otherwise falls back to introspection.

        Args:
            app_instance: Application instance
            framework: Framework name
            openapi_spec: OpenAPI specification (if available)

        Returns:
            List of endpoint dictionaries, each containing:
            - path: Endpoint path
            - method: HTTP method
            - operation_id: Operation identifier
            - summary: Endpoint description
            - parameters: Request parameters
            - request_body: Request body schema
            - responses: Response schemas
        """
        endpoints = []

        # Method 1: Extract from OpenAPI spec (preferred)
        if openapi_spec and "paths" in openapi_spec:
            endpoints = self._parse_openapi_endpoints(openapi_spec)
            logger.info(f"Discovered {len(endpoints)} endpoints from OpenAPI spec")
            return endpoints

        # Method 2: Framework-specific introspection
        if framework == "fastapi":
            endpoints = await self._introspect_fastapi_endpoints(app_instance)
        elif framework == "flask":
            endpoints = await self._introspect_flask_endpoints(app_instance)

        logger.info(f"Discovered {len(endpoints)} endpoints via introspection")
        return endpoints

    def _parse_openapi_endpoints(self, openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse endpoints from OpenAPI specification.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []

        for path, path_item in openapi_spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                    continue

                endpoint = {
                    "path": path,
                    "method": method.upper(),
                    "operation_id": operation.get("operationId", f"{method}_{path}"),
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "parameters": operation.get("parameters", []),
                    "request_body": operation.get("requestBody"),
                    "responses": operation.get("responses", {}),
                    "tags": operation.get("tags", [])
                }

                endpoints.append(endpoint)

        return endpoints

    async def _introspect_fastapi_endpoints(self, app_instance: Any) -> List[Dict[str, Any]]:
        """
        Introspect FastAPI application to discover endpoints.

        Args:
            app_instance: FastAPI application instance

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []

        try:
            # FastAPI stores routes in app.routes
            if hasattr(app_instance, "routes"):
                for route in app_instance.routes:
                    if hasattr(route, "path") and hasattr(route, "methods"):
                        for method in route.methods:
                            endpoint = {
                                "path": route.path,
                                "method": method,
                                "operation_id": getattr(route, "name", ""),
                                "summary": getattr(route, "summary", ""),
                                "description": ""
                            }
                            endpoints.append(endpoint)

        except Exception as e:
            logger.error(f"Failed to introspect FastAPI endpoints: {e}")

        return endpoints

    async def _introspect_flask_endpoints(self, app_instance: Any) -> List[Dict[str, Any]]:
        """
        Introspect Flask application to discover endpoints.

        Args:
            app_instance: Flask application instance

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []

        try:
            # Flask stores routes in app.url_map
            if hasattr(app_instance, "url_map"):
                for rule in app_instance.url_map.iter_rules():
                    for method in rule.methods:
                        if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            endpoint = {
                                "path": rule.rule,
                                "method": method,
                                "operation_id": rule.endpoint,
                                "summary": "",
                                "description": ""
                            }
                            endpoints.append(endpoint)

        except Exception as e:
            logger.error(f"Failed to introspect Flask endpoints: {e}")

        return endpoints

    def _extract_metadata(self, app_instance: Any, framework: str) -> Dict[str, Any]:
        """
        Extract metadata from the application.

        Args:
            app_instance: Application instance
            framework: Framework name

        Returns:
            Dictionary with metadata
        """
        metadata = {
            "framework": framework,
            "app_type": type(app_instance).__name__,
            "app_module": type(app_instance).__module__
        }

        # FastAPI metadata
        if framework == "fastapi":
            if hasattr(app_instance, "title"):
                metadata["title"] = app_instance.title
            if hasattr(app_instance, "version"):
                metadata["version"] = app_instance.version
            if hasattr(app_instance, "description"):
                metadata["description"] = app_instance.description

        # Flask metadata
        elif framework == "flask":
            if hasattr(app_instance, "name"):
                metadata["name"] = app_instance.name

        return metadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)