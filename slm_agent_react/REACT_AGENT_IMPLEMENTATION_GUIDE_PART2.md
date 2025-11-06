# ReAct Multi-Agent System - Implementation Guide (Part 2)

This continues from REACT_AGENT_IMPLEMENTATION_GUIDE.md

---

## Feedback Loop Mechanics (Continued)

### 1. Error Feedback Loop (Complete)

```
┌─────────────────────────────────────────────────────┐
│ ITERATION N                                          │
│ CodeGen generates code                              │
│         ↓                                            │
│ Tester runs tests → Errors detected                │
│         ↓                                            │
│ State updated with errors                           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ ITERATION N+1                                        │
│ Planner sees errors → Decision: "analyze"           │
│         ↓                                            │
│ Analyzer categorizes errors → "undeclared"          │
│         ↓                                            │
│ State updated with category                         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ ITERATION N+2                                        │
│ Planner sees categorized errors                     │
│         ↓                                            │
│ Decision: "code_gen" → fix undeclared signals       │
│         ↓                                            │
│ CodeGen refines code with declarations              │
│         ↓                                            │
│ State updated with new code                         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ ITERATION N+3                                        │
│ Planner → Decision: "test" → verify fixes           │
│         ↓                                            │
│ Tester runs tests → Success or new errors           │
│         ↓                                            │
│ State updated with results                          │
└─────────────────────────────────────────────────────┘
```

### 2. Quality Tier Progression

```
Tier 0: No Valid Code
    ↓
    CodeGen generates initial code
    ↓
Tier 1: Compiles (Structure Valid)
    ↓
    Validator checks ports → Issues found
    ↓
    CodeGen fixes port usage
    ↓
Tier 2: All Ports Used
    ↓
    Tester runs test suite → Some tests fail
    ↓
    Analyzer categorizes failures
    ↓
    CodeGen refines logic
    ↓
    Tester re-runs tests → All pass
    ↓
Tier 3: Tests Pass ✅ COMPLETE
```

### 3. Budget-Aware Adaptation

The system adapts behavior based on remaining budget:

```
GREEN ZONE (40-50 invocations remaining):
├─ Strategy: Exploration and refinement
├─ Behavior: Try multiple approaches
├─ Quality: Aim for Tier 3 (tests passing)
└─ Actions: code_gen → validate → test → analyze → refine

YELLOW ZONE (15-39 invocations remaining):
├─ Strategy: Focused improvement
├─ Behavior: Target known issues
├─ Quality: Aim for Tier 2 minimum
└─ Actions: Prioritize critical fixes

RED ZONE (1-14 invocations remaining):
├─ Strategy: Quick wins
├─ Behavior: Accept current quality
├─ Quality: Return best achieved
└─ Actions: Final polish only
```

---

## Workflow Details

### Complete Execution Example

**Task**: "Generate a 4-bit up counter with enable"

#### Iteration 1: Initial Generation
```
Planner Decision:
  Thought: No code exists, need initial generation
  → Action: "code_gen"

CodeGen Execution:
  Thought: Check generation type
  Action: check_if_initial_generation
  Observation: {"is_initial": true}
  
  Thought: Get counter pattern
  Action: get_design_pattern("counter")
  Observation: {pattern: "module counter #(..."}
  
  Thought: Adapt pattern to 4-bit with enable
  Final Answer: {code: "module counter_4bit(...", method: "initial"}

State Update:
  current_code = "module counter_4bit(...)..."
  tier_achieved = 0
  invocations = 1
```

#### Iteration 2: Structure Validation
```
Planner Decision:
  Thought: Code exists, validate structure
  → Action: "validate"

Validator Execution:
  Check structure: PASS
  Check ports: enable input declared but not used
  → Tier 1 achieved (compiles)
  → Issue: unused port 'enable'

State Update:
  tier_achieved = 1
  port_analysis = {unused_inputs: ["enable"]}
  invocations = 2
```

#### Iteration 3: Port Usage Analysis
```
Planner Decision:
  Thought: Port issue detected, need analysis
  → Action: "code_gen" (fix ports)

CodeGen Execution:
  Thought: Check generation type
  Observation: {is_initial: false}
  
  Thought: Check for port issues
  Action: refine_code_for_port_usage
  Observation: {strategy: "Use enable in counter logic"}
  
  Thought: Add enable to counting logic
  Final Answer: {code: "if (enable) count <= ...", method: "port_usage"}

State Update:
  current_code = "module counter_4bit (updated)"
  invocations = 3
```

#### Iteration 4: Re-validation
```
Planner Decision:
  Thought: Code updated, re-validate
  → Action: "validate"

Validator Execution:
  Check structure: PASS
  Check ports: All ports used
  → Tier 2 achieved

State Update:
  tier_achieved = 2
  port_analysis = {all_ports_used: true}
  invocations = 4
```

#### Iteration 5: Testing
```
Planner Decision:
  Thought: Structure valid, run tests
  → Action: "test"

Tester Execution:
  Write code to file
  Run Verilator: PASS
  Run cocotb tests: ALL PASS
  → Tier 3 achieved

State Update:
  tier_achieved = 3
  tests_passed = true
  invocations = 5
```

#### Iteration 6: Completion
```
Planner Decision:
  Thought: Tier 3 achieved, task complete
  → Action: "complete"

Final Output:
  Code: [Working 4-bit counter with enable]
  Tier: 3/3
  Invocations Used: 5/50
  Success: TRUE
```

---

## Tool System

### Tool Architecture

```
┌────────────────────────────────────────────────┐
│              LangChain Tool Interface           │
│                                                 │
│  @tool decorator wraps Python functions        │
│  Provides:                                      │
│  • name: Tool identifier                       │
│  • description: What the tool does             │
│  • args_schema: Expected input format          │
│  • func: Actual implementation                 │
└────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│            Tool Registration                    │
│                                                 │
│  Tools registered with agents during init:     │
│  agent = BaseReActAgent(                        │
│      tools=[tool1, tool2, tool3]               │
│  )                                              │
└────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│          Tool Invocation in ReAct               │
│                                                 │
│  Agent decides to use tool:                     │
│  Action: tool_name                              │
│  Action Input: {"param": "value"}              │
│                                                 │
│  Executor calls tool function                   │
│  Returns result as Observation                  │
└────────────────────────────────────────────────┘
```

### PlannerAgent Tools

**1. analyze_budget_status**
```python
@tool
def analyze_budget_status(invocations_used: int, max_invocations: int) -> Dict:
    """
    Analyze computational budget status
    
    Returns budget zone and recommendations:
    - green: 80-100% remaining
    - yellow: 30-79% remaining  
    - red: 0-29% remaining
    """
    remaining = max_invocations - invocations_used
    percentage = (remaining / max_invocations) * 100
    
    if percentage >= 80:
        zone = "green"
        recommendation = "continue_exploration"
    elif percentage >= 30:
        zone = "yellow"
        recommendation = "focus_on_improvements"
    else:
        zone = "red"
        recommendation = "quick_wins_only"
    
    return {
        "zone": zone,
        "remaining": remaining,
        "used": invocations_used,
        "percentage": percentage,
        "recommendation": recommendation
    }
```

**2. categorize_errors**
```python
@tool
def categorize_errors(errors: str) -> Dict:
    """
    Categorize error messages by type
    
    Categories:
    - syntax, undeclared, type, width, latch, general
    """
    error_lower = errors.lower()
    
    if "syntax error" in error_lower or ";" in errors:
        return {"category": "syntax", "priority": "high"}
    elif "undeclared" in error_lower or "not declared" in error_lower:
        return {"category": "undeclared", "priority": "high"}
    elif "type mismatch" in error_lower:
        return {"category": "type", "priority": "medium"}
    # ... more patterns
    
    return {"category": "general", "priority": "medium"}
```

### CodeGenAgent Tools

**1. check_if_initial_generation**
```python
@tool
def check_if_initial_generation(state_json: str) -> Dict:
    """Determine if initial generation or refinement"""
    state = json.loads(state_json)
    is_initial = not bool(state.get("current_code", ""))
    
    return {
        "is_initial": is_initial,
        "reason": "No existing code" if is_initial else "Code exists",
        "iteration": state.get("iteration", 0)
    }
```

**2. get_design_pattern**
```python
@tool
def get_design_pattern(pattern_type: str) -> Dict:
    """Retrieve design pattern example"""
    patterns = {
        "counter": "module counter #(parameter WIDTH=4)...",
        "fifo": "module fifo #(parameter DEPTH=8)...",
        "fsm": "module fsm (input clk, rst...)..."
    }
    
    return {
        "pattern": patterns.get(pattern_type, patterns["counter"]),
        "description": f"{pattern_type} implementation example",
        "pattern_type": pattern_type
    }
```

**3. refine_code_for_errors**
```python
@tool
def refine_code_for_errors(code: str, errors: str, error_category: str) -> Dict:
    """Analyze errors and provide refinement strategy"""
    strategies = {
        "syntax": {
            "strategy": "Fix syntax errors",
            "focus_areas": ["Check semicolons", "Verify keywords", "Check parentheses"]
        },
        "undeclared": {
            "strategy": "Add missing declarations",
            "focus_areas": ["Declare signals", "Add wire/reg", "Check names"]
        },
        # ... more categories
    }
    
    return strategies.get(error_category, strategies["general"])
```

**4. refine_code_for_port_usage**
```python
@tool
def refine_code_for_port_usage(code: str, unused_inputs: str, unused_outputs: str) -> Dict:
    """Provide strategy to fix unused ports"""
    actions = []
    
    if unused_inputs:
        inputs = unused_inputs.split(",")
        actions.append(f"Use inputs in logic: {', '.join(inputs)}")
    
    if unused_outputs:
        outputs = unused_outputs.split(",")
        actions.append(f"Assign values to: {', '.join(outputs)}")
    
    return {
        "strategy": "Fix unused port issues for Tier 2",
        "actions": actions,
        "priority": "high"
    }
```

---

## Implementation Examples

### Example 1: Simple Counter Task

**Input**: "Generate a 4-bit counter"

**Execution Trace**:
```
1. Planner → code_gen (no code exists)
2. CodeGen → initial generation with pattern
3. Planner → validate (check structure)
4. Validator → Tier 1, all ports used
5. Planner → test (run tests)
6. Tester → Tier 3, tests pass
7. Planner → complete

Result: Tier 3 in 6 invocations
```

### Example 2: Complex Task with Errors

**Input**: "Generate FIFO with configurable depth"

**Execution Trace**:
```
1. Planner → code_gen
2. CodeGen → initial generation
3. Planner → validate
4. Validator → Tier 1, unused ports detected
5. Planner → code_gen (fix ports)
6. CodeGen → port refinement
7. Planner → validate  
8. Validator → Tier 2
9. Planner → test
10. Tester → Lint errors: "signal undeclared"
11. Planner → analyze
12. Analyzer → category: "undeclared"
13. Planner → code_gen (fix errors)
14. CodeGen → add declarations
15. Planner → test
16. Tester → Tests fail: timing issue
17. Planner → analyze
18. Analyzer → category: "general"
19. Planner → code_gen (fix logic)
20. CodeGen → refine timing logic
21. Planner → test
22. Tester → Tier 3, all tests pass
23. Planner → complete

Result: Tier 3 in 22 invocations
```

### Example 3: Budget Exhaustion

**Input**: "Complex protocol implementation"

**Execution Trace**:
```
1-10: Multiple refinement cycles
11-30: Error fixes and improvements
31-45: Reaching Tier 2
46: Budget = yellow zone
47: Planner → prioritize critical issues
48: CodeGen → targeted fix
49: Validator → Tier 2 confirmed
50: Budget exhausted

Result: Tier 2 (best effort) in 50 invocations
```

---

## Configuration & Tuning

### System Configuration

**File**: `slm_agent_react/config/react_settings.py`

```python
class ReActConfig:
    """Configuration for ReAct multi-agent system"""
    
    # Budget Management
    max_agent_invocations: int = 50
    budget_green_threshold: float = 0.8    # 80% remaining
    budget_yellow_threshold: float = 0.3   # 30% remaining
    
    # Quality Tiers
    tier_structure_valid: int = 1
    tier_ports_used: int = 2
    tier_tests_pass: int = 3
    target_tier: int = 3
    
    # Agent Limits
    planner_max_iterations: int = 5      # Per invocation
    codegen_max_iterations: int = 5      # Per invocation
    
    # Timeouts
    test_timeout: int = 120              # Seconds
    lint_timeout: int = 30               # Seconds
    
    # SLM Parameters
    temperature_initial: float = 0.7     # Initial generation
    temperature_refinement: float = 0.6  # Refinement
    max_tokens: int = 2048
    
    # Workflow Control
    max_code_generations: int = 10       # Max code generation attempts
    max_refinement_cycles: int = 3       # Max refinement per issue
    enable_port_validation: bool = True
    enable_test_execution: bool = True
```

### Tuning Guidelines

#### 1. Budget Allocation

**Tight Budget (25-35 invocations)**:
```python
max_agent_invocations = 30
budget_yellow_threshold = 0.4  # More aggressive
target_tier = 2                # Accept lower quality
```

**Generous Budget (60-100 invocations)**:
```python
max_agent_invocations = 80
budget_yellow_threshold = 0.2  # More exploration
target_tier = 3                # Demand high quality
```

#### 2. Temperature Settings

**Conservative (Consistent output)**:
```python
temperature_initial = 0.5
temperature_refinement = 0.4
```

**Exploratory (Creative solutions)**:
```python
temperature_initial = 0.8
temperature_refinement = 0.7
```

#### 3. Quality vs Speed Trade-off

**Speed Priority**:
```python
target_tier = 1  # Accept compilation
enable_port_validation = False
max_refinement_cycles = 1
```

**Quality Priority**:
```python
target_tier = 3  # Demand tests pass
enable_port_validation = True
max_refinement_cycles = 5
```

---

## Performance Metrics

### Success Metrics

**Tier Achievement Rates** (typical):
- Tier 1 (Compiles): 95%
- Tier 2 (Ports Used): 80%
- Tier 3 (Tests Pass): 60-70%

**Invocation Efficiency**:
- Simple tasks: 5-15 invocations
- Medium tasks: 15-30 invocations
- Complex tasks: 30-50 invocations

**Budget Utilization**:
- Optimal range: 40-60% of budget
- Under-utilization (<30%): May indicate early success or overly simple task
- Over-utilization (>90%): Task complexity high or inefficient reasoning

### Monitoring Points

**Key Metrics to Track**:
1. Average invocations per tier
2. Success rate by task complexity
3. Budget zone distribution
4. Error category frequencies
5. Tool usage patterns
6. Refinement cycle lengths

---

## Troubleshooting

### Common Issues

**1. Agent Stuck in Loop**
```
Symptom: Repeating same action
Cause: State not updating properly
Solution: Check state merge logic after agent execution
```

**2. Budget Exhaustion Without Progress**
```
Symptom: Reaching limit at Tier 0/1
Cause: Inefficient reasoning or hard task
Solution: Review ReAct prompts, increase temperature slightly
```

**3. Tools Not Being Used**
```
Symptom: Agent not calling expected tools
Cause: Tool descriptions unclear or prompt issues
Solution: Improve tool descriptions, check prompt template
```

**4. JSON Parsing Failures**
```
Symptom: parse_json_output returns None
Cause: Agent not following output format
Solution: Strengthen output format instructions in prompt
```

---

## Advanced Topics

### 1. Custom Tool Development

To add a new tool to CodeGenAgent:

```python
@tool
def my_custom_tool(param1: str, param2: int) -> Dict:
    """
    Clear description of what this tool does.
    Agent will see this description.
    """
    # Implementation
    result = process(param1, param2)
    
    return {
        "result": result,
        "metadata": {...}
    }

# Register in CodeGenAgent.__init__
tools = [
    existing_tools...,
    my_custom_tool
]
```

### 2. Prompt Engineering

**Effective Prompt Structure**:
1. Clear role definition
2. Available tools list
3. Step-by-step reasoning guide
4. Output format specification
5. Examples (if helpful)

### 3. State Extension

To add new state fields:

```python
# In state initialization
state["my_new_field"] = initial_value

# Update after agent action
state["my_new_field"] = agent_result.get("my_field")

# Use in agent prompts
"Current my_field: {my_new_field}"
```

---

## Conclusion

The ReAct Multi-Agent System provides a powerful, flexible framework for Verilog code generation through:

- **Intelligent Reasoning**: ReAct pattern enables thoughtful decision-making
- **Specialized Expertise**: Each agent excels at its specific role
- **Continuous Improvement**: Feedback loops drive iterative refinement
- **Budget Awareness**: Adaptive behavior based on resource constraints
- **Quality Assurance**: Progressive tiers ensure code quality

**Key Takeaways**:
1. Planner orchestrates, specialists execute
2. State carries all context between agents
3. Tools enable informed reasoning
4. Feedback loops drive improvement
5. Budget management ensures efficiency

For questions or contributions, refer to the project documentation or contact the development team.

---

**End of Implementation Guide**
