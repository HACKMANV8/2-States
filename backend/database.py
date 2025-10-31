"""
Database configuration for TestGPT backend.

Uses SQLAlchemy with SQLite, shared with Next.js frontend via the same database file.
"""

from sqlalchemy import create_engine, MetaData, Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database path - shared with frontend
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "lib", "db", "testgpt.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class TestSuite(Base):
    """Stored test suite (reusable test scenario)"""
    __tablename__ = "test_suites"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    prompt = Column(Text, nullable=False)  # Original prompt that generated the test
    target_url = Column(String, nullable=False)

    # Test definition (JSON)
    test_steps = Column(JSON)  # List of test steps (Playwright actions/assertions)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime)
    created_by = Column(String)  # Slack user/GitHub PR
    source_type = Column(String)  # slack_trigger, github_pr, manual
    tags = Column(JSON)  # Array of tags

    # Relationships
    executions = relationship("TestExecution", back_populates="test_suite")


class ConfigurationTemplate(Base):
    """Reusable configuration templates for test execution"""
    __tablename__ = "configuration_templates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # Browser configuration
    browsers = Column(JSON)  # Array: ["chrome", "firefox", "safari", "edge"]

    # Viewport configuration
    viewports = Column(JSON)  # Array of viewport configs: [{"width": 1920, "height": 1080, "device_name": "desktop"}]

    # Network configuration
    network_modes = Column(JSON)  # Array: ["online", "fast3g", "slow3g", "offline"]

    # User agent strings (for mobile simulation)
    user_agent_strings = Column(JSON)

    # Additional settings
    screenshot_on_failure = Column(Boolean, default=True)
    video_recording = Column(Boolean, default=False)
    parallel_execution = Column(Boolean, default=True)
    max_workers = Column(Integer, default=4)
    default_timeout = Column(Integer, default=30000)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("TestExecution", back_populates="config")


class TestExecution(Base):
    """Test execution record"""
    __tablename__ = "test_executions_v2"  # v2 to avoid conflicts with frontend schema

    id = Column(String, primary_key=True)
    test_suite_id = Column(String, ForeignKey("test_suites.id"), nullable=True)
    config_id = Column(String, ForeignKey("configuration_templates.id"), nullable=True)

    # Execution status
    status = Column(String, nullable=False, default="pending")  # pending, running, passed, failed

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    # Results
    execution_logs = Column(JSON)  # Detailed logs
    screenshots = Column(JSON)  # Array of screenshot URLs/paths
    video_url = Column(String)
    error_details = Column(Text)

    # Environment
    browser = Column(String)
    viewport_width = Column(Integer)
    viewport_height = Column(Integer)
    network_mode = Column(String)

    # Trigger information
    triggered_by = Column(String)  # slack, manual, github
    triggered_by_user = Column(String)

    # Slack integration
    slack_channel_id = Column(String)
    slack_message_ts = Column(String)
    slack_workspace = Column(String)

    # GitHub integration
    github_repo_url = Column(String)
    github_pr_number = Column(Integer)
    github_pr_title = Column(String)
    github_commit_sha = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_suite = relationship("TestSuite", back_populates="executions")
    config = relationship("ConfigurationTemplate", back_populates="executions")


class ExecutionStep(Base):
    """Individual step result within a test execution"""
    __tablename__ = "execution_steps"

    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey("test_executions_v2.id"), nullable=False)

    step_number = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    target = Column(String)
    expected_outcome = Column(String)
    actual_outcome = Column(String)
    passed = Column(Boolean, nullable=False)

    error_message = Column(Text)
    duration_ms = Column(Integer)
    screenshot_url = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class PRTestRun(Base):
    """PR-based test run record"""
    __tablename__ = "pr_test_runs"

    id = Column(String, primary_key=True)

    # PR Information
    pr_url = Column(String, nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=False)
    pr_author = Column(String)
    repo_owner = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    base_branch = Column(String)
    head_branch = Column(String)
    head_sha = Column(String)

    # PR Context
    pr_description = Column(Text)
    files_changed_count = Column(Integer)
    changed_files = Column(JSON)  # List of file paths
    acceptance_criteria = Column(JSON)  # List of criteria
    linked_issues = Column(JSON)  # List of linked issue numbers

    # Deployment Information
    deployment_url = Column(String)
    deployment_platform = Column(String)  # vercel, netlify, etc.
    deployment_accessible = Column(Boolean)
    deployment_response_time_ms = Column(Integer)

    # Codebase Analysis
    project_type = Column(String)  # frontend, backend, fullstack
    tech_stack = Column(JSON)  # Array of technologies
    framework_detected = Column(String)

    # Test Context
    test_scenarios_generated = Column(JSON)  # List of scenarios
    scenario_count = Column(Integer)

    # Test Execution
    status = Column(String, nullable=False)  # pending, running, passed, failed, error
    overall_pass = Column(Boolean)
    scenarios_passed = Column(Integer)
    scenarios_failed = Column(Integer)
    scenarios_total = Column(Integer)

    # Results
    test_results = Column(JSON)  # Full test results object
    failures = Column(JSON)  # List of failure details
    console_errors = Column(JSON)  # Console errors captured
    screenshots = Column(JSON)  # Screenshot paths
    agent_response = Column(Text)  # Full agent response

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)

    # GitHub Integration
    github_comment_posted = Column(Boolean, default=False)
    github_comment_url = Column(String)
    github_comment_id = Column(String)

    # Slack Integration
    slack_message_posted = Column(Boolean, default=False)
    slack_channel_id = Column(String)
    slack_message_ts = Column(String)

    # Trigger Information
    triggered_by = Column(String)  # slack, github_webhook, manual
    triggered_by_user = Column(String)
    custom_instructions = Column(Text)

    # Metrics
    github_api_calls = Column(Integer)
    total_processing_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PRTestMetrics(Base):
    """Aggregated metrics for PR testing"""
    __tablename__ = "pr_test_metrics"

    id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)

    # Daily aggregates
    total_pr_tests = Column(Integer, default=0)
    total_passed = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)

    # Timing metrics
    avg_execution_time_ms = Column(Integer)
    avg_github_fetch_time_ms = Column(Integer)
    avg_deployment_validation_time_ms = Column(Integer)

    # Deployment metrics
    deployments_found = Column(Integer, default=0)
    deployments_accessible = Column(Integer, default=0)
    deployment_platforms = Column(JSON)  # Count by platform

    # Framework metrics
    frameworks_detected = Column(JSON)  # Count by framework

    # Success rates by type
    frontend_success_rate = Column(Float)
    backend_success_rate = Column(Float)
    fullstack_success_rate = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DB_PATH}")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
