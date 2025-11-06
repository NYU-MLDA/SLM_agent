#!/usr/bin/env python3
"""Code Generator Agent - Verilog Code Creation and Refinement using ReAct"""

import logging
from typing import Dict, Any
from .base_agent import BaseReActAgent
from ..prompts.codegen_prompts import (
    CODEGEN_SYSTEM_PROMPT,
    CODEGEN_REACT_TEMPLATE
)
from ..tools.code_tools import (
    extract_code_from_response,
    get_design_pattern,
    check_if_initial_generation,
    refine_code_for_errors,
    refine_code_for_port_usage,
    build_generation_prompt
)

logger = logging.getLogger(__name__)


class CodeGenAgent(BaseReActAgent):
    """
    Code Generator Agent - Creates and refines Verilog code using ReAct reasoning.
    
    This agent uses the ReAct (Reasoning + Acting) pattern to:
    1. Analyze the current state (initial generation vs refinement)
    2. Use appropriate tools to guide code generation
    3. Generate or refine code based on context and feedback
    
    Responsibilities:
    - Generate initial code based on task
    - Refine code based on errors
    - Fix port usage issues
    - Apply design patterns
    - Integrate feedback from validation/testing
    """
    
    def __init__(self, slm_client):
        """
        Initialize Code Generator Agent with ReAct capabilities
        
        Args:
            slm_client: Shared SLM API client
        """
        # Register all code generation tools
        tools = [
            check_if_initial_generation,    # Determine generation type
            refine_code_for_errors,         # Error-driven refinement strategy
            refine_code_for_port_usage,     # Port usage refinement strategy
            build_generation_prompt,        # Prompt construction helper
            extract_code_from_response,     # Code extraction utility
            get_design_pattern              # Design pattern retrieval
        ]
        
        super().__init__(
            name="code_gen",
            slm_client=slm_client,
            tools=tools,
            system_prompt=CODEGEN_SYSTEM_PROMPT,
            react_template=CODEGEN_REACT_TEMPLATE
        )
        
        logger.info("CodeGenAgent initialized with unified ReAct flow")
    
    def generate_code(self, state: Dict) -> Dict[str, Any]:
        """
        Generate or refine Verilog code using unified ReAct reasoning.
        
        The agent will:
        1. Check if this is initial generation or refinement (via tool)
        2. Use appropriate tools to analyze the situation
        3. Reason through the best approach
        4. Generate or refine code accordingly
        
        Args:
            state: Current VerilogState containing:
                - task_description: Original task
                - current_code: Existing code (if refinement)
                - current_errors: Error messages (if any)
                - port_analysis: Port usage analysis (if any)
                - error_category: Categorized error type
                - iteration: Current iteration number
                - context_files: Available context
                
        Returns:
            Result dict: {
                "code": str,           # Generated/refined Verilog code
                "success": bool,       # Whether generation succeeded
                "method": str          # Generation method used
            }
        """
        logger.info("=" * 80)
        logger.info("CODE GENERATOR AGENT (Unified ReAct)")
        logger.info("=" * 80)
        
        # Log current state summary
        is_initial = not state.get("current_code")
        iteration = state.get("iteration", 0)
        logger.info(f"Generation type: {'INITIAL' if is_initial else 'REFINEMENT'}")
        logger.info(f"Iteration: {iteration}")
        
        if not is_initial:
            has_errors = bool(state.get("current_errors"))
            has_port_issues = (
                state.get("port_analysis", {}).get("all_ports_used") == False
            )
            logger.info(f"Has errors: {has_errors}")
            logger.info(f"Has port issues: {has_port_issues}")
        
        try:
            # Invoke ReAct agent with current state
            logger.info("Invoking ReAct reasoning loop...")
            result = self.invoke(state)
            
            # Parse output from ReAct agent
            output = result.get("output", "")
            logger.debug(f"ReAct output: {output[:200]}...")
            
            # Try to parse JSON output
            code_result = self.parse_json_output(output)
            
            if code_result and "code" in code_result:
                logger.info(f"Code generation successful: {len(code_result['code'])} bytes")
                logger.info(f"Method: {code_result.get('method', 'unknown')}")
                return code_result
            else:
                # Fallback: try to extract code directly from output
                logger.warning("Failed to parse JSON, attempting direct extraction")
                from slm_agent.llm.response_parser import ResponseParser
                parser = ResponseParser()
                code = parser.extract_verilog(output)
                
                if code:
                    logger.info(f"Extracted code via fallback: {len(code)} bytes")
                    return {
                        "code": code,
                        "success": True,
                        "method": "fallback_extraction"
                    }
                else:
                    logger.error("Failed to extract any code from ReAct output")
                    return {
                        "code": "",
                        "success": False,
                        "method": "failed"
                    }
                    
        except Exception as e:
            logger.error(f"CodeGen ReAct invocation failed: {e}", exc_info=True)
            return {
                "code": "",
                "success": False,
                "method": "error",
                "error": str(e)
            }
