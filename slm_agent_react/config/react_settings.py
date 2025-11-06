#!/usr/bin/env python3
"""Configuration for ReAct Multi-Agent System"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReActConfig:
    """Configuration for ReAct multi-agent system with 50-invocation budget"""
    
    # Budget settings (PRIMARY CONSTRAINT)
    max_agent_invocations: int = 50        # Total agent calls allowed
    max_code_refinements: int = 10         # Max code generation calls
    max_consecutive_failures: int = 5       # Stop if 5 fails in a row
    max_time_seconds: int = 900            # 15 minute timeout
    
    # Progressive quality tiers
    tier1_compile: int = 10                # Target: Code compiles
    tier2_complete: int = 25               # Target: All ports used
    tier3_tested: int = 40                 # Target: Tests pass
    tier4_optimal: int = 50                # Target: Optimized code
    
    # SLM settings (single endpoint - reads from environment variables)
    slm_api_url: str = field(default_factory=lambda: os.getenv("SLM_API_URL", "http://host.docker.internal:8000"))
    slm_model: str = field(default_factory=lambda: os.getenv("SLM_MODEL", "deepseek"))
    slm_max_length: int = field(default_factory=lambda: int(os.getenv("SLM_MAX_LENGTH", "8192")))
    slm_timeout: int = field(default_factory=lambda: int(os.getenv("SLM_TIMEOUT", "300")))
    
    # Advanced features (FUTURE - placeholders for planned enhancements)
    # Note: These flags are defined but not yet implemented in current version
    enable_self_reflection: bool = False    # TODO: Agents critique own work
    enable_alternative_strategies: bool = False  # TODO: Try different approaches
    enable_progressive_refinement: bool = False  # TODO: Multi-phase improvement
    enable_optimization_phase: bool = False      # TODO: Final optimization pass
    
    # Quality gates
    require_port_validation: bool = True
    require_test_pass: bool = True
    require_synthesis_check: bool = False
    
    # Early exit strategies
    exit_on_tier3: bool = True             # Stop at Tier 3 if achieved early
    exit_on_first_success: bool = False    # Continue improving
    allow_partial_success: bool = True     # Accept compilable code
    
    # Optimization
    enable_caching: bool = True
    smart_routing: bool = True
    verbose_logging: bool = True
    
    def validate(self) -> None:
        """Validate configuration"""
        assert self.max_agent_invocations > 0, "max_agent_invocations must be positive"
        assert self.max_code_refinements > 0, "max_code_refinements must be positive"
        assert self.tier1_compile < self.tier2_complete < self.tier3_tested <= self.tier4_optimal
    
    def __post_init__(self):
        """Validate on initialization"""
        self.validate()
