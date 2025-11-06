#!/usr/bin/env python3
"""Tester Agent - Test Execution"""

import logging
from typing import Dict, Any
from .base_specialist_agent import BaseSpecialistAgent

logger = logging.getLogger(__name__)


class TesterAgent(BaseSpecialistAgent):
    """
    Tester Agent - Executes tests and reports results.
    
    This is a specialist agent that performs deterministic testing
    without needing ReAct reasoning. It runs predefined test suites
    and returns structured results.
    """
    
    def __init__(self, slm_client):
        super().__init__(name="tester", slm_client=slm_client)
    
    def test(self, state: Dict) -> Dict[str, Any]:
        """Run tests on code"""
        logger.info("=" * 80)
        logger.info("TESTER AGENT")
        logger.info("=" * 80)
        
        code = state.get("current_code", "")
        target_file = state.get("target_file", "/code/rtl/top.sv")
        
        if not code:
            return {"passed": False, "errors": "No code to test", "tier_achieved": 0}
        
        # Run comprehensive tests (simplified)
        from slm_agent.testing.test_runner import TestRunner
        from slm_agent.hdl.code_manager import CodeManager
        from pathlib import Path
        
        # Write code
        manager = CodeManager()
        manager.write_code(Path(target_file), code)
        
        # Run tests
        runner = TestRunner(test_timeout=120, lint_timeout=30)
        passed, errors = runner.run()
        
        tier_achieved = 3 if passed else 1  # 3 if tests pass, 1 if just compiles
        
        logger.info(f"Tests: {'PASSED' if passed else 'FAILED'}, Tier: {tier_achieved}")
        
        return {
            "passed": passed,
            "errors": errors if errors else None,
            "tier_achieved": tier_achieved,
            "backend": "comprehensive"
        }
