#!/usr/bin/env python3
"""Code generation tools wrapping SLM calls"""

from langchain.tools import tool
from typing import Dict
import logging

logger = logging.getLogger(__name__)


# Note: Code generation is implemented directly in CodeGenAgent class
# (agents/codegen_agent.py) because it needs direct SLM access
# LangChain tools can't easily access slm_client from execution context

@tool  
def extract_code_from_response(response: str) -> Dict:
    """
    Extracts Verilog code from SLM response.
    
    Args:
        response: Raw SLM response
        
    Returns:
        Extracted code: {"code": str, "method": str}
    """
    from slm_agent.llm.response_parser import ResponseParser
    
    parser = ResponseParser()
    code = parser.extract_verilog(response)
    
    # Determine extraction method
    if "```verilog" in response or "```systemverilog" in response:
        method = "markdown"
    elif "module " in response:
        method = "module_boundary"
    else:
        method = "raw"
    
    logger.info(f"Extracted code using method: {method}")
    
    return {
        "code": code,
        "method": method,
        "success": bool(code)
    }


@tool
def get_design_pattern(pattern_type: str) -> Dict:
    """
    Retrieves a design pattern example.
    
    Args:
        pattern_type: Type of pattern (counter, fifo, fsm)
        
    Returns:
        Pattern example: {"pattern": str, "description": str}
    """
    from slm_agent.prompts.templates import FEW_SHOT_EXAMPLES
    
    pattern = FEW_SHOT_EXAMPLES.get(pattern_type, FEW_SHOT_EXAMPLES["counter"])
    
    descriptions = {
        "counter": "Parameterized counter with enable and reset",
        "fifo": "Synchronous FIFO with full/empty flags",
        "fsm": "Finite state machine with proper state encoding"
    }
    
    description = descriptions.get(pattern_type, "Basic design pattern")
    
    logger.info(f"Retrieved pattern: {pattern_type}")
    
    return {
        "pattern": pattern,
        "description": description,
        "pattern_type": pattern_type
    }


@tool
def check_if_initial_generation(state_json: str) -> Dict:
    """
    Check if this is initial code generation or refinement.
    
    Args:
        state_json: JSON string of current state
        
    Returns:
        Result: {"is_initial": bool, "reason": str}
    """
    import json
    
    try:
        state = json.loads(state_json)
    except:
        state = {}
    
    current_code = state.get("current_code", "")
    is_initial = not bool(current_code)
    
    reason = "No existing code found" if is_initial else "Code exists, will refine"
    
    logger.info(f"Generation type check: {'INITIAL' if is_initial else 'REFINEMENT'}")
    
    return {
        "is_initial": is_initial,
        "reason": reason,
        "iteration": state.get("iteration", 0)
    }


@tool
def refine_code_for_errors(code: str, errors: str, error_category: str) -> Dict:
    """
    Analyze errors and determine refinement strategy.
    
    Args:
        code: Current code
        errors: Error messages from testing
        error_category: Category of errors (syntax, undeclared, etc.)
        
    Returns:
        Refinement strategy: {"strategy": str, "focus_areas": list}
    """
    strategies = {
        "syntax": {
            "strategy": "Fix syntax errors (semicolons, parentheses, keywords)",
            "focus_areas": ["Check semicolons", "Verify module/endmodule", "Check parentheses"]
        },
        "undeclared": {
            "strategy": "Add missing signal declarations",
            "focus_areas": ["Declare all signals", "Check signal names", "Add wire/reg as needed"]
        },
        "type": {
            "strategy": "Fix type mismatches",
            "focus_areas": ["Verify signal types", "Add type casting", "Check bit widths"]
        },
        "width": {
            "strategy": "Fix width mismatches",
            "focus_areas": ["Check bit widths", "Verify array dimensions", "Add width specifiers"]
        },
        "latch": {
            "strategy": "Remove inferred latches",
            "focus_areas": ["Add default case", "Complete if/else branches", "Initialize outputs"]
        },
        "general": {
            "strategy": "General error fixes",
            "focus_areas": ["Review error messages", "Check Verilog standard", "Fix reported issues"]
        }
    }
    
    result = strategies.get(error_category, strategies["general"])
    
    logger.info(f"Refinement strategy: {result['strategy']}")
    
    return {
        **result,
        "error_category": error_category,
        "errors_present": bool(errors)
    }


@tool
def refine_code_for_port_usage(code: str, unused_inputs: str, unused_outputs: str) -> Dict:
    """
    Analyze unused ports and determine how to use them.
    
    Args:
        code: Current code
        unused_inputs: Comma-separated unused input ports
        unused_outputs: Comma-separated unused output ports
        
    Returns:
        Port usage strategy: {"strategy": str, "actions": list}
    """
    actions = []
    
    if unused_inputs:
        inputs = [i.strip() for i in unused_inputs.split(",") if i.strip()]
        actions.append(f"Use input ports in logic: {', '.join(inputs)}")
    
    if unused_outputs:
        outputs = [o.strip() for o in unused_outputs.split(",") if o.strip()]
        actions.append(f"Assign values to outputs: {', '.join(outputs)}")
    
    strategy = "Fix unused port issues to achieve Tier 2 quality"
    
    logger.info(f"Port usage strategy: {len(actions)} actions needed")
    
    return {
        "strategy": strategy,
        "actions": actions,
        "unused_input_count": len(unused_inputs.split(",")) if unused_inputs else 0,
        "unused_output_count": len(unused_outputs.split(",")) if unused_outputs else 0
    }


@tool
def build_generation_prompt(task: str, context_files: str, is_initial: bool) -> Dict:
    """
    Build appropriate prompt for code generation.
    
    Args:
        task: Task description
        context_files: Available context files (JSON string)
        is_initial: True for initial generation, False for refinement
        
    Returns:
        Prompt info: {"prompt_type": str, "use_few_shot": bool}
    """
    import json
    
    try:
        context = json.loads(context_files) if context_files else []
    except:
        context = []
    
    if is_initial:
        prompt_type = "initial_generation"
        use_few_shot = True
        logger.info("Building initial generation prompt with examples")
    else:
        prompt_type = "refinement"
        use_few_shot = False
        logger.info("Building refinement prompt")
    
    return {
        "prompt_type": prompt_type,
        "use_few_shot": use_few_shot,
        "context_file_count": len(context),
        "task_length": len(task)
    }
