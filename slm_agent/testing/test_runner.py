#!/usr/bin/env python3
"""Orchestrate test execution (CocoTB and lint checks)"""

import logging
from pathlib import Path
from typing import Tuple, List
from .cocotb_runner import CocotbRunner
from .lint_runner import LintRunner

logger = logging.getLogger(__name__)


class TestRunner:
    """Orchestrate test execution"""
    
    def __init__(self, test_timeout: int = 120, lint_timeout: int = 30):
        """
        Initialize test runner
        
        Args:
            test_timeout: Timeout for CocoTB tests
            lint_timeout: Timeout for lint checks
        """
        self.cocotb_runner = CocotbRunner(timeout=test_timeout)
        self.lint_runner = LintRunner(timeout=lint_timeout)
    
    def run(self) -> Tuple[bool, str]:
        """
        Run tests using available tools
        
        Returns:
            Tuple of (success, error_messages)
        """
        logger.info("Starting test execution...")
        
        # Check if CocoTB tests are available
        cocotb_success, cocotb_errors = self.cocotb_runner.run()
        
        if cocotb_errors:  # CocoTB tests were found and executed
            return cocotb_success, cocotb_errors
        
        # Fallback to lint checks
        logger.info("CocoTB tests not available, running lint checks...")
        return self._run_lint_checks()
    
    def _run_lint_checks(self) -> Tuple[bool, str]:
        """Run lint checks on RTL files"""
        # Find RTL files
        rtl_files = self._find_rtl_files()
        
        if not rtl_files:
            logger.warning("No RTL files found for linting")
            return False, "No RTL files found"
        
        return self.lint_runner.run(rtl_files)
    
    def _find_rtl_files(self) -> List[Path]:
        """Find all RTL files for linting"""
        rtl_files = []
        rtl_dir = Path("/code/rtl")
        
        if not rtl_dir.exists():
            return rtl_files
        
        # Find .v and .sv files
        rtl_files.extend(rtl_dir.glob("*.v"))
        rtl_files.extend(rtl_dir.glob("*.sv"))
        
        return list(rtl_files)
    
    def categorize_errors(self, errors: str) -> str:
        """
        Categorize error messages
        
        Args:
            errors: Error messages from tests
            
        Returns:
            Error category (syntax, logic, timing, etc.)
        """
        errors_lower = errors.lower()
        
        # Syntax errors
        if any(kw in errors_lower for kw in ["syntax error", "parse error", "unexpected", "expected"]):
            return "syntax"
        
        # Undefined/undeclared
        if any(kw in errors_lower for kw in ["undeclared", "undefined", "not declared"]):
            return "undeclared"
        
        # Type errors
        if any(kw in errors_lower for kw in ["type mismatch", "incompatible types"]):
            return "type"
        
        # Width mismatches
        if any(kw in errors_lower for kw in ["width", "bit width", "size mismatch"]):
            return "width"
        
        # Latch inference
        if "latch" in errors_lower:
            return "latch"
        
        # Timing
        if any(kw in errors_lower for kw in ["timing", "setup", "hold"]):
            return "timing"
        
        # Default
        return "general"
