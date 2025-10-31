"""
Repository Manager for Dynamic Backend Testing

Handles Git operations including:
- Cloning repositories
- Checking out branches and PRs
- Managing temporary workspaces
- Dependency installation

This module enables testing of user-submitted APIs from any Git repository.
"""

import subprocess
import shutil
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RepoManager:
    """
    Manages Git repository operations for dynamic API testing.

    This class handles:
    - Cloning repositories from URLs
    - Checking out specific branches or PRs
    - Managing temporary workspace directories
    - Installing dependencies from requirements.txt
    - Cleaning up resources

    Example:
        manager = RepoManager()
        repo_path = await manager.clone_repo(
            "https://github.com/user/api-repo",
            branch="main"
        )
        await manager.install_dependencies(repo_path)
        # ... test the API ...
        manager.cleanup(repo_path)
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize the repository manager.

        Args:
            workspace_root: Base directory for cloned repos.
                          If None, uses system temp directory.
        """
        self.workspace_root = workspace_root or Path(tempfile.gettempdir()) / "api_testing_workspace"
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"RepoManager initialized with workspace: {self.workspace_root}")

    async def clone_repo(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        pr_number: Optional[int] = None,
        commit: Optional[str] = None
    ) -> Path:
        """
        Clone a Git repository and checkout the specified ref.

        Args:
            repo_url: Git repository URL (https or ssh)
            branch: Branch name to checkout (optional)
            pr_number: GitHub PR number to checkout (optional)
            commit: Specific commit hash to checkout (optional)

        Returns:
            Path to the cloned repository

        Raises:
            RuntimeError: If git operations fail
        """
        logger.info(f"Cloning repository: {repo_url}")

        # Extract repo name from URL for workspace directory
        repo_name = self._extract_repo_name(repo_url)
        repo_path = self.workspace_root / repo_name

        # Remove existing directory if it exists
        if repo_path.exists():
            logger.warning(f"Removing existing directory: {repo_path}")
            shutil.rmtree(repo_path)

        try:
            # Clone the repository
            clone_cmd = ["git", "clone", repo_url, str(repo_path)]
            if branch:
                # Clone specific branch for efficiency
                clone_cmd.extend(["--branch", branch, "--single-branch"])

            logger.debug(f"Running: {' '.join(clone_cmd)}")
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Repository cloned successfully to {repo_path}")

            # Handle PR checkout if specified
            if pr_number:
                await self._checkout_pr(repo_path, pr_number)
            # Handle commit checkout if specified
            elif commit:
                await self._checkout_commit(repo_path, commit)
            # Branch is already checked out during clone if specified

            return repo_path

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to clone repository: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _checkout_pr(self, repo_path: Path, pr_number: int) -> None:
        """
        Checkout a GitHub pull request.

        This fetches the PR branch and checks it out locally.

        Args:
            repo_path: Path to the cloned repository
            pr_number: GitHub PR number

        Raises:
            RuntimeError: If git operations fail
        """
        logger.info(f"Checking out PR #{pr_number}")

        try:
            # Fetch the PR branch
            # GitHub PRs are available as refs/pull/{number}/head
            fetch_cmd = [
                "git", "fetch", "origin",
                f"pull/{pr_number}/head:pr-{pr_number}"
            ]

            subprocess.run(
                fetch_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Checkout the PR branch
            checkout_cmd = ["git", "checkout", f"pr-{pr_number}"]
            subprocess.run(
                checkout_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Successfully checked out PR #{pr_number}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to checkout PR #{pr_number}: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _checkout_commit(self, repo_path: Path, commit: str) -> None:
        """
        Checkout a specific commit.

        Args:
            repo_path: Path to the cloned repository
            commit: Commit hash

        Raises:
            RuntimeError: If git operations fail
        """
        logger.info(f"Checking out commit: {commit}")

        try:
            checkout_cmd = ["git", "checkout", commit]
            subprocess.run(
                checkout_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Successfully checked out commit: {commit}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to checkout commit {commit}: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _extract_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from URL.

        Examples:
            https://github.com/user/repo.git -> repo
            https://github.com/user/repo -> repo
            git@github.com:user/repo.git -> repo

        Args:
            repo_url: Git repository URL

        Returns:
            Repository name
        """
        # Remove .git suffix if present
        url = repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]

        # Extract last part of the URL path
        repo_name = url.split("/")[-1]
        return repo_name

    async def install_dependencies(
        self,
        repo_path: Path,
        requirements_file: str = "requirements.txt",
        use_venv: bool = True
    ) -> Dict[str, Any]:
        """
        Install Python dependencies for the cloned repository.

        This method:
        1. Looks for requirements.txt (or specified file)
        2. Optionally creates a virtual environment
        3. Installs dependencies using pip

        Args:
            repo_path: Path to the cloned repository
            requirements_file: Name of requirements file (default: requirements.txt)
            use_venv: Whether to create and use a virtual environment

        Returns:
            Dictionary with installation results:
            - success: bool
            - venv_path: Path to venv if created
            - installed_packages: list of installed packages
            - errors: list of error messages if any

        """
        logger.info(f"Installing dependencies for {repo_path}")

        result = {
            "success": False,
            "venv_path": None,
            "installed_packages": [],
            "errors": []
        }

        requirements_path = repo_path / requirements_file

        if not requirements_path.exists():
            logger.warning(f"No {requirements_file} found in {repo_path}")
            result["errors"].append(f"No {requirements_file} found")
            # Not necessarily an error - some projects don't have requirements.txt
            result["success"] = True
            return result

        try:
            # Create virtual environment if requested
            if use_venv:
                venv_path = repo_path / ".venv"
                logger.debug(f"Creating virtual environment at {venv_path}")

                subprocess.run(
                    ["python", "-m", "venv", str(venv_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )

                # Get path to pip in the venv
                if os.name == "nt":  # Windows
                    pip_path = venv_path / "Scripts" / "pip"
                else:  # Unix-like
                    pip_path = venv_path / "bin" / "pip"

                result["venv_path"] = str(venv_path)
            else:
                # Use system pip
                pip_path = "pip"

            # Install requirements
            logger.info(f"Installing from {requirements_path}")
            install_result = subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse installed packages
            result["installed_packages"] = self._parse_pip_output(install_result.stdout)
            result["success"] = True

            logger.info(f"Dependencies installed successfully: {len(result['installed_packages'])} packages")

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install dependencies: {e.stderr}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def _parse_pip_output(self, output: str) -> list:
        """
        Parse pip install output to extract installed package names.

        Args:
            output: stdout from pip install command

        Returns:
            List of installed package names
        """
        packages = []
        for line in output.split("\n"):
            # Look for lines like "Successfully installed package-1.0.0"
            if "Successfully installed" in line:
                # Extract package names
                parts = line.split("Successfully installed")[1].strip().split()
                packages.extend([p.rsplit("-", 1)[0] for p in parts])

        return packages

    async def get_repo_info(self, repo_path: Path) -> Dict[str, Any]:
        """
        Get information about the cloned repository.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary with repo information:
            - current_branch: Current branch name
            - current_commit: Current commit hash
            - remote_url: Remote origin URL
            - commit_message: Latest commit message
        """
        logger.debug(f"Getting repo info for {repo_path}")

        info = {}

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            info["current_branch"] = branch_result.stdout.strip()

            # Get current commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            info["current_commit"] = commit_result.stdout.strip()

            # Get remote URL
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            info["remote_url"] = remote_result.stdout.strip()

            # Get latest commit message
            message_result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            info["commit_message"] = message_result.stdout.strip()

            logger.debug(f"Repo info: {info}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get repo info: {e.stderr}")

        return info

    def cleanup(self, repo_path: Path) -> bool:
        """
        Clean up a cloned repository.

        Args:
            repo_path: Path to the repository to remove

        Returns:
            True if cleanup successful, False otherwise
        """
        logger.info(f"Cleaning up repository: {repo_path}")

        try:
            if repo_path.exists():
                shutil.rmtree(repo_path)
                logger.info(f"Repository removed: {repo_path}")
                return True
            else:
                logger.warning(f"Repository path does not exist: {repo_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to cleanup repository: {e}")
            return False

    def cleanup_workspace(self) -> int:
        """
        Clean up entire workspace (all cloned repositories).

        Returns:
            Number of repositories removed
        """
        logger.info(f"Cleaning up entire workspace: {self.workspace_root}")

        count = 0
        if self.workspace_root.exists():
            for item in self.workspace_root.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    if self.cleanup(item):
                        count += 1

        logger.info(f"Cleaned up {count} repositories")
        return count


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
