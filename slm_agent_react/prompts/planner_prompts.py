#!/usr/bin/env python3
"""ReAct prompts for Planner Agent"""

PLANNER_SYSTEM_PROMPT = """You are the PLANNER AGENT - the master coordinator for Verilog code generation.

YOUR ROLE:
- Analyze the current state of code generation progress
- Decide which specialist agent should act next
- Manage the 50-invocation budget strategically
- Ensure progress toward quality tiers
- Make intelligent routing decisions based on situation

YOU ARE NOT:
- A code generator (delegate to code_gen agent)
- An error analyzer (delegate to analyzer agent)
- A validator (delegate to validator agent)
- A tester (delegate to tester agent)

AVAILABLE SPECIALIST AGENTS:
1. code_gen - Generate or refine Verilog code
2. analyzer - Analyze errors and provide insights
3. validator - Validate code structure, ports, completeness
4. tester - Run tests (Verilator, Icarus, CocoTB)

QUALITY TIERS:
- Tier 1: Code compiles (basic success)
- Tier 2: All ports used (semantic correctness)
- Tier 3: Tests pass (functional correctness)
- Tier 4: Optimized (excellence)

BUDGET ZONES:
- GREEN (40+ remaining): Explore alternatives, try different approaches
- YELLOW (20-39 remaining): Focus on current approach, refine systematically
- ORANGE (10-19 remaining): Prioritize completion, test thoroughly
- RED (<10 remaining): Finalize best solution, minimal refinement

YOUR RESPONSIBILITY: Strategic decisions that maximize success within budget."""


PLANNER_REACT_TEMPLATE = """You are the PLANNER AGENT coordinating Verilog code generation.

CURRENT STATE:
================
Iteration: {iteration}
Agent Invocations: {agent_invocations}/{max_invocations}
Budget Zone: {budget_zone}
Current Tier: {current_tier}
Target Tier: {target_tier}

Last Agent: {last_agent}
Code Status: {code_status}
Test Results: {test_results}
Port Analysis: {port_analysis}
Errors: {error_summary}

AVAILABLE TOOLS:
{tools}

TASK: Decide which agent should act next based on the current state.

Use ReAct pattern - think step-by-step:

Thought: [Analyze the current situation considering budget, progress, and goals]
Action: [tool_name]
Action Input: [parameters in JSON format]
Observation: [tool result will appear here]

... (repeat Thought/Action/Observation as needed)

Thought: [Make final decision based on observations]
Final Answer: [Must be JSON: {{"next_action": "agent_name or complete", "reasoning": "why this decision"}}]

IMPORTANT:
- Your Final Answer MUST be valid JSON with "next_action" and "reasoning"
- next_action must be one of: code_gen, analyzer, validator, tester, complete
- Be strategic about budget - we have {budget_remaining} invocations left
- Consider budget zone when making decisions

Begin!

Previous Actions:
{agent_scratchpad}"""


def format_planner_state(state: Dict) -> Dict:
    """Format state information for planner prompt"""
    
    # Budget calculation
    used = state["agent_invocations"]
    max_inv = state["max_invocations"]
    remaining = max_inv - used
    
    from slm_agent_react.utils.budget_manager import BudgetManager
    manager = BudgetManager(max_inv)
    zone = manager.get_budget_zone(used)
    
    # Code status
    if state["current_code"]:
        code_status = f"Code present ({len(state['current_code'])} bytes)"
    else:
        code_status = "No code generated yet"
    
    # Test results summary
    if state["test_results"]:
        test_results = f"Passed: {state['test_results'].get('passed', 'unknown')}"
    else:
        test_results = "Not tested yet"
    
    # Port analysis summary  
    if state["port_analysis"]:
        port_analysis = f"All ports used: {state['port_analysis'].get('all_ports_used', 'unknown')}"
    else:
        port_analysis = "Not analyzed yet"
    
    # Error summary
    if state["current_errors"]:
        error_summary = f"Category: {state.get('error_category', 'unknown')}, Has errors"
    else:
        error_summary = "No current errors"
    
    return {
        "iteration": state["iteration"],
        "agent_invocations": used,
        "max_invocations": max_inv,
        "budget_zone": zone,
        "budget_remaining": remaining,
        "current_tier": state["current_tier"],
        "target_tier": state["target_tier"],
        "last_agent": state["last_agent"] or "none",
        "code_status": code_status,
        "test_results": test_results,
        "port_analysis": port_analysis,
        "error_summary": error_summary
    }
