#!/usr/bin/env python3
"""Planner Agent - Master Coordinator"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseReActAgent
from ..prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_REACT_TEMPLATE,
    format_planner_state
)
from ..tools.analysis_tools import analyze_budget_status, categorize_errors

logger = logging.getLogger(__name__)


class PlannerAgent(BaseReActAgent):
    """
    Planner Agent - Master coordinator for multi-agent system.
    
    Responsibilities:
    - Analyze current state
    - Decide which specialist agent to invoke next
    - Manage budget strategically
    - Track quality tier progress
    - Determine when task is complete
    """
    
    def __init__(self, slm_client):
        """
        Initialize Planner Agent
        
        Args:
            slm_client: Shared SLM API client
        """
        # Planner's tools
        tools = [
            analyze_budget_status,
            categorize_errors
        ]
        
        super().__init__(
            name="planner",
            slm_client=slm_client,
            tools=tools,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            react_template=PLANNER_REACT_TEMPLATE
        )
    
    def decide_next_action(self, state: Dict) -> Dict[str, Any]:
        """
        Decide which agent should act next
        
        Args:
            state: Current VerilogState
            
        Returns:
            Decision dict: {"next_action": str, "reasoning": str}
        """
        logger.info("=" * 80)
        logger.info(f"PLANNER DECISION (Invocation {state['agent_invocations'] + 1}/50)")
        logger.info("=" * 80)
        
        # Format state for prompt
        prompt_inputs = format_planner_state(state)
        prompt_inputs["tools"] = self._format_tools()
        prompt_inputs["agent_scratchpad"] = "\n".join(state.get("agent_scratchpad", []))
        
        # Invoke planner
        try:
            result = self.executor.invoke(prompt_inputs)
            
            # Parse output
            output = result.get("output", "")
            decision = self.parse_json_output(output)
            
            if decision and "next_action" in decision:
                logger.info(f"Planner decision: {decision['next_action']}")
                logger.info(f"Reasoning: {decision.get('reasoning', 'N/A')}")
                return decision
            else:
                logger.warning("Planner output invalid, defaulting to code_gen")
                return {
                    "next_action": "code_gen",
                    "reasoning": "Default action due to parsing error"
                }
                
        except Exception as e:
            logger.error(f"Planner invocation failed: {e}")
            return {
                "next_action": "complete",
                "reasoning": f"Error occurred: {e}"
            }
    
    def _format_tools(self) -> str:
        """Format tool descriptions for prompt"""
        tool_descs = []
        for tool in self.tools:
            tool_descs.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tool_descs)
