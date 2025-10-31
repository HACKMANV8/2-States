"""
GitHub Service for PR Context Extraction.

Handles all GitHub API interactions including:
- PR metadata fetching
- Diff parsing
- Comments and review extraction
- Linked issues parsing
- CI/CD status checking
"""

import re
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from .github_retry import github_api_call, get_rate_limit_stats


class GitHubService:
    """
    Service for interacting with GitHub API to extract PR context.

    Supports both github.com and GitHub Enterprise.
    Uses Personal Access Token (PAT) for authentication.
    """

    def __init__(self, github_token: Optional[str] = None, api_base: str = "https://api.github.com"):
        """
        Initialize GitHub service.

        Args:
            github_token: GitHub Personal Access Token (falls back to GITHUB_TOKEN env var)
            api_base: GitHub API base URL (default: public GitHub)
        """
        self.token = github_token or os.environ.get("GITHUB_TOKEN")
        self.api_base = api_base.rstrip("/")

        if not self.token:
            print("⚠️  Warning: No GitHub token provided. API rate limits will be restrictive.")

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TestGPT-PR-Tester"
        }

        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def parse_pr_url(self, pr_url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub PR URL into components.

        Supports formats:
        - https://github.com/owner/repo/pull/123
        - https://github.company.com/owner/repo/pull/123
        - owner/repo#123

        Args:
            pr_url: GitHub PR URL or shorthand

        Returns:
            Dict with owner, repo, pr_number, or None if invalid
        """
        # Full URL pattern
        url_pattern = r'https?://(?:www\.)?([^/]+)/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(url_pattern, pr_url)

        if match:
            github_host = match.group(1)
            owner = match.group(2)
            repo = match.group(3)
            pr_number = match.group(4)

            # Update API base if enterprise GitHub
            if github_host != "github.com":
                self.api_base = f"https://{github_host}/api/v3"

            return {
                "owner": owner,
                "repo": repo,
                "pr_number": pr_number,
                "github_host": github_host
            }

        # Shorthand pattern: owner/repo#123
        shorthand_pattern = r'^([^/]+)/([^#]+)#(\d+)$'
        match = re.match(shorthand_pattern, pr_url)

        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2),
                "pr_number": match.group(3),
                "github_host": "github.com"
            }

        return None

    @github_api_call(max_retries=3)
    async def get_pr_metadata(self, owner: str, repo: str, pr_number: str) -> Dict[str, Any]:
        """
        Fetch PR metadata from GitHub API.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number

        Returns:
            Dict containing PR metadata
        """
        url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()

            pr_data = response.json()

            return {
                "title": pr_data["title"],
                "description": pr_data["body"] or "",
                "state": pr_data["state"],
                "author": pr_data["user"]["login"],
                "created_at": pr_data["created_at"],
                "updated_at": pr_data["updated_at"],
                "base_branch": pr_data["base"]["ref"],
                "head_branch": pr_data["head"]["ref"],
                "head_sha": pr_data["head"]["sha"],
                "base_sha": pr_data["base"]["sha"],
                "labels": [label["name"] for label in pr_data["labels"]],
                "mergeable": pr_data.get("mergeable"),
                "merged": pr_data["merged"],
                "draft": pr_data["draft"],
                "html_url": pr_data["html_url"],
                "commits_url": pr_data["commits_url"],
                "comments_url": pr_data["comments_url"],
                "review_comments_url": pr_data["review_comments_url"],
            }

    @github_api_call(max_retries=3)
    async def get_pr_diff(self, owner: str, repo: str, pr_number: str) -> Dict[str, Any]:
        """
        Fetch and parse PR diff.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number

        Returns:
            Dict containing parsed diff information
        """
        url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}"

        # Request diff format
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()

            diff_text = response.text

            # Parse diff to extract changed files
            changed_files = self._parse_diff(diff_text)

            return {
                "raw_diff": diff_text,
                "changed_files": changed_files,
                "files_changed_count": len(changed_files)
            }

    def _parse_diff(self, diff_text: str) -> List[Dict[str, Any]]:
        """
        Parse unified diff format to extract changed files and modifications.

        Args:
            diff_text: Raw diff text

        Returns:
            List of changed files with their modifications
        """
        changed_files = []
        current_file = None

        lines = diff_text.split("\n")

        for line in lines:
            # New file marker
            if line.startswith("diff --git"):
                if current_file:
                    changed_files.append(current_file)

                # Extract file path: diff --git a/path/to/file b/path/to/file
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[2][2:]  # Remove "a/" prefix
                    current_file = {
                        "path": file_path,
                        "additions": 0,
                        "deletions": 0,
                        "changes": []
                    }

            # Count additions/deletions
            elif current_file:
                if line.startswith("+") and not line.startswith("+++"):
                    current_file["additions"] += 1
                    current_file["changes"].append({"type": "addition", "line": line[1:]})
                elif line.startswith("-") and not line.startswith("---"):
                    current_file["deletions"] += 1
                    current_file["changes"].append({"type": "deletion", "line": line[1:]})

        # Add last file
        if current_file:
            changed_files.append(current_file)

        return changed_files

    @github_api_call(max_retries=3)
    async def get_pr_files(self, owner: str, repo: str, pr_number: str) -> List[Dict[str, Any]]:
        """
        Get list of files changed in PR (using GitHub API for structured data).

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number

        Returns:
            List of changed files with metadata
        """
        url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/files"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()

            files_data = response.json()

            return [
                {
                    "filename": file["filename"],
                    "status": file["status"],  # added, removed, modified, renamed
                    "additions": file["additions"],
                    "deletions": file["deletions"],
                    "changes": file["changes"],
                    "patch": file.get("patch", ""),
                }
                for file in files_data
            ]

    async def get_pr_comments(self, owner: str, repo: str, pr_number: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get PR comments and review comments.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number

        Returns:
            Dict with issue_comments and review_comments
        """
        # Issue comments (general PR comments)
        issue_comments_url = f"{self.api_base}/repos/{owner}/{repo}/issues/{pr_number}/comments"

        # Review comments (inline code comments)
        review_comments_url = f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/comments"

        async with httpx.AsyncClient() as client:
            # Fetch both types of comments
            issue_response = await client.get(issue_comments_url, headers=self.headers, timeout=30.0)
            review_response = await client.get(review_comments_url, headers=self.headers, timeout=30.0)

            issue_response.raise_for_status()
            review_response.raise_for_status()

            issue_comments = [
                {
                    "author": comment["user"]["login"],
                    "body": comment["body"],
                    "created_at": comment["created_at"],
                    "type": "issue_comment"
                }
                for comment in issue_response.json()
            ]

            review_comments = [
                {
                    "author": comment["user"]["login"],
                    "body": comment["body"],
                    "path": comment["path"],
                    "line": comment.get("line"),
                    "created_at": comment["created_at"],
                    "type": "review_comment"
                }
                for comment in review_response.json()
            ]

            return {
                "issue_comments": issue_comments,
                "review_comments": review_comments,
                "total_comments": len(issue_comments) + len(review_comments)
            }

    async def get_linked_issues(self, owner: str, repo: str, pr_description: str) -> List[Dict[str, Any]]:
        """
        Extract and fetch linked issues from PR description.

        Looks for patterns like: Closes #123, Fixes #456

        Args:
            owner: Repository owner
            repo: Repository name
            pr_description: PR description text

        Returns:
            List of linked issues with their data
        """
        # Pattern to match issue references
        issue_pattern = r'(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)'
        issue_numbers = re.findall(issue_pattern, pr_description, re.IGNORECASE)

        linked_issues = []

        async with httpx.AsyncClient() as client:
            for issue_num in issue_numbers:
                try:
                    url = f"{self.api_base}/repos/{owner}/{repo}/issues/{issue_num}"
                    response = await client.get(url, headers=self.headers, timeout=30.0)
                    response.raise_for_status()

                    issue_data = response.json()

                    linked_issues.append({
                        "number": issue_num,
                        "title": issue_data["title"],
                        "body": issue_data["body"],
                        "labels": [label["name"] for label in issue_data["labels"]],
                        "state": issue_data["state"],
                    })
                except Exception as e:
                    print(f"⚠️  Could not fetch issue #{issue_num}: {e}")

        return linked_issues

    async def get_ci_status(self, owner: str, repo: str, head_sha: str) -> Dict[str, Any]:
        """
        Get CI/CD status for the PR head commit.

        Args:
            owner: Repository owner
            repo: Repository name
            head_sha: Head commit SHA

        Returns:
            Dict with CI status information
        """
        url = f"{self.api_base}/repos/{owner}/{repo}/commits/{head_sha}/status"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()

            status_data = response.json()

            return {
                "state": status_data["state"],  # pending, success, failure, error
                "total_count": status_data["total_count"],
                "statuses": [
                    {
                        "context": status["context"],
                        "state": status["state"],
                        "description": status.get("description", ""),
                        "target_url": status.get("target_url", ""),
                    }
                    for status in status_data["statuses"]
                ],
            }

    @github_api_call(max_retries=2)  # Less retries for writes
    async def post_pr_comment(self, owner: str, repo: str, pr_number: str, comment_body: str) -> Dict[str, Any]:
        """
        Post a comment on the PR.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            comment_body: Comment text (supports Markdown)

        Returns:
            Dict with posted comment data
        """
        url = f"{self.api_base}/repos/{owner}/{repo}/issues/{pr_number}/comments"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"body": comment_body},
                timeout=30.0
            )
            response.raise_for_status()

            comment_data = response.json()

            return {
                "comment_id": comment_data["id"],
                "html_url": comment_data["html_url"],
                "created_at": comment_data["created_at"],
            }

    async def get_full_pr_context(self, pr_url: str) -> Dict[str, Any]:
        """
        Get complete PR context in one call.

        This is the main entry point that fetches everything needed for testing.

        Args:
            pr_url: GitHub PR URL

        Returns:
            Complete PR context including metadata, diff, comments, etc.
        """
        print(f"\n🔍 Fetching PR context from GitHub...")

        # Parse PR URL
        pr_info = self.parse_pr_url(pr_url)
        if not pr_info:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")

        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_number = pr_info["pr_number"]

        print(f"   Repository: {owner}/{repo}")
        print(f"   PR Number: #{pr_number}")

        # Fetch all PR data
        metadata = await self.get_pr_metadata(owner, repo, pr_number)
        files = await self.get_pr_files(owner, repo, pr_number)
        comments = await self.get_pr_comments(owner, repo, pr_number)
        linked_issues = await self.get_linked_issues(owner, repo, metadata["description"])

        # Try to get CI status
        try:
            ci_status = await self.get_ci_status(owner, repo, metadata["head_sha"])
        except Exception as e:
            print(f"   ℹ️  Could not fetch CI status: {e}")
            ci_status = {"state": "unknown", "statuses": []}

        print(f"   ✅ Fetched PR context")
        print(f"      Title: {metadata['title']}")
        print(f"      Author: {metadata['author']}")
        print(f"      Files changed: {len(files)}")
        print(f"      Comments: {comments['total_comments']}")
        print(f"      Linked issues: {len(linked_issues)}")

        return {
            "pr_info": pr_info,
            "metadata": metadata,
            "files": files,
            "comments": comments,
            "linked_issues": linked_issues,
            "ci_status": ci_status,
        }
