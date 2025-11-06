#!/usr/bin/env python3
"""LangGraph State Definition for Verilog Generation"""

from typing import TypedDict, Optional, List, Dict, Any


class VerilogState(TypedDict):
    """
    Shared state for ReAct multi-agent Verilog generation.
    
    This state is passed between agents through LangGraph.
    Each agent can read from and write to this state.
    """
    
    # ===== Task Information =====
    task_description: str                   # Original task from prompt.json
    context_files: Dict[str, str]           # File path -> content mapping
    target_file: str                        # Where to write generated code
    
    # ===== Code Evolution =====
    current_code: Optional[str]             # Current version of generated code
    code_history: List[str]                 # History of code versions (in-session)
    best_code: Optional[str]                # Best code so far (fallback)
    
    # ===== Validation Results =====
    structure_valid: bool                   # Basic structure check passed
    port_analysis: Optional[Dict]           # Port usage analysis results
    test_results: Optional[Dict]            # Test execution results
    validation_cache: Dict[str, Any]        # Cache validation results
    
    # ===== Error Tracking =====
    current_errors: Optional[str]           # Current error messages
    error_category: Optional[str]           # Categorized error type
    error_history: List[Dict]               # History of errors (in-session)
    consecutive_failures: int               # Count of consecutive failures
    
    # ===== Agent Coordination =====
    agent_scratchpad: List[str]             # Reasoning traces from agents
    last_agent: str                         # Last agent that executed
    next_action: str                        # Next agent to execute
    planner_reasoning: List[str]            # Planner's decision history
    
    # ===== Budget Tracking =====
    agent_invocations: int                  # Current agent call count
    max_invocations: int                    # Budget limit (50)
    code_refinements: int                   # Code generation count
    planner_calls: int                      # Planner invocation count
    specialist_calls: int                   # Specialist agent calls
    
    # ===== Quality Tracking =====
    current_tier: int                       # Current quality tier (1-4)
    target_tier: int                        # Target quality tier
    tier_achievements: Dict[int, bool]      # Which tiers achieved
    quality_metrics: Dict[str, Any]         # Quality measurements
    
    # ===== Status =====
    iteration: int                          # Current iteration number
    success: bool                           # Task completed successfully
    completed: bool                         # Workflow should terminate
    timeout: bool                           # Hit time limit
    budget_exhausted: bool                  # Hit invocation limit
    
    # ===== Metadata =====
    start_time: float                       # Task start timestamp
    execution_time: float                   # Total execution time
    final_message: str                      # Final status message


def create_initial_state(
    task_description: str,
    context_files: Dict[str, str],
    target_file: str,
    max_invocations: int = 50
) -> VerilogState:
    """
    Create initial state for a new Verilog generation task.
    
    Args:
        task_description: Task from prompt.json
        context_files: Context gathered from project
        target_file: Where to write code
        max_invocations: Budget limit
        
    Returns:
        Initialized VerilogState
    """
    import time
    
    return VerilogState(
        # Task
        task_description=task_description,
        context_files=context_files,
        target_file=target_file,
        
        # Code
        current_code=None,
        code_history=[],
        best_code=None,
        
        # Validation
        structure_valid=False,
        port_analysis=None,
        test_results=None,
        validation_cache={},
        
        # Errors
        current_errors=None,
        error_category=None,
        error_history=[],
        consecutive_failures=0,
        
        # Coordination
        agent_scratchpad=[],
        last_agent="",
        next_action="planner",  # Start with planner
        planner_reasoning=[],
        
        # Budget
        agent_invocations=0,
        max_invocations=max_invocations,
        code_refinements=0,
        planner_calls=0,
        specialist_calls=0,
        
        # Quality
        current_tier=0,
        target_tier=3,  # Default: aim for tested code
        tier_achievements={1: False, 2: False, 3: False, 4: False},
        quality_metrics={},
        
        # Status
        iteration=0,
        success=False,
        completed=False,
        timeout=False,
        budget_exhausted=False,
        
        # Metadata
        start_time=time.time(),
        execution_time=0.0,
        final_message=""
    )
