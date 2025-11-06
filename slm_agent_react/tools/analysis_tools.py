#!/usr/bin/env python3
"""Analysis tools for error categorization and insights"""

from langchain.tools import tool
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


@tool
def categorize_errors(error_text: str) -> Dict:
    """
    Categorizes error messages into types for targeted refinement.
    
    Categories:
    - syntax: Parse errors, unexpected tokens
    - undeclared: Undefined variables/signals
    - type: Type mismatches
    - width: Bit width issues
    - latch: Latch inference warnings
    - timing: Timing violations
    - general: Other errors
    
    Args:
        error_text: Raw error messages from tests
        
    Returns:
        Categorization result: {"category": str, "description": str}
    """
    from slm_agent.testing.test_runner import TestRunner
    
    runner = TestRunner()
    category = runner.categorize_errors(error_text)
    
    descriptions = {
        "syntax": "Syntax/parse errors - structural issues in code",
        "undeclared": "Undeclared variables/signals - missing declarations",
        "type": "Type mismatches - incompatible types in expressions",
        "width": "Bit width issues - size mismatches in operations",
        "latch": "Latch inference - incomplete case/if statements",
        "timing": "Timing violations - setup/hold time issues",
        "general": "General errors - uncategorized"
    }
    
    description = descriptions.get(category, "Unknown error type")
    
    logger.info(f"Error category: {category}")
    
    return {
        "category": category,
        "description": description,
        "severity": "high" if category in ["syntax", "undeclared"] else "medium"
    }


@tool
def extract_error_locations(error_text: str) -> Dict:
    """
    Extracts line numbers and specific locations from error messages.
    
    Args:
        error_text: Raw error messages
        
    Returns:
        Extracted locations: {
            "line_numbers": List[int],
            "files": List[str],
            "snippets": List[str]
        }
    """
    import re
    
    line_numbers = []
    files = []
    snippets = []
    
    # Extract line numbers (e.g., "line 47", ":47:", "line=47")
    line_patterns = [
        r'line[:\s]+(\d+)',
        r':(\d+):',
        r'line=(\d+)'
    ]
    
    for pattern in line_patterns:
        matches = re.findall(pattern, error_text, re.IGNORECASE)
        line_numbers.extend([int(m) for m in matches])
    
    # Extract file references
    file_pattern = r'(\S+\.(?:v|sv))'
    files = list(set(re.findall(file_pattern, error_text)))
    
    # Extract error snippets (lines with "error:" or "Error:")
    for line in error_text.split('\n'):
        if 'error' in line.lower() or 'fail' in line.lower():
            snippets.append(line.strip())
    
    logger.info(f"Extracted {len(line_numbers)} error locations")
    
    return {
        "line_numbers": sorted(set(line_numbers)),
        "files": files,
        "snippets": snippets[:10]  # First 10 error lines
    }


@tool
def generate_fix_suggestions(error_category: str, error_details: str) -> Dict:
    """
    Generates specific fix suggestions based on error category.
    
    Args:
        error_category: Type of error (from categorize_errors)
        error_details: Detailed error messages
        
    Returns:
        Fix suggestions: {
            "suggestions": List[str],
            "priority": str,
            "estimated_effort": str
        }
    """
    suggestions = []
    priority = "medium"
    effort = "moderate"
    
    if error_category == "syntax":
        suggestions = [
            "Check for missing semicolons",
            "Verify balanced parentheses and braces",
            "Check module/endmodule keywords",
            "Verify signal declarations before use"
        ]
        priority = "high"
        effort = "low"
    
    elif error_category == "undeclared":
        suggestions = [
            "Add signal declarations (logic, wire, reg)",
            "Check for typos in signal names",
            "Verify scope of signal declarations",
            "Add parameter declarations if needed"
        ]
        priority = "high"
        effort = "low"
    
    elif error_category == "type":
        suggestions = [
            "Check signal types in expressions",
            "Add explicit type casting if needed",
            "Verify packed vs unpacked array usage",
            "Check signed/unsigned mismatches"
        ]
        priority = "medium"
        effort = "moderate"
    
    elif error_category == "width":
        suggestions = [
            "Check bit width of operands",
            "Add explicit width specifications",
            "Verify array dimensions",
            "Check parameter values"
        ]
        priority = "medium"
        effort = "moderate"
    
    elif error_category == "latch":
        suggestions = [
            "Add default case in case statements",
            "Ensure all conditions covered in if/else",
            "Use always_ff for sequential logic",
            "Initialize all outputs in combinational blocks"
        ]
        priority = "high"
        effort = "moderate"
    
    else:  # general or unknown
        suggestions = [
            "Review error messages carefully",
            "Check IEEE 1800 SystemVerilog standard",
            "Verify all signal assignments",
            "Check for common Verilog pitfalls"
        ]
        priority = "medium"
        effort = "high"
    
    logger.info(f"Generated {len(suggestions)} suggestions for {error_category}")
    
    return {
        "suggestions": suggestions,
        "priority": priority,
        "estimated_effort": effort
    }


@tool
def analyze_budget_status(used: int, max_budget: int, current_tier: int) -> Dict:
    """
    Analyzes current budget usage and recommends strategy.
    
    Args:
        used: Invocations used so far
        max_budget: Total budget (50)
        current_tier: Current quality tier achieved
        
    Returns:
        Budget analysis: {
            "zone": str,
            "remaining": int,
            "percentage_used": float,
            "strategy": str,
            "recommendation": str
        }
    """
    from slm_agent_react.utils.budget_manager import BudgetManager
    
    manager = BudgetManager(total_budget=max_budget)
    
    remaining = max_budget - used
    percentage = (used / max_budget) * 100
    zone = manager.get_budget_zone(used)
    strategy = manager.get_strategy_recommendation(used, current_tier)
    
    # Generate recommendation
    if zone == "GREEN":
        recommendation = "Explore different approaches, be creative"
    elif zone == "YELLOW":
        recommendation = "Focus on current approach, refine systematically"
    elif zone == "ORANGE":
        recommendation = "Prioritize completion, test thoroughly"
    else:  # RED
        recommendation = "Finalize best solution, minimal refinement"
    
    logger.info(f"Budget analysis: {percentage:.1f}% used, zone={zone}")
    
    return {
        "zone": zone,
        "remaining": remaining,
        "percentage_used": percentage,
        "strategy": strategy,
        "recommendation": recommendation
    }
