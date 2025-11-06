#!/usr/bin/env python3
"""Base class for all ReAct agents"""

import json
import logging
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class BaseReActAgent:
    """Base class for all ReAct agents in the system"""
    
    def __init__(
        self,
        name: str,
        slm_client,
        tools: List[BaseTool],
        system_prompt: str,
        react_template: str
    ):
        """
        Initialize base ReAct agent
        
        Args:
            name: Agent name (for logging)
            slm_client: Shared SLM API client
            tools: List of LangChain tools this agent can use
            system_prompt: System prompt defining agent role
            react_template: ReAct prompt template
        """
        self.name = name
        self.slm_client = slm_client
        self.tools = tools
        self.system_prompt = system_prompt
        self.react_template = react_template
        
        # Create prompt template
        self.prompt = PromptTemplate.from_template(react_template)
        
        # Create ReAct agent
        self.agent = create_react_agent(
            llm=slm_client,
            tools=tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5  # Internal ReAct iterations
        )
        
        logger.info(f"Initialized {name} agent with {len(tools)} tools")
    
    def invoke(self, state: Dict) -> Dict[str, Any]:
        """
        Universal invoke wrapper for ReAct agents.
        
        This method provides a consistent interface for invoking the ReAct
        executor across all agents that need reasoning capabilities.
        
        Args:
            state: Current system state (VerilogState)
            
        Returns:
            Executor result dict with 'output' key
        """
        prompt_inputs = self.format_state_for_prompt(state)
        result = self.executor.invoke(prompt_inputs)
        return result
    
    def format_state_for_prompt(self, state: Dict) -> Dict[str, Any]:
        """
        Format state for ReAct agent consumption.
        
        Converts the system state into a format suitable for the
        LangChain ReAct prompt template.
        
        Args:
            state: Current system state
            
        Returns:
            Formatted prompt inputs dict
        """
        import json
        
        return {
            "state": json.dumps(state, indent=2),
            "tools": self._format_tools(),
            "agent_scratchpad": "\n".join(state.get("agent_scratchpad", []))
        }
    
    def _format_tools(self) -> str:
        """
        Format tool descriptions for prompt.
        
        Returns:
            Formatted string of available tools
        """
        tool_descs = []
        for tool in self.tools:
            tool_descs.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tool_descs)
    
    def parse_json_output(self, output: str) -> Optional[Dict]:
        """
        Parse JSON from agent output
        
        Args:
            output: Agent output string
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            # Try to find JSON in output
            if "{" in output and "}" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                json_str = output[start:end]
                return json.loads(json_str)
            return None
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from {self.name} output")
            return None
