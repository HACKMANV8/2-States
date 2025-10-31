"""
TestGPT Code Coverage System

Comprehensive coverage tracking, MCDC analysis, and intelligent test stopping.
"""

from .orchestrator import CoverageOrchestrator
from .models import (
    CoverageRun,
    CoverageData,
    MCDCAnalysis,
    StopDecision,
    CoverageGap,
    CoverageReport,
    TestEffectiveness
)
from .config import CoverageConfig

__all__ = [
    'CoverageOrchestrator',
    'CoverageRun',
    'CoverageData',
    'MCDCAnalysis',
    'StopDecision',
    'CoverageGap',
    'CoverageReport',
    'TestEffectiveness',
    'CoverageConfig'
]
