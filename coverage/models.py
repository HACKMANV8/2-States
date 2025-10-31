"""
Data models for TestGPT coverage system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class CoverageStatus(str, Enum):
    """Coverage run status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class StopReason(str, Enum):
    """Reasons for stopping test execution."""
    THRESHOLD_MET = "threshold_met"  # Coverage thresholds satisfied
    PLATEAU_REACHED = "plateau"  # No improvement in N tests
    TIME_LIMIT = "time_limit"  # Time budget exhausted
    MCDC_SATISFIED = "mcdc_satisfied"  # MCDC criteria met
    MANUAL = "manual"  # User requested stop
    ERROR = "error"  # Error occurred


class GapType(str, Enum):
    """Types of coverage gaps."""
    UNCOVERED_LINES = "uncovered_lines"
    UNCOVERED_BRANCH = "uncovered_branch"
    UNCOVERED_CONDITION = "uncovered_condition"
    UNCOVERED_PATH = "uncovered_path"
    PARTIAL_MCDC = "partial_mcdc"


class GapPriority(str, Enum):
    """Coverage gap priority levels."""
    CRITICAL = "critical"  # Must be covered (security, payment, auth)
    HIGH = "high"  # Should be covered (business logic)
    MEDIUM = "medium"  # Nice to cover (utility functions)
    LOW = "low"  # Optional (error messages, logging)


@dataclass
class CoverageRun:
    """A coverage collection run for a PR or test execution."""
    run_id: str
    pr_id: Optional[str] = None
    pr_url: Optional[str] = None
    repo_url: Optional[str] = None
    branch_name: Optional[str] = None
    commit_sha: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: CoverageStatus = CoverageStatus.RUNNING
    stop_reason: Optional[StopReason] = None

    # Aggregate metrics
    overall_coverage_percent: float = 0.0
    changed_lines_covered: int = 0
    changed_lines_total: int = 0
    branches_covered: int = 0
    branches_total: int = 0
    mcdc_satisfied: bool = False
    test_count: int = 0

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'run_id': self.run_id,
            'pr_id': self.pr_id,
            'pr_url': self.pr_url,
            'repo_url': self.repo_url,
            'branch_name': self.branch_name,
            'commit_sha': self.commit_sha,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status.value,
            'stop_reason': self.stop_reason.value if self.stop_reason else None,
            'overall_coverage_percent': self.overall_coverage_percent,
            'changed_lines_covered': self.changed_lines_covered,
            'changed_lines_total': self.changed_lines_total,
            'branches_covered': self.branches_covered,
            'branches_total': self.branches_total,
            'mcdc_satisfied': self.mcdc_satisfied,
            'test_count': self.test_count,
            'config_json': self.config
        }


@dataclass
class CoverageData:
    """Line-level coverage data."""
    run_id: str
    file_path: str
    line_number: int
    hit_count: int = 0
    branch_id: Optional[str] = None
    branch_taken: Optional[bool] = None
    test_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'run_id': self.run_id,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'hit_count': self.hit_count,
            'branch_id': self.branch_id,
            'branch_taken': self.branch_taken,
            'test_id': self.test_id,
            'timestamp': self.timestamp
        }


@dataclass
class MCDCAnalysis:
    """MCDC (Modified Condition/Decision Coverage) analysis for a condition."""
    run_id: str
    file_path: str
    line_number: int
    condition_id: str
    condition_text: str
    truth_table: List[Dict[str, Any]]
    required_tests: List[Dict[str, Any]]
    completed_tests: List[Dict[str, Any]]
    satisfaction_percent: float = 0.0
    is_satisfied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        import json
        return {
            'run_id': self.run_id,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'condition_id': self.condition_id,
            'condition_text': self.condition_text,
            'truth_table_json': json.dumps(self.truth_table),
            'required_tests_json': json.dumps(self.required_tests),
            'completed_tests_json': json.dumps(self.completed_tests),
            'satisfaction_percent': self.satisfaction_percent,
            'is_satisfied': self.is_satisfied
        }


@dataclass
class StopDecision:
    """A decision about whether to stop testing."""
    run_id: str
    decision_time: datetime = field(default_factory=datetime.now)
    should_stop: bool = False
    reason: str = ""
    confidence_score: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        import json
        return {
            'run_id': self.run_id,
            'decision_time': self.decision_time,
            'should_stop': self.should_stop,
            'reason': self.reason,
            'confidence_score': self.confidence_score,
            'metrics_json': json.dumps(self.metrics)
        }


@dataclass
class CoverageGap:
    """An identified gap in code coverage."""
    run_id: str
    file_path: str
    line_start: int
    line_end: int
    gap_type: GapType
    priority: GapPriority
    suggested_test: Optional[str] = None
    risk_score: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        import json
        return {
            'run_id': self.run_id,
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'gap_type': self.gap_type.value,
            'priority': self.priority.value,
            'suggested_test': self.suggested_test,
            'risk_score': self.risk_score,
            'context_json': json.dumps(self.context)
        }


@dataclass
class CoverageReport:
    """A generated coverage report."""
    report_id: str
    run_id: str
    report_type: str  # html, json, summary
    report_url: Optional[str] = None
    report_data: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        import json
        return {
            'report_id': self.report_id,
            'run_id': self.run_id,
            'report_type': self.report_type,
            'report_url': self.report_url,
            'report_data': self.report_data,
            'generated_at': self.generated_at,
            'metrics_json': json.dumps(self.metrics)
        }


@dataclass
class TestEffectiveness:
    """Measures how effective a single test was at increasing coverage."""
    run_id: str
    test_id: str
    test_name: str
    coverage_delta_lines: int = 0
    coverage_delta_branches: int = 0
    unique_coverage_lines: int = 0
    execution_time_ms: int = 0
    effectiveness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'run_id': self.run_id,
            'test_id': self.test_id,
            'test_name': self.test_name,
            'coverage_delta_lines': self.coverage_delta_lines,
            'coverage_delta_branches': self.coverage_delta_branches,
            'unique_coverage_lines': self.unique_coverage_lines,
            'execution_time_ms': self.execution_time_ms,
            'effectiveness_score': self.effectiveness_score
        }


@dataclass
class InstrumentedFile:
    """Represents a file that has been instrumented for coverage."""
    file_path: str
    original_content: str
    instrumented_content: str
    source_map: Dict[int, int]  # Instrumented line -> Original line
    is_changed: bool = False  # Whether file was changed in PR
    language: str = "unknown"  # js, ts, python, etc.


@dataclass
class CodePath:
    """Represents a code execution path."""
    path_id: str
    file_path: str
    start_line: int
    end_line: int
    conditions: List[str]
    is_covered: bool = False
    is_critical: bool = False
    complexity_score: int = 0
