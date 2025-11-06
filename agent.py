#!/usr/bin/env python3
"""
Unified Agent Dispatcher - Routes between Iterative and ReAct systems

This is the main entry point that allows choosing between:
- System A: Modular Iterative Agent (slm_agent/)
- System B: ReAct Multi-Agent System (slm_agent_react/)
"""

import sys
import os
import argparse
import logging
from enum import Enum
from typing import Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Available agent system types"""
    ITERATIVE = "iterative"     # System A: Fast, proven, 3 iterations
    REACT = "react"            # System B: Advanced, adaptive, 50 invocations
    AUTO = "auto"              # Automatically select based on task complexity


class UnifiedAgentDispatcher:
    """
    Unified dispatcher that routes to appropriate agent system.
    
    Selection Strategies:
    1. Explicit: User specifies which system to use
    2. Auto: Analyzes task and selects optimal system
    3. Environment variable: AGENT_TYPE=iterative|react
    """
    
    def __init__(self, agent_type: AgentType = AgentType.AUTO):
        """
        Initialize dispatcher
        
        Args:
            agent_type: Which agent system to use (or AUTO for automatic)
        """
        self.agent_type = agent_type
        logger.info("=" * 80)
        logger.info("UNIFIED AGENT DISPATCHER")
        logger.info("=" * 80)
        logger.info(f"Agent type: {agent_type.value}")
    
    def run(self) -> int:
        """
        Execute the selected agent system
        
        Returns:
            Exit code (0 for success)
        """
        # Determine which system to use
        selected_system = self._select_system()
        
        logger.info("=" * 80)
        logger.info(f"SELECTED SYSTEM: {selected_system.value.upper()}")
        logger.info("=" * 80)
        
        # Route to appropriate system
        if selected_system == AgentType.ITERATIVE:
            return self._run_iterative()
        elif selected_system == AgentType.REACT:
            return self._run_react()
        else:
            logger.error(f"Unknown system: {selected_system}")
            return 1
    
    def _select_system(self) -> AgentType:
        """
        Select which system to use based on configuration or auto-detection
        
        Returns:
            Selected AgentType
        """
        # Check environment variable first
        env_agent = os.getenv("AGENT_TYPE", "").lower()
        if env_agent == "iterative":
            logger.info("Using ITERATIVE system (from environment variable)")
            return AgentType.ITERATIVE
        elif env_agent == "react":
            logger.info("Using REACT system (from environment variable)")
            return AgentType.REACT
        
        # If explicit type set, use it
        if self.agent_type in [AgentType.ITERATIVE, AgentType.REACT]:
            return self.agent_type
        
        # Default to iterative
        logger.info("Defaulting to REACT system")
        return AgentType.REACT
    
    
    def _run_iterative(self) -> int:
        """Run the iterative agent system (System A)"""
        logger.info("\n" + "=" * 80)
        logger.info("LAUNCHING ITERATIVE AGENT SYSTEM (System A)")
        logger.info("=" * 80)
        logger.info("Features: 3 iterations, port validation, optimized prompts")
        logger.info("")
        
        try:
            from slm_agent.main import main
            return main()
        except Exception as e:
            logger.error(f"Iterative system failed: {e}")
            return 1
    
    def _run_react(self) -> int:
        """Run the ReAct multi-agent system (System B)"""
        logger.info("\n" + "=" * 80)
        logger.info("LAUNCHING REACT MULTI-AGENT SYSTEM (System B)")
        logger.info("=" * 80)
        logger.info("Features: 5 agents, 50 invocations, progressive tiers, explainable reasoning")
        logger.info("")
        
        try:
            from slm_agent_react.main import main
            return main()
        except Exception as e:
            logger.error(f"ReAct system failed: {e}")
            logger.warning("Falling back to iterative system...")
            return self._run_iterative()


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Unified SLM Agent Dispatcher - Choose between Iterative and ReAct systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py                    # Auto-select based on task complexity
  python agent.py --type iterative   # Force iterative system (3 iterations)
  python agent.py --type react       # Force ReAct system (50 invocations)
  
  # Or via environment variable:
  export AGENT_TYPE=react
  python agent.py

System Comparison:
  Iterative (System A):
    - Fast: 1-3 SLM calls
    - Cost-effective
    - Proven and stable
    - Best for: Simple to moderate tasks
    
  ReAct (System B):
    - Intelligent: 5-50 SLM calls (adaptive)
    - High quality
    - Explainable reasoning
    - Best for: Complex tasks requiring exploration
"""
    )
    
    parser.add_argument(
        "--type",
        choices=["iterative", "react", "auto"],
        default="react",
        help="Agent system type (default: react)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Map argument to enum
    agent_type_map = {
        "iterative": AgentType.ITERATIVE,
        "react": AgentType.REACT,
        "auto": AgentType.AUTO
    }
    
    agent_type = agent_type_map[args.type]
    
    # Create and run dispatcher
    dispatcher = UnifiedAgentDispatcher(agent_type=agent_type)
    exit_code = dispatcher.run()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
