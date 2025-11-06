#!/usr/bin/env python3
"""Validation tools wrapping existing slm_agent modules"""

from langchain.tools import tool
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@tool
def validate_structure(code: str) -> Dict:
    """
    Validates basic Verilog structure (module/endmodule, balanced parens).
    
    Args:
        code: Verilog source code to validate
        
    Returns:
        Dictionary with validation result: {"valid": bool, "message": str}
    """
    from slm_agent.llm.response_parser import ResponseParser
    
    parser = ResponseParser()
    valid = parser.validate_basic_structure(code)
    
    if valid:
        message = "Structure validation passed: module/endmodule present, balanced parentheses"
    else:
        message = "Structure validation failed: missing module/endmodule or unbalanced parentheses"
    
    logger.info(f"Structure validation: {valid}")
    return {"valid": valid, "message": message}


@tool
def validate_port_usage(code: str) -> Dict:
    """
    Validates that all declared module ports are used in the code.
    
    Checks:
    - All input ports are referenced in module logic
    - All output ports are assigned values
    
    Args:
        code: Verilog source code to analyze
        
    Returns:
        Dictionary with port analysis: {
            "all_ports_used": bool,
            "unused_inputs": List[str],
            "unused_outputs": List[str],
            "feedback": str
        }
    """
    from slm_agent.hdl.port_analyzer import PortAnalyzer
    
    analyzer = PortAnalyzer()
    result = analyzer.analyze(code)
    
    logger.info(f"Port validation: all_used={result['all_ports_used']}")
    if not result["all_ports_used"]:
        logger.warning(f"  Unused inputs: {result['unused_inputs']}")
        logger.warning(f"  Unused outputs: {result['unused_outputs']}")
    
    return result


@tool
def check_module_completeness(code: str, task_requirements: str) -> Dict:
    """
    Checks if generated code addresses all task requirements.
    
    Args:
        code: Verilog source code
        task_requirements: Original task description
        
    Returns:
        Dictionary with completeness analysis: {
            "complete": bool,
            "missing_features": List[str],
            "feedback": str
        }
    """
    # Extract module name
    from slm_agent.llm.response_parser import ResponseParser
    
    parser = ResponseParser()
    module_name = parser.extract_module_name(code)
    
    missing_features = []
    
    # Basic checks
    if not module_name:
        missing_features.append("Module name not found")
    
    # Check for common requirements in task
    task_lower = task_requirements.lower()
    
    if "reset" in task_lower and "rst" not in code.lower():
        missing_features.append("Reset logic mentioned in task but not in code")
    
    if "clock" in task_lower and "clk" not in code.lower():
        missing_features.append("Clock mentioned in task but not in code")
    
    if "parameter" in task_lower and "parameter" not in code.lower():
        missing_features.append("Parameterization mentioned but not implemented")
    
    complete = len(missing_features) == 0
    
    if complete:
        feedback = "Code appears complete with respect to task requirements"
    else:
        feedback = "Missing features: " + ", ".join(missing_features)
    
    logger.info(f"Completeness check: {complete}")
    
    return {
        "complete": complete,
        "missing_features": missing_features,
        "feedback": feedback
    }
