"""
Database models and operations for TestGPT coverage system.

Integrates with existing TestGPT database (SQLAlchemy + SQLite).
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List

Base = declarative_base()


class CoverageRunDB(Base):
    """Database model for coverage runs."""
    __tablename__ = 'coverage_runs'

    run_id = Column(String, primary_key=True)
    pr_id = Column(String, nullable=True)
    pr_url = Column(String, nullable=True)
    repo_url = Column(String, nullable=True)
    branch_name = Column(String, nullable=True)
    commit_sha = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default='running')
    stop_reason = Column(String, nullable=True)

    # Aggregate metrics
    overall_coverage_percent = Column(Float, default=0.0)
    changed_lines_covered = Column(Integer, default=0)
    changed_lines_total = Column(Integer, default=0)
    branches_covered = Column(Integer, default=0)
    branches_total = Column(Integer, default=0)
    mcdc_satisfied = Column(Boolean, default=False)
    test_count = Column(Integer, default=0)

    # Configuration
    config_json = Column(JSON, nullable=True)

    # Relationships
    coverage_data = relationship("CoverageDataDB", back_populates="run", cascade="all, delete-orphan")
    mcdc_analyses = relationship("MCDCAnalysisDB", back_populates="run", cascade="all, delete-orphan")
    stop_decisions = relationship("StopDecisionDB", back_populates="run", cascade="all, delete-orphan")
    gaps = relationship("CoverageGapDB", back_populates="run", cascade="all, delete-orphan")
    reports = relationship("CoverageReportDB", back_populates="run", cascade="all, delete-orphan")
    effectiveness = relationship("TestEffectivenessDB", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_coverage_runs_pr_id', 'pr_id'),
        Index('idx_coverage_runs_status', 'status'),
    )


class CoverageDataDB(Base):
    """Database model for line-level coverage data."""
    __tablename__ = 'coverage_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    hit_count = Column(Integer, default=0)
    branch_id = Column(String, nullable=True)
    branch_taken = Column(Boolean, nullable=True)
    test_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("CoverageRunDB", back_populates="coverage_data")

    __table_args__ = (
        Index('idx_coverage_data_run_id', 'run_id'),
        Index('idx_coverage_data_file', 'file_path', 'line_number'),
    )


class MCDCAnalysisDB(Base):
    """Database model for MCDC analysis."""
    __tablename__ = 'mcdc_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    condition_id = Column(String, nullable=False)
    condition_text = Column(Text, nullable=False)

    truth_table_json = Column(Text, nullable=False)
    required_tests_json = Column(Text, nullable=False)
    completed_tests_json = Column(Text, nullable=False)

    satisfaction_percent = Column(Float, default=0.0)
    is_satisfied = Column(Boolean, default=False)

    run = relationship("CoverageRunDB", back_populates="mcdc_analyses")

    __table_args__ = (
        Index('idx_mcdc_analysis_run_id', 'run_id'),
        Index('idx_mcdc_analysis_file', 'file_path', 'line_number'),
    )


class StopDecisionDB(Base):
    """Database model for stop decisions."""
    __tablename__ = 'stop_decisions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    decision_time = Column(DateTime, default=datetime.utcnow)
    should_stop = Column(Boolean, default=False)
    reason = Column(String, nullable=False)
    confidence_score = Column(Float, default=0.0)
    metrics_json = Column(Text, nullable=True)

    run = relationship("CoverageRunDB", back_populates="stop_decisions")

    __table_args__ = (
        Index('idx_stop_decisions_run_id', 'run_id'),
    )


class CoverageGapDB(Base):
    """Database model for coverage gaps."""
    __tablename__ = 'coverage_gaps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    file_path = Column(String, nullable=False)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)
    gap_type = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    suggested_test = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)
    context_json = Column(Text, nullable=True)

    run = relationship("CoverageRunDB", back_populates="gaps")

    __table_args__ = (
        Index('idx_coverage_gaps_run_id', 'run_id'),
        Index('idx_coverage_gaps_priority', 'priority'),
    )


class CoverageReportDB(Base):
    """Database model for coverage reports."""
    __tablename__ = 'coverage_reports'

    report_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    report_type = Column(String, nullable=False)
    report_url = Column(String, nullable=True)
    report_data = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    metrics_json = Column(Text, nullable=True)

    run = relationship("CoverageRunDB", back_populates="reports")

    __table_args__ = (
        Index('idx_coverage_reports_run_id', 'run_id'),
    )


class TestEffectivenessDB(Base):
    """Database model for test effectiveness tracking."""
    __tablename__ = 'test_effectiveness'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('coverage_runs.run_id'), nullable=False)
    test_id = Column(String, nullable=False)
    test_name = Column(String, nullable=False)
    coverage_delta_lines = Column(Integer, default=0)
    coverage_delta_branches = Column(Integer, default=0)
    unique_coverage_lines = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.0)

    run = relationship("CoverageRunDB", back_populates="effectiveness")

    __table_args__ = (
        Index('idx_test_effectiveness_run_id', 'run_id'),
        Index('idx_test_effectiveness_score', 'effectiveness_score'),
    )


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class CoverageDatabase:
    """Database operations for coverage system."""

    def __init__(self, db_url: str = "sqlite:///./testgpt_coverage.db"):
        """
        Initialize database connection.

        Args:
            db_url: Database URL
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Coverage database tables created")

    def get_session(self):
        """Get database session."""
        return self.SessionLocal()

    # Coverage Run operations
    def save_coverage_run(self, coverage_run):
        """Save or update coverage run in database."""
        session = self.get_session()
        try:
            # Use merge to handle both insert and update
            db_run = CoverageRunDB(**coverage_run.to_dict())
            merged_run = session.merge(db_run)
            session.commit()
            return merged_run.run_id
        finally:
            session.close()

    def update_coverage_run(self, run_id: str, updates: dict):
        """Update coverage run."""
        session = self.get_session()
        try:
            session.query(CoverageRunDB).filter_by(run_id=run_id).update(updates)
            session.commit()
        finally:
            session.close()

    def get_coverage_run(self, run_id: str) -> Optional[CoverageRunDB]:
        """Get coverage run by ID."""
        session = self.get_session()
        try:
            return session.query(CoverageRunDB).filter_by(run_id=run_id).first()
        finally:
            session.close()

    # Coverage Data operations
    def save_coverage_data(self, coverage_data_list):
        """Save coverage data in batch."""
        session = self.get_session()
        try:
            db_data = [CoverageDataDB(**cd.to_dict()) for cd in coverage_data_list]
            session.bulk_save_objects(db_data)
            session.commit()
        finally:
            session.close()

    # MCDC Analysis operations
    def save_mcdc_analysis(self, mcdc_analysis):
        """Save MCDC analysis."""
        session = self.get_session()
        try:
            db_mcdc = MCDCAnalysisDB(**mcdc_analysis.to_dict())
            session.add(db_mcdc)
            session.commit()
            return db_mcdc.id
        finally:
            session.close()

    # Stop Decision operations
    def save_stop_decision(self, stop_decision):
        """Save stop decision."""
        session = self.get_session()
        try:
            db_decision = StopDecisionDB(**stop_decision.to_dict())
            session.add(db_decision)
            session.commit()
            return db_decision.id
        finally:
            session.close()

    # Coverage Gap operations
    def save_coverage_gaps(self, coverage_gaps):
        """Save coverage gaps."""
        session = self.get_session()
        try:
            db_gaps = [CoverageGapDB(**gap.to_dict()) for gap in coverage_gaps]
            session.bulk_save_objects(db_gaps)
            session.commit()
        finally:
            session.close()

    # Report operations
    def save_coverage_report(self, coverage_report):
        """Save coverage report."""
        session = self.get_session()
        try:
            db_report = CoverageReportDB(**coverage_report.to_dict())
            session.add(db_report)
            session.commit()
            return db_report.report_id
        finally:
            session.close()

    # Test Effectiveness operations
    def save_test_effectiveness(self, effectiveness):
        """Save test effectiveness."""
        session = self.get_session()
        try:
            db_effectiveness = TestEffectivenessDB(**effectiveness.to_dict())
            session.add(db_effectiveness)
            session.commit()
            return db_effectiveness.id
        finally:
            session.close()

    # Query operations
    def get_recent_runs(self, limit: int = 10) -> List[CoverageRunDB]:
        """Get recent coverage runs."""
        session = self.get_session()
        try:
            return session.query(CoverageRunDB)\
                .order_by(CoverageRunDB.started_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    def get_runs_by_pr(self, pr_id: str) -> List[CoverageRunDB]:
        """Get all coverage runs for a PR."""
        session = self.get_session()
        try:
            return session.query(CoverageRunDB)\
                .filter_by(pr_id=pr_id)\
                .order_by(CoverageRunDB.started_at.desc())\
                .all()
        finally:
            session.close()
