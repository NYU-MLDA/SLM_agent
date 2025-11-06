#!/usr/bin/env python3
"""Main entry point for ReAct Multi-Agent System"""

import sys
import logging
import time
from pathlib import Path
from typing import Optional,Dict

# Import from slm_agent for reuse
from slm_agent.llm.api_client import SLMAPIClient
from slm_agent.hdl.code_manager import CodeManager
from slm_agent.utils.logger import setup_logging

# Import ReAct components
from .config.react_settings import ReActConfig
from .state.verilog_state import create_initial_state
from .agents.planner_agent import PlannerAgent
from .agents.codegen_agent import CodeGenAgent
from .agents.validator_agent import ValidatorAgent
from .agents.analyzer_agent import AnalyzerAgent
from .agents.tester_agent import TesterAgent
from .graph.workflow import create_workflow

logger = logging.getLogger(__name__)


class ReActVerilogAgent:
    """ReAct Multi-Agent System for Verilog Generation"""
    
    def __init__(self, config: Optional[ReActConfig] = None):
        """
        Initialize ReAct agent system
        
        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or ReActConfig()
        
        # Setup logging
        setup_logging('/code/rundir/agent_react_detailed.log')
        
        logger.info("=" * 80)
        logger.info("REACT MULTI-AGENT SYSTEM INITIALIZING")
        logger.info("=" * 80)
        logger.info(f"Configuration:")
        logger.info(f"  Max invocations: {self.config.max_agent_invocations}")
        logger.info(f"  Target tier: {self.config.target_tier}")
        logger.info(f"  SLM Model: {self.config.slm_model}")
        
        # Initialize shared SLM client
        self.slm_client = SLMAPIClient(
            api_url=self.config.slm_api_url,
            model=self.config.slm_model,
            max_length=self.config.slm_max_length,
            timeout=self.config.slm_timeout
        )
        
        # Initialize agents (all share same SLM client)
        logger.info("Initializing agents...")
        self.agents = {
            "planner": PlannerAgent(self.slm_client),
            "code_gen": CodeGenAgent(self.slm_client),
            "validator": ValidatorAgent(self.slm_client),
            "tester": TesterAgent(self.slm_client),
            "analyzer": AnalyzerAgent(self.slm_client)
        }
        
        logger.info(f"Initialized {len(self.agents)} agents")
        
        # Create workflow
        logger.info("Creating LangGraph workflow...")
        self.workflow = create_workflow(self.agents, self.config)
        
        logger.info("ReAct system initialized successfully")
    
    def run(self) -> int:
        """
        Execute the ReAct multi-agent workflow
        
        Returns:
            Exit code (0 for success)
        """
        try:
            logger.info("=" * 80)
            logger.info("STARTING REACT MULTI-AGENT EXECUTION")
            logger.info("=" * 80)
            
            # Step 1: Read task
            logger.info("\nStep 1: Reading task...")
            code_manager = CodeManager()
            task = code_manager.read_prompt()
            if not task:
                logger.error("No task found")
                return 0
            
            # Step 2: Gather context
            logger.info("\nStep 2: Gathering context...")
            context = code_manager.gather_context()
            
            # Step 3: Find target file
            logger.info("\nStep 3: Finding target file...")
            target_file = code_manager.find_target_file()
            logger.info(f"Target file: {target_file}")
            
            # Step 4: Create initial state
            logger.info("\nStep 4: Creating initial state...")
            initial_state = create_initial_state(
                task_description=task,
                context_files=context,
                target_file=str(target_file),
                max_invocations=self.config.max_agent_invocations
            )
            
            # Step 5: Execute workflow
            logger.info("\nStep 5: Executing ReAct workflow...")
            logger.info(f"Budget: {self.config.max_agent_invocations} invocations")
            
            start_time = time.time()
            
            # Run LangGraph workflow
            final_state = self.workflow.invoke(initial_state)
            
            execution_time = time.time() - start_time
            
            # Step 6: Report results
            logger.info("\n" + "=" * 80)
            logger.info("REACT WORKFLOW COMPLETED")
            logger.info("=" * 80)
            
            self._report_results(final_state, execution_time)
            
            # Always return 0 for benchmark compatibility
            return 0
            
        except Exception as e:
            logger.error(f"\nReAct system failed: {e}", exc_info=True)
            return 0
    
    def _report_results(self, state: Dict, execution_time: float):
        """Report final results"""
        logger.info(f"\nExecution Summary:")
        logger.info(f"  Total time: {execution_time:.2f}s")
        logger.info(f"  Agent invocations: {state['agent_invocations']}/{state['max_invocations']}")
        logger.info(f"  Code refinements: {state['code_refinements']}")
        logger.info(f"  Planner calls: {state['planner_calls']}")
        logger.info(f"  Specialist calls: {state['specialist_calls']}")
        logger.info(f"  Current tier: {state['current_tier']}")
        logger.info(f"  Success: {state['success']}")
        
        if state["success"]:
            logger.info("\nSUCCESS: Code generated and validated")
        else:
            logger.warning("\nPARTIAL SUCCESS: Code generated but not fully validated")
        
        if state["current_code"]:
            logger.info(f"  Final code: {len(state['current_code'])} bytes")


def main():
    """Main entry point"""
    agent = ReActVerilogAgent()
    return agent.run()


if __name__ == "__main__":
    sys.exit(main())
