#!/usr/bin/env python3
"""Base class for deterministic specialist agents (no ReAct needed)"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseSpecialistAgent:
    """
    Base class for specialist agents that perform deterministic operations.
    
    These agents don't need ReAct reasoning loops or tool-based execution.
    They implement straightforward operations like validation, testing, and analysis.
    
    Examples:
        - ValidatorAgent: Runs validation checks
        - TesterAgent: Executes tests
        - AnalyzerAgent: Categorizes errors
    """
    
    def __init__(self, name: str, slm_client):
        """
        Initialize specialist agent
        
        Args:
            name: Agent name (for logging)
            slm_client: Shared SLM API client (for potential future use)
        """
        self.name = name
        self.slm_client = slm_client
        
        logger.info(f"Initialized {name} specialist agent")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
