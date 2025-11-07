#!/usr/bin/env python3
"""Build optimized prompts for SLM code generation"""

import logging
from typing import Dict, List
from prompts.templates import *

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Construct optimized prompts for SLM code generation"""
    
    def __init__(self, use_few_shot: bool = True, max_context_files: int = 10):
        """
        Initialize prompt builder
        
        Args:
            use_few_shot: Whether to include few-shot examples
            max_context_files: Maximum number of context files to include
        """
        self.use_few_shot = use_few_shot
        self.max_context_files = max_context_files
        logger.info(f"Initialized PromptBuilder (few_shot={use_few_shot}, max_files={max_context_files})")
    
    def build_initial_prompt(self, task: str, context: Dict[str, str]) -> str:
        """
        Build initial code generation prompt
        
        Args:
            task: Task description from prompt.json
            context: Dictionary of file_path -> content
            
        Returns:
            Formatted prompt string
        """
        # Format context files (prioritized)
        context_str = self._format_context(context)
        
        # Select relevant few-shot examples
        examples_str = ""
        if self.use_few_shot:
            examples_str = self._select_examples(task)
        
        prompt = INITIAL_GENERATION_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT,
            task_description=task,
            context_files=context_str,
            few_shot_examples=examples_str
        )
        
        logger.info(f"Built initial prompt: {len(prompt)} chars")
        return prompt
    
    def build_refinement_prompt(
        self,
        task: str,
        previous_code: str,
        errors: str,
        error_category: str,
        iteration: int
    ) -> str:
        """
        Build error-driven refinement prompt
        
        Args:
            task: Original task description
            previous_code: Code from previous iteration
            errors: Error messages from tests
            error_category: Category of errors (syntax, logic, etc.)
            iteration: Current iteration number
            
        Returns:
            Formatted refinement prompt
        """
        prompt = REFINEMENT_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT,
            task_description=task,
            previous_code=previous_code,
            error_messages=errors,
            error_category=error_category,
            iteration=iteration
        )
        
        logger.info(f"Built refinement prompt: {len(prompt)} chars")
        return prompt
    
    def build_port_usage_prompt(
        self,
        current_code: str,
        unused_inputs: List[str],
        unused_outputs: List[str]
    ) -> str:
        """
        Build port usage refinement prompt (NEW)
        
        Args:
            current_code: Current code that compiles but has unused ports
            unused_inputs: List of unused input port names
            unused_outputs: List of unused output port names
            
        Returns:
            Formatted port usage prompt
        """
        unused_inputs_str = ", ".join(unused_inputs) if unused_inputs else "None"
        unused_outputs_str = ", ".join(unused_outputs) if unused_outputs else "None"
        
        prompt = PORT_USAGE_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT,
            current_code=current_code,
            unused_inputs=unused_inputs_str,
            unused_outputs=unused_outputs_str
        )
        
        logger.info(f"Built port usage prompt: {len(prompt)} chars")
        logger.info(f"  Unused inputs: {unused_inputs_str}")
        logger.info(f"  Unused outputs: {unused_outputs_str}")
        return prompt
    
    def _format_context(self, context: Dict[str, str]) -> str:
        """
        Format context files with prioritization
        
        Args:
            context: Dictionary of file_path -> content
            
        Returns:
            Formatted context string
        """
        lines = []
        file_count = 0
        
        # Priority order: docs > rtl > verif
        priority_order = ["docs/", "rtl/", "verif/"]
        
        for prefix in priority_order:
            for file_path, content in context.items():
                if file_path.startswith(prefix) and file_count < self.max_context_files:
                    # Truncate large files to 2000 chars
                    truncated_content = content[:2000]
                    if len(content) > 2000:
                        truncated_content += "\n... (truncated)"
                    
                    lines.append(f"\nFILE: {file_path}\n```\n{truncated_content}\n```")
                    file_count += 1
        
        if not lines:
            return "No context files available"
        
        logger.info(f"Formatted {file_count} context files")
        return "\n".join(lines)
    
    def _select_examples(self, task: str) -> str:
        """
        Select relevant few-shot examples based on task keywords
        
        Args:
            task: Task description
            
        Returns:
            Formatted examples string
        """
        task_lower = task.lower()
        selected = []
        
        # Keyword matching for example selection
        if any(kw in task_lower for kw in ["counter", "count"]):
            selected.append(FEW_SHOT_EXAMPLES["counter"])
        
        if any(kw in task_lower for kw in ["fifo", "buffer", "queue"]):
            selected.append(FEW_SHOT_EXAMPLES["fifo"])
        
        if any(kw in task_lower for kw in ["fsm", "state", "machine"]):
            selected.append(FEW_SHOT_EXAMPLES["fsm"])
        
        # Default: include counter example if no specific match
        if not selected:
            selected.append(FEW_SHOT_EXAMPLES["counter"])
        
        logger.info(f"Selected {len(selected)} few-shot examples")
        return "\nDESIGN PATTERNS:\n" + "\n".join(selected)
