#!/usr/bin/env python3
"""Run Verilator and Icarus Verilog lint checks"""

import subprocess
import logging
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)


class LintRunner:
    """Run HDL lint checks using Verilator or Icarus Verilog"""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize lint runner
        
        Args:
            timeout: Timeout for lint commands in seconds
        """
        self.timeout = timeout
    
    def run(self, rtl_files: List[Path]) -> Tuple[bool, str]:
        """
        Run lint checks on RTL files
        
        Args:
            rtl_files: List of RTL file paths
            
        Returns:
            Tuple of (success, error_messages)
        """
        if not rtl_files:
            logger.warning("No RTL files to lint")
            return False, "No RTL files found"
        
        logger.info(f"Linting {len(rtl_files)} RTL files...")
        
        # Try Verilator first
        success, errors = self._run_verilator(rtl_files)
        if success or errors:  # If verilator worked (even with errors)
            return success, errors
        
        # Fallback to Icarus Verilog
        logger.info("Verilator not available, trying Icarus Verilog...")
        return self._run_icarus(rtl_files)
    
    def _run_verilator(self, rtl_files: List[Path]) -> Tuple[bool, str]:
        """Run Verilator lint checks"""
        try:
            cmd = ["verilator", "--lint-only", "-Wall"] + [str(f) for f in rtl_files]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stderr + result.stdout
            
            if result.returncode == 0:
                logger.info("Verilator lint checks PASSED")
                return True, ""
            else:
                logger.warning("Verilator lint checks FAILED")
                # Extract first 50 lines of errors
                error_lines = output.split("\n")[:50]
                errors = "\n".join(error_lines)
                return False, errors
                
        except FileNotFoundError:
            logger.info("Verilator not found")
            return False, ""
        except subprocess.TimeoutExpired:
            logger.error(f"Verilator timeout after {self.timeout}s")
            return False, f"Lint timeout after {self.timeout}s"
        except Exception as e:
            logger.warning(f"Verilator error: {e}")
            return False, ""
    
    def _run_icarus(self, rtl_files: List[Path]) -> Tuple[bool, str]:
        """Run Icarus Verilog lint checks"""
        try:
            cmd = ["iverilog", "-tnull", "-Wall"] + [str(f) for f in rtl_files]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stderr + result.stdout
            
            # Icarus returns 0 even with warnings, check for "error" in output
            if result.returncode == 0 and "error" not in output.lower():
                logger.info("Icarus Verilog checks PASSED")
                return True, ""
            else:
                logger.warning("Icarus Verilog checks FAILED")
                error_lines = output.split("\n")[:50]
                errors = "\n".join(error_lines)
                return False, errors
                
        except FileNotFoundError:
            logger.error("Icarus Verilog not found")
            return False, "No suitable lint tool available (tried Verilator and Icarus)"
        except subprocess.TimeoutExpired:
            logger.error(f"Icarus timeout after {self.timeout}s")
            return False, f"Lint timeout after {self.timeout}s"
        except Exception as e:
            logger.error(f"Icarus error: {e}")
            return False, str(e)
