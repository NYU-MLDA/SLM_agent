#!/usr/bin/env python3
"""Budget manager for 50-invocation limit"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class BudgetManager:
    """Manages the 50-invocation budget across all agents"""
    
    def __init__(self, total_budget: int = 50):
        """
        Initialize budget manager
        
        Args:
            total_budget: Total agent invocations allowed (default: 50)
        """
        self.total_budget = total_budget
        
        # Phase allocations (soft limits)
        self.phase_allocations = {
            "planner": 15,      # Planner gets significant budget for decisions
            "code_gen": 15,     # Code generation
            "validator": 8,     # Validation passes
            "tester": 8,        # Testing passes
            "analyzer": 4       # Analysis passes
        }
        
        logger.info(f"Initialized BudgetManager with {total_budget} invocations")
    
    def get_budget_zone(self, used: int) -> str:
        """
        Determine current budget zone
        
        Args:
            used: Invocations used so far
            
        Returns:
            Budget zone: GREEN, YELLOW, ORANGE, or RED
        """
        remaining = self.total_budget - used
        
        if remaining >= 40:
            return "GREEN"      # Explore alternatives
        elif remaining >= 20:
            return "YELLOW"     # Focus on refinement
        elif remaining >= 10:
            return "ORANGE"     # Prioritize completion
        else:
            return "RED"        # Finalize
    
    def get_strategy_recommendation(self, used: int, current_tier: int) -> str:
        """
        Recommend strategy based on budget and tier
        
        Args:
            used: Invocations used
            current_tier: Current quality tier achieved
            
        Returns:
            Strategy recommendation
        """
        zone = self.get_budget_zone(used)
        remaining = self.total_budget - used
        
        if zone == "GREEN":
            return "explore_alternatives"
        elif zone == "YELLOW":
            if current_tier >= 2:
                return "focus_on_testing"
            else:
                return "focus_on_quality"
        elif zone == "ORANGE":
            if current_tier >= 3:
                return "optimize"
            else:
                return "finish_strong"
        else:  # RED
            return "wrap_up"
    
    def can_invoke(self, used: int, agent_type: str, phase_used: Dict[str, int]) -> Tuple[bool, str]:
        """
        Check if agent can be invoked within budget
        
        Args:
            used: Total invocations used
            agent_type: Type of agent requesting invocation
            phase_used: Dict of agent_type -> count used
            
        Returns:
            Tuple of (can_invoke, reason)
        """
        # Hard limit check
        if used >= self.total_budget:
            return False, f"Budget exhausted ({used}/{self.total_budget})"
        
        # Soft limit check (per-phase)
        agent_used = phase_used.get(agent_type, 0)
        agent_limit = self.phase_allocations.get(agent_type, 10)
        
        if agent_used >= agent_limit:
            remaining_global = self.total_budget - used
            if remaining_global > 5:  # Still have global budget
                logger.warning(f"Agent {agent_type} exceeded soft limit ({agent_used}/{agent_limit})")
                return True, f"Using global budget (remaining: {remaining_global})"
            else:
                return False, f"Agent {agent_type} at limit and low global budget"
        
        return True, f"Within budget ({used}/{self.total_budget})"
    
    def format_budget_status(self, state) -> str:
        """
        Format budget status for logging
        
        Args:
            state: VerilogState dict
            
        Returns:
            Formatted budget status string
        """
        used = state["agent_invocations"]
        remaining = self.total_budget - used
        zone = self.get_budget_zone(used)
        percentage = (used / self.total_budget) * 100
        
        status = f"""
Budget Status:
  Used: {used}/{self.total_budget} ({percentage:.1f}%)
  Remaining: {remaining}
  Zone: {zone}
  Planner calls: {state["planner_calls"]}
  Code refinements: {state["code_refinements"]}
  Specialist calls: {state["specialist_calls"]}
"""
        return status.strip()
    
    def should_stop(self, state) -> Tuple[bool, str]:
        """
        Determine if execution should stop
        
        Args:
            state: VerilogState dict
            
        Returns:
            Tuple of (should_stop, reason)
        """
        # Budget exhausted
        if state["agent_invocations"] >= self.total_budget:
            return True, "Budget exhausted"
        
        # Success achieved
        if state["success"] and state["tier_achievements"].get(3, False):
            return True, "Success achieved (Tier 3)"
        
        # Too many consecutive failures
        if state["consecutive_failures"] >= 5:
            return True, "Too many consecutive failures"
        
        # Explicitly completed
        if state["completed"]:
            return True, "Task completed"
        
        return False, "Continue"
