#!/usr/bin/env python3
"""Testing tools wrapping existing test runners"""

from langchain.tools import tool
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@tool
def run_verilator_lint(code: str, target_file: str) -> Dict:
    """
    Runs Verilator lint checks on Verilog code.
    
    Args:
        code: Verilog code to test
        target_file: Path to write code before testing
        
    Returns:
        Test results: {"passed": bool, "errors": Optional[str]}
    """
    from slm_agent.testing.lint_runner import LintRunner
    from slm_agent.hdl.code_manager import CodeManager
    
    # Write code to file
    code_manager = CodeManager()
    target_path = Path(target_file)
    code_manager.write_code(target_path, code)
    
    # Run lint
    runner = LintRunner(timeout=30)
    success, errors = runner.run([target_path])
    
    logger.info(f"Verilator lint: passed={success}")
    
    return {
        "passed": success,
        "errors": errors if errors else None,
        "tool": "verilator"
    }


@tool
def run_cocotb_tests(code: str, target_file: str) -> Dict:
    """
    Runs CocoTB functional tests if available.
    
    Args:
        code: Verilog code to test
        target_file: Path to write code before testing
        
    Returns:
        Test results: {"passed": bool, "errors": Optional[str], "available": bool}
    """
    from slm_agent.testing.cocotb_runner import CocotbRunner
    from slm_agent.hdl.code_manager import CodeManager
    
    # Write code to file
    code_manager = CodeManager()
    target_path = Path(target_file)
    code_manager.write_code(target_path, code)
    
    # Run CocoTB
    runner = CocotbRunner(timeout=120)
    success, errors = runner.run()
    
    # If no errors returned, CocoTB not available
    available = bool(errors) or success
    
    logger.info(f"CocoTB tests: passed={success}, available={available}")
    
    return {
        "passed": success,
        "errors": errors if errors else None,
        "available": available,
        "tool": "cocotb"
    }


@tool
def run_comprehensive_tests(code: str, target_file: str) -> Dict:
    """
    Runs all available tests (CocoTB, Verilator, Icarus).
    
    Args:
        code: Verilog code to test
        target_file: Path to write code
        
    Returns:
        Comprehensive test results: {
            "passed": bool,
            "errors": Optional[str],
            "backend": str
        }
    """
    from slm_agent.testing.test_runner import TestRunner
    from slm_agent.hdl.code_manager import CodeManager
    
    # Write code to file
    code_manager = CodeManager()
    target_path = Path(target_file)
    code_manager.write_code(target_path, code)
    
    # Run comprehensive tests
    runner = TestRunner(test_timeout=120, lint_timeout=30)
    success, errors = runner.run()
    
    # Determine backend used
    backend = "unknown"
    if errors:
        if "verilator" in errors.lower():
            backend = "verilator"
        elif "icarus" in errors.lower() or "iverilog" in errors.lower():
            backend = "icarus"
        elif "pytest" in errors.lower() or "cocotb" in errors.lower():
            backend = "cocotb"
    else:
        backend = "passed"
    
    logger.info(f"Comprehensive tests: passed={success}, backend={backend}")
    
    return {
        "passed": success,
        "errors": errors if errors else None,
        "backend": backend
    }
