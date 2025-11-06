#!/usr/bin/env python3
"""LangGraph workflow for ReAct multi-agent system"""

import logging
import time
from typing import Dict
from langgraph.graph import StateGraph, END
from ..state.verilog_state import VerilogState
from ..utils.budget_manager import BudgetManager

logger = logging.getLogger(__name__)


def create_workflow(agents: Dict, config) -> StateGraph:
    """
    Create LangGraph workflow for Verilog generation
    
    Args:
        agents: Dictionary of agent instances
        config: ReActConfig instance
        
    Returns:
        Compiled StateGraph
    """
    workflow = StateGraph(VerilogState)
    
    # Create node functions for each agent
    def planner_node(state: VerilogState) -> VerilogState:
        """Planner agent node"""
        logger.info(f"\n>>> PLANNER NODE (Invocation {state['agent_invocations'] + 1})")
        
        # Check budget
        budget_mgr = BudgetManager(state["max_invocations"])
        should_stop, reason = budget_mgr.should_stop(state)
        if should_stop:
            logger.warning(f"Stopping: {reason}")
            state["completed"] = True
            state["next_action"] = "complete"
            return state
        
        # Planner decides
        decision = agents["planner"].decide_next_action(state)
        
        # Update state
        state["next_action"] = decision.get("next_action", "complete")
        state["planner_reasoning"].append(decision.get("reasoning", ""))
        state["agent_invocations"] += 1
        state["planner_calls"] += 1
        state["last_agent"] = "planner"
        
        logger.info(f"Planner decision: {state['next_action']}")
        
        return state
    
    def code_gen_node(state: VerilogState) -> VerilogState:
        """Code generator agent node"""
        logger.info(f"\n>>> CODE GENERATOR NODE (Invocation {state['agent_invocations'] + 1})")
        
        # Generate code
        result = agents["code_gen"].generate_code(state)
        
        # Update state
        if result.get("success"):
            state["current_code"] = result["code"]
            state["code_history"].append(result["code"])
            state["code_refinements"] += 1
            if not state["best_code"] or len(result["code"]) > len(state["best_code"]):
                state["best_code"] = result["code"]
            state["consecutive_failures"] = 0
        else:
            state["consecutive_failures"] += 1
        
        state["agent_invocations"] += 1
        state["specialist_calls"] += 1
        state["last_agent"] = "code_gen"
        state["iteration"] += 1
        
        return state
    
    def validator_node(state: VerilogState) -> VerilogState:
        """Validator agent node"""
        logger.info(f"\n>>> VALIDATOR NODE (Invocation {state['agent_invocations'] + 1})")
        
        # Validate code
        result = agents["validator"].validate(state)
        
        # Update state
        state["structure_valid"] = result.get("valid", False)
        state["port_analysis"] = result.get("port_analysis")
        tier = result.get("tier_achieved", 0)
        
        if tier > state["current_tier"]:
            state["current_tier"] = tier
            state["tier_achievements"][tier] = True
            logger.info(f"TIER {tier} ACHIEVED!")
        
        if not result.get("valid"):
            state["current_errors"] = "\n".join(result.get("issues", []))
        
        state["agent_invocations"] += 1
        state["specialist_calls"] += 1
        state["last_agent"] = "validator"
        
        return state
    
    def tester_node(state: VerilogState) -> VerilogState:
        """Tester agent node"""
        logger.info(f"\n>>> TESTER NODE (Invocation {state['agent_invocations'] + 1})")
        
        # Run tests
        result = agents["tester"].test(state)
        
        # Update state
        state["test_results"] = result
        passed = result.get("passed", False)
        tier = result.get("tier_achieved", 0)
        
        if tier > state["current_tier"]:
            state["current_tier"] = tier
            state["tier_achievements"][tier] = True
            logger.info(f"TIER {tier} ACHIEVED!")
        
        if passed:
            state["success"] = True
            if config.exit_on_tier3 and tier >= 3:
                state["completed"] = True
        else:
            state["current_errors"] = result.get("errors", "")
            state["consecutive_failures"] += 1
        
        state["agent_invocations"] += 1
        state["specialist_calls"] += 1
        state["last_agent"] = "tester"
        
        return state
    
    def analyzer_node(state: VerilogState) -> VerilogState:
        """Analyzer agent node"""
        logger.info(f"\n>>> ANALYZER NODE (Invocation {state['agent_invocations'] + 1})")
        
        # Analyze errors
        result = agents["analyzer"].analyze(state)
        
        # Update state
        state["error_category"] = result.get("category", "general")
        state["error_history"].append({
            "category": result["category"],
            "suggestions": result["suggestions"]
        })
        
        state["agent_invocations"] += 1
        state["specialist_calls"] += 1
        state["last_agent"] = "analyzer"
        
        return state
    
    # Add nodes to workflow
    workflow.add_node("planner", planner_node)
    workflow.add_node("code_gen", code_gen_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("analyzer", analyzer_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Conditional routing from planner
    def route_from_planner(state: VerilogState) -> str:
        """Route to next agent based on planner decision"""
        next_action = state.get("next_action", "complete")
        
        # Check termination conditions
        if state.get("completed") or next_action == "complete":
            return END
        
        if state["agent_invocations"] >= state["max_invocations"]:
            logger.warning("Budget exhausted!")
            return END
        
        # Route to specialist
        valid_actions = ["code_gen", "validator", "tester", "analyzer"]
        if next_action in valid_actions:
            return next_action
        
        logger.warning(f"Invalid action {next_action}, ending")
        return END
    
    # Conditional edges from planner
    workflow.add_conditional_edges(
        "planner",
        route_from_planner,
        {
            "code_gen": "code_gen",
            "validator": "validator",
            "tester": "tester",
            "analyzer": "analyzer",
            END: END
        }
    )
    
    # All specialists return to planner
    workflow.add_edge("code_gen", "planner")
    workflow.add_edge("validator", "planner")
    workflow.add_edge("tester", "planner")
    workflow.add_edge("analyzer", "planner")
    
    # Compile workflow
    return workflow.compile()
