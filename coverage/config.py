"""
Configuration for TestGPT coverage system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CoverageConfig:
    """Configuration for coverage collection and analysis."""

    # Coverage thresholds
    changed_lines_threshold: float = 80.0  # % of changed lines to cover
    new_lines_threshold: float = 100.0  # % of new lines to cover
    branches_threshold: float = 100.0  # % of new branches to cover
    mcdc_required: bool = True  # Whether MCDC must be satisfied

    # Stop conditions
    plateau_test_count: int = 5  # Stop if no improvement in N tests
    time_limit_minutes: int = 60  # Maximum time for coverage collection
    min_coverage_percent: float = 80.0  # Minimum acceptable coverage
    max_tests: int = 100  # Maximum number of tests to run

    # File patterns
    critical_file_patterns: List[str] = field(default_factory=lambda: [
        "*/auth/*",
        "*/payment/*",
        "*/security/*",
        "*/authentication/*"
    ])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*/tests/*",
        "*/test/*",
        "*/__tests__/*",
        "*/migrations/*",
        "*/__pycache__/*",
        "*/node_modules/*",
        "*/venv/*",
        "*.test.js",
        "*.test.ts",
        "*.spec.js",
        "*.spec.ts",
        "*_test.py",
        "*_test.go"
    ])

    # Instrumentation settings
    enable_js_instrumentation: bool = True
    enable_ts_instrumentation: bool = True
    enable_python_instrumentation: bool = True
    enable_go_instrumentation: bool = False

    # MCDC settings
    mcdc_max_conditions: int = 8  # Max conditions in single expression
    mcdc_timeout_seconds: int = 30  # Timeout for MCDC analysis

    # Reporting settings
    generate_html_report: bool = True
    generate_json_report: bool = True
    report_directory: str = "./coverage_reports"

    # Performance settings
    streaming_mode: bool = True  # Stream coverage data for large codebases
    parallel_instrumentation: bool = True
    max_file_size_mb: int = 10  # Skip files larger than this

    # Integration settings
    integrate_with_playwright: bool = True
    integrate_with_mcp: bool = True
    track_network_requests: bool = True

    def is_file_excluded(self, file_path: str) -> bool:
        """Check if file should be excluded from coverage."""
        import fnmatch
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def is_file_critical(self, file_path: str) -> bool:
        """Check if file is critical (requires higher coverage)."""
        import fnmatch
        for pattern in self.critical_file_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def get_file_threshold(self, file_path: str) -> float:
        """Get coverage threshold for specific file."""
        if self.is_file_critical(file_path):
            return 100.0  # Critical files need 100% coverage
        return self.changed_lines_threshold

    @classmethod
    def default(cls) -> 'CoverageConfig':
        """Get default configuration."""
        return cls()

    @classmethod
    def strict(cls) -> 'CoverageConfig':
        """Get strict configuration (high thresholds)."""
        return cls(
            changed_lines_threshold=100.0,
            new_lines_threshold=100.0,
            branches_threshold=100.0,
            mcdc_required=True,
            min_coverage_percent=100.0
        )

    @classmethod
    def permissive(cls) -> 'CoverageConfig':
        """Get permissive configuration (low thresholds)."""
        return cls(
            changed_lines_threshold=50.0,
            new_lines_threshold=70.0,
            branches_threshold=70.0,
            mcdc_required=False,
            min_coverage_percent=50.0
        )

    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return {
            'changed_lines_threshold': self.changed_lines_threshold,
            'new_lines_threshold': self.new_lines_threshold,
            'branches_threshold': self.branches_threshold,
            'mcdc_required': self.mcdc_required,
            'plateau_test_count': self.plateau_test_count,
            'time_limit_minutes': self.time_limit_minutes,
            'min_coverage_percent': self.min_coverage_percent,
            'max_tests': self.max_tests,
            'critical_file_patterns': self.critical_file_patterns,
            'exclude_patterns': self.exclude_patterns,
            'enable_js_instrumentation': self.enable_js_instrumentation,
            'enable_ts_instrumentation': self.enable_ts_instrumentation,
            'enable_python_instrumentation': self.enable_python_instrumentation,
            'enable_go_instrumentation': self.enable_go_instrumentation,
            'mcdc_max_conditions': self.mcdc_max_conditions,
            'mcdc_timeout_seconds': self.mcdc_timeout_seconds,
            'generate_html_report': self.generate_html_report,
            'generate_json_report': self.generate_json_report,
            'report_directory': self.report_directory,
            'streaming_mode': self.streaming_mode,
            'parallel_instrumentation': self.parallel_instrumentation,
            'max_file_size_mb': self.max_file_size_mb,
            'integrate_with_playwright': self.integrate_with_playwright,
            'integrate_with_mcp': self.integrate_with_mcp,
            'track_network_requests': self.track_network_requests
        }
