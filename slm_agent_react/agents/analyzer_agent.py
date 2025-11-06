#!/usr/bin/env python3
"""Analyzer Agent - Error Analysis and Insights"""

import logging
from typing import Dict, Any
from .base_specialist_agent import BaseSpecialistAgent

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseSpecialistAgent):
    """
    Analyzer Agent - Analyzes errors and provides insights.
    
    This is a specialist agent that performs deterministic error analysis
    without needing ReAct reasoning. It categorizes errors and suggests
    fixes based on predefined patterns.
    """
    
    def __init__(self, slm_client):
        super().__init__(name="analyzer", slm_client=slm_client)
    
    def analyze(self, state: Dict) -> Dict[str, Any]:
        """Analyze errors and provide insights"""
        logger.info("=" * 80)
        logger.info("ANALYZER AGENT")
        logger.info("=" * 80)
        
        errors = state.get("current_errors", "")
        if not errors:
            return {"category": "none", "suggestions": [], "priority": "low"}
        
        # Use tools directly (simplified)
        from slm_agent.testing.test_runner import TestRunner
        
        runner = TestRunner()
        category = runner.categorize_errors(errors)
        
        logger.info(f"Error category: {category}")
        
        # Generate suggestions based on category
        suggestions_map = {
            "syntax": ["Check semicolons", "Verify module/endmodule", "Check parentheses"],
            "undeclared": ["Add signal declarations", "Check signal names"],
            "type": ["Verify signal types", "Add type casting"],
            "width": ["Check bit widths", "Verify array dimensions"],
            "latch": ["Add default case", "Complete if/else"],
            "general": ["Review error messages", "Check Verilog standard"]
        }
        
        suggestions = suggestions_map.get(category, ["Review errors carefully"])
        
        return {
            "category": category,
            "suggestions": suggestions,
            "priority": "high" if category in ["syntax", "undeclared"] else "medium"
        }
