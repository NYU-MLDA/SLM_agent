#!/usr/bin/env python3
"""Validator Agent - Code Quality Validation"""

import logging
from typing import Dict, Any
from .base_specialist_agent import BaseSpecialistAgent

logger = logging.getLogger(__name__)


class ValidatorAgent(BaseSpecialistAgent):
    """
    Validator Agent - Validates code structure and semantics.
    
    This is a specialist agent that performs deterministic validation
    without needing ReAct reasoning. It directly checks code quality
    through a series of well-defined validation steps.
    """
    
    def __init__(self, slm_client):
        super().__init__(name="validator", slm_client=slm_client)
    
    def validate(self, state: Dict) -> Dict[str, Any]:
        """Run validation checks on code"""
        logger.info("=" * 80)
        logger.info("VALIDATOR AGENT")
        logger.info("=" * 80)
        
        code = state.get("current_code", "")
        if not code:
            return {"valid": False, "issues": ["No code to validate"], "tier_achieved": 0}
        
        # Run validations directly (simplified for prototype)
        from slm_agent.llm.response_parser import ResponseParser
        from slm_agent.hdl.port_analyzer import PortAnalyzer
        
        issues = []
        tier = 0
        
        # Structure check
        parser = ResponseParser()
        if parser.validate_basic_structure(code):
            tier = 1
            logger.info("Structure validation PASSED")
        else:
            issues.append("Structure validation failed")
        
        # Port check
        if tier >= 1:
            analyzer = PortAnalyzer()
            port_result = analyzer.analyze(code)
            if port_result["all_ports_used"]:
                tier = 2
                logger.info("Port validation PASSED")
            else:
                issues.append(f"Unused ports: {port_result['feedback']}")
        
        return {
            "valid": tier >= 2,
            "issues": issues,
            "tier_achieved": tier,
            "port_analysis": port_result if tier >= 1 else None
        }
