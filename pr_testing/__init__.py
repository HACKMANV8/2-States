"""
PR-Based Context Testing System for TestGPT.

This module provides comprehensive PR testing capabilities including:
- GitHub PR context extraction
- Deployment URL detection
- Codebase analysis
- Automated test generation from PR changes
- Results posting to GitHub and Slack
"""

from .github_service import GitHubService
from .deployment_detector import DeploymentDetector
from .codebase_analyzer import CodebaseAnalyzer
from .context_builder import PRContextBuilder
from .pr_orchestrator import PRTestOrchestrator

__all__ = [
    'GitHubService',
    'DeploymentDetector',
    'CodebaseAnalyzer',
    'PRContextBuilder',
    'PRTestOrchestrator',
]
