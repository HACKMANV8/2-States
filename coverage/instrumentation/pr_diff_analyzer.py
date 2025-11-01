"""
PR Diff Analyzer - Identifies changed code blocks requiring coverage.

Integrates with TestGPT's pr_testing/github_service.py to analyze:
- Modified functions/methods
- New functions/methods
- Changed conditional statements
- Modified loops
- Changed API endpoints
- Modified React/Vue components
"""

import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeChange:
    """Represents a code change from a PR."""
    file_path: str
    change_type: str  # added, modified, deleted
    line_start: int
    line_end: int
    old_code: Optional[str] = None
    new_code: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    is_test_file: bool = False
    complexity_score: int = 1
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ChangedFunction:
    """A function that was changed in the PR."""
    file_path: str
    function_name: str
    line_start: int
    line_end: int
    change_type: str  # added, modified, deleted
    callers: List[str] = field(default_factory=list)
    callees: List[str] = field(default_factory=list)
    complexity: int = 1
    is_critical: bool = False


@dataclass
class PRDiffSummary:
    """Summary of all changes in a PR."""
    pr_number: int
    pr_url: str
    changed_files: List[str]
    code_changes: List[CodeChange]
    changed_functions: List[ChangedFunction]
    total_lines_added: int
    total_lines_deleted: int
    total_lines_modified: int
    critical_changes: List[CodeChange]


class PRDiffAnalyzer:
    """
    Analyzes PR diffs to identify code requiring coverage.

    Integrates with TestGPT's GitHub service to fetch and analyze PRs.
    """

    def __init__(self):
        """Initialize PR diff analyzer."""
        self.github_service = None  # Will be initialized lazily

        # Critical path patterns
        self.critical_patterns = [
            r'auth',
            r'authentication',
            r'security',
            r'payment',
            r'billing',
            r'password',
            r'token',
            r'credential',
            r'encrypt',
            r'decrypt'
        ]

    async def analyze_pr(
        self,
        pr_url: str,
        github_token: Optional[str] = None
    ) -> PRDiffSummary:
        """
        Analyze a GitHub PR to identify changed code.

        Args:
            pr_url: GitHub PR URL
            github_token: Optional GitHub token for private repos

        Returns:
            PRDiffSummary with all changes
        """
        print(f" Analyzing PR: {pr_url}")

        # Extract PR info
        pr_number = self._extract_pr_number(pr_url)
        if not pr_number:
            raise ValueError(f"Invalid PR URL: {pr_url}")

        # Initialize GitHub service if needed
        if not self.github_service:
            await self._init_github_service(github_token)

        # Fetch PR data
        pr_data = await self._fetch_pr_data(pr_url)

        # Parse changed files
        changed_files = self._parse_changed_files(pr_data)
        print(f"   Found {len(changed_files)} changed files")

        # Analyze each file's changes
        code_changes = []
        changed_functions = []
        total_added = 0
        total_deleted = 0
        total_modified = 0

        for file_path, file_changes in changed_files.items():
            # Skip test files
            if self._is_test_file(file_path):
                continue

            # Parse changes in this file
            changes = self._parse_file_changes(file_path, file_changes)
            code_changes.extend(changes)

            # Extract function-level changes
            functions = self._extract_changed_functions(file_path, changes)
            changed_functions.extend(functions)

            # Count lines
            for change in changes:
                if change.change_type == "added":
                    total_added += (change.line_end - change.line_start + 1)
                elif change.change_type == "deleted":
                    total_deleted += (change.line_end - change.line_start + 1)
                else:
                    total_modified += (change.line_end - change.line_start + 1)

        # Identify critical changes
        critical_changes = [
            change for change in code_changes
            if self._is_critical_change(change)
        ]

        print(f"    Analysis complete:")
        print(f"      Lines added: {total_added}")
        print(f"      Lines deleted: {total_deleted}")
        print(f"      Lines modified: {total_modified}")
        print(f"      Functions changed: {len(changed_functions)}")
        print(f"      Critical changes: {len(critical_changes)}")

        return PRDiffSummary(
            pr_number=pr_number,
            pr_url=pr_url,
            changed_files=list(changed_files.keys()),
            code_changes=code_changes,
            changed_functions=changed_functions,
            total_lines_added=total_added,
            total_lines_deleted=total_deleted,
            total_lines_modified=total_modified,
            critical_changes=critical_changes
        )

    def identify_dependent_code(
        self,
        changed_functions: List[ChangedFunction],
        codebase_path: Path
    ) -> List[str]:
        """
        Identify code that depends on changed functions.

        Args:
            changed_functions: Functions that were changed
            codebase_path: Path to codebase root

        Returns:
            List of file paths containing dependent code
        """
        print(f" Identifying dependent code...")

        dependent_files = set()

        for func in changed_functions:
            # Find files that import or call this function
            callers = self._find_callers(func, codebase_path)
            dependent_files.update(callers)

        print(f"   Found {len(dependent_files)} files with dependencies")

        return list(dependent_files)

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    async def _init_github_service(self, github_token: Optional[str]):
        """Initialize GitHub service."""
        try:
            # Import TestGPT's GitHub service
            from pr_testing.github_service import GitHubService
            self.github_service = GitHubService(github_token)
            print("    GitHub service initialized")
        except ImportError:
            print("     GitHub service not available, using fallback")
            self.github_service = None

    async def _fetch_pr_data(self, pr_url: str) -> Dict:
        """Fetch PR data from GitHub."""
        if self.github_service:
            # Use TestGPT's GitHub service
            return await self.github_service.fetch_pr_context(pr_url)
        else:
            # Fallback: simulate PR data
            return {
                'files': [],
                'diff': '',
                'additions': 0,
                'deletions': 0
            }

    def _extract_pr_number(self, pr_url: str) -> Optional[int]:
        """Extract PR number from URL."""
        match = re.search(r'/pull/(\d+)', pr_url)
        if match:
            return int(match.group(1))
        return None

    def _parse_changed_files(self, pr_data: Dict) -> Dict[str, str]:
        """Parse changed files from PR data."""
        changed_files = {}

        # Extract from GitHub API response
        if 'files' in pr_data:
            for file_info in pr_data['files']:
                file_path = file_info.get('filename', '')
                patch = file_info.get('patch', '')
                changed_files[file_path] = patch

        return changed_files

    def _parse_file_changes(
        self,
        file_path: str,
        patch: str
    ) -> List[CodeChange]:
        """Parse individual changes from file patch."""
        changes = []

        # Parse unified diff format
        lines = patch.split('\n')
        current_line = 0
        change_start = None
        change_lines = []
        change_type = None

        for line in lines:
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            if line.startswith('@@'):
                match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_line = int(match.group(2))
                continue

            # Addition
            if line.startswith('+') and not line.startswith('+++'):
                if change_type != 'added':
                    if change_start is not None:
                        changes.append(self._create_code_change(
                            file_path, change_type, change_start,
                            current_line - 1, change_lines
                        ))
                    change_start = current_line
                    change_lines = []
                    change_type = 'added'
                change_lines.append(line[1:])
                current_line += 1

            # Deletion
            elif line.startswith('-') and not line.startswith('---'):
                if change_type != 'deleted':
                    if change_start is not None:
                        changes.append(self._create_code_change(
                            file_path, change_type, change_start,
                            current_line - 1, change_lines
                        ))
                    change_start = current_line
                    change_lines = []
                    change_type = 'deleted'
                change_lines.append(line[1:])
                # Don't increment current_line for deletions

            # Context line
            else:
                if change_start is not None:
                    changes.append(self._create_code_change(
                        file_path, change_type, change_start,
                        current_line - 1, change_lines
                    ))
                    change_start = None
                    change_lines = []
                    change_type = None
                current_line += 1

        # Handle remaining change
        if change_start is not None:
            changes.append(self._create_code_change(
                file_path, change_type, change_start,
                current_line - 1, change_lines
            ))

        return changes

    def _create_code_change(
        self,
        file_path: str,
        change_type: str,
        line_start: int,
        line_end: int,
        lines: List[str]
    ) -> CodeChange:
        """Create CodeChange object from parsed data."""
        code = '\n'.join(lines)

        # Extract function/class names if possible
        function_name = self._extract_function_name(code)
        class_name = self._extract_class_name(code)

        # Calculate complexity
        complexity = self._calculate_complexity(code)

        return CodeChange(
            file_path=file_path,
            change_type=change_type,
            line_start=line_start,
            line_end=line_end,
            new_code=code if change_type == 'added' else None,
            old_code=code if change_type == 'deleted' else None,
            function_name=function_name,
            class_name=class_name,
            complexity_score=complexity
        )

    def _extract_changed_functions(
        self,
        file_path: str,
        changes: List[CodeChange]
    ) -> List[ChangedFunction]:
        """Extract function-level changes."""
        functions = []

        for change in changes:
            if change.function_name:
                # Check if function already tracked
                existing = next(
                    (f for f in functions if f.function_name == change.function_name),
                    None
                )

                if existing:
                    # Update existing function
                    existing.line_end = max(existing.line_end, change.line_end)
                else:
                    # Create new function entry
                    functions.append(ChangedFunction(
                        file_path=file_path,
                        function_name=change.function_name,
                        line_start=change.line_start,
                        line_end=change.line_end,
                        change_type=change.change_type,
                        complexity=change.complexity_score,
                        is_critical=self._is_critical_function(change.function_name)
                    ))

        return functions

    def _extract_function_name(self, code: str) -> Optional[str]:
        """Extract function name from code."""
        # Python function
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)

        # JavaScript/TypeScript function
        match = re.search(r'function\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)

        # Arrow function with name
        match = re.search(r'const\s+(\w+)\s*=\s*\(.*\)\s*=>', code)
        if match:
            return match.group(1)

        return None

    def _extract_class_name(self, code: str) -> Optional[str]:
        """Extract class name from code."""
        # Python/JavaScript class
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)

        return None

    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity score."""
        complexity = 1  # Base complexity

        # Count decision points
        complexity += code.count('if ')
        complexity += code.count('elif ')
        complexity += code.count('else if ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('case ')
        complexity += code.count('catch ')
        complexity += code.count('&&')
        complexity += code.count('||')
        complexity += code.count('?')  # Ternary operator

        return complexity

    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        test_patterns = [
            'test', 'spec', '__tests__', '_test', '.test.', '.spec.'
        ]
        return any(pattern in file_path.lower() for pattern in test_patterns)

    def _is_critical_change(self, change: CodeChange) -> bool:
        """Check if change is critical (requires high coverage)."""
        # Check file path
        for pattern in self.critical_patterns:
            if re.search(pattern, change.file_path, re.IGNORECASE):
                return True

        # Check function name
        if change.function_name:
            for pattern in self.critical_patterns:
                if re.search(pattern, change.function_name, re.IGNORECASE):
                    return True

        # Check code content
        if change.new_code:
            for pattern in self.critical_patterns:
                if re.search(pattern, change.new_code, re.IGNORECASE):
                    return True

        return False

    def _is_critical_function(self, function_name: str) -> bool:
        """Check if function is critical."""
        for pattern in self.critical_patterns:
            if re.search(pattern, function_name, re.IGNORECASE):
                return True
        return False

    def _find_callers(
        self,
        func: ChangedFunction,
        codebase_path: Path
    ) -> Set[str]:
        """Find files that call this function."""
        callers = set()

        # TODO: Implement AST-based call graph analysis
        # For now, use simple grep-like search

        try:
            import subprocess
            result = subprocess.run(
                ['grep', '-r', '-l', func.function_name, str(codebase_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line and not self._is_test_file(line):
                        callers.add(line)

        except Exception as e:
            print(f"     Error finding callers: {e}")

        return callers
