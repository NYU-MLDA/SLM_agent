# ReAct Multi-Agent System - Implementation Guide

**Version**: 2.0  
**Date**: November 5, 2025  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [ReAct Agent Infrastructure](#react-agent-infrastructure)
4. [Agent Specifications](#agent-specifications)
5. [State Management](#state-management)
6. [Feedback Loop Mechanics](#feedback-loop-mechanics)
7. [Workflow Details](#workflow-details)
8. [Tool System](#tool-system)
9. [Implementation Examples](#implementation-examples)
10. [Configuration & Tuning](#configuration--tuning)

---

## System Overview

### What is the ReAct Multi-Agent System?

The ReAct Multi-Agent System is a sophisticated Verilog code generation framework that combines:
- **ReAct (Reasoning + Acting)** paradigm for intelligent decision-making
- **Multi-agent coordination** for specialized task handling
- **Progressive quality tiers** for iterative improvement
- **Budget-aware execution** for cost control

### Core Philosophy

The system operates on three principles:
1. **Separation of Concerns**: Each agent has a specific role
2. **Reasoning Before Acting**: Agents think through problems before taking action
3. **Continuous Feedback**: Each action informs the next decision

---

## Architecture Diagrams

### 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER TASK INPUT                              │
│                  "Generate a 4-bit counter"                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REACT MULTI-AGENT SYSTEM                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PLANNER AGENT (ReAct)                       │   │
│  │  - Analyzes current state                                │   │
│  │  - Decides next action                                   │   │
│  │  - Manages budget                                        │   │
│  │  - Controls workflow                                     │   │
│  └─────────┬──────────────────────────────────────┬────────┘   │
│            │                                       │             │
│            ├───────────┐              ┌───────────┤             │
│            ▼           ▼              ▼           ▼             │
│  ┌─────────────┐ ┌─────────┐  ┌─────────┐ ┌──────────┐        │
│  │  CODEGEN    │ │VALIDATOR│  │ TESTER  │ │ ANALYZER │        │
│  │   (ReAct)   │ │(Special)│  │(Special)│ │(Special) │        │
│  │             │ │         │  │         │ │          │        │
│  │ Generates   │ │Validates│  │  Runs   │ │Categorize│        │
│  │ Verilog     │ │Structure│  │ Tests   │ │  Errors  │        │
│  │ Code        │ │& Ports  │  │         │ │          │        │
│  └─────┬───────┘ └────┬────┘  └────┬────┘ └────┬─────┘        │
│        │              │            │           │               │
│        └──────────────┴────────────┴───────────┘               │
│                       │                                         │
│                       ▼                                         │
│            ┌──────────────────────┐                            │
│            │   VERILOG STATE      │                            │
│            │  - Current code      │                            │
│            │  - Errors            │                            │
│            │  - Quality tier      │                            │
│            │  - Iteration count   │                            │
│            └──────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: VERILOG CODE                          │
│                    Quality Tier: 1/2/3                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2. ReAct Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BaseReActAgent Infrastructure                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. INITIALIZATION                                      │    │
│  │     - Register Tools                                    │    │
│  │     - Create LangChain Agent                           │    │
│  │     - Build AgentExecutor                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  2. INVOCATION (agent.invoke(state))                   │    │
│  │     ├─ Format state for prompt                         │    │
│  │     ├─ Add available tools list                        │    │
│  │     └─ Initialize agent scratchpad                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  3. REACT REASONING LOOP (max 5 iterations)            │    │
│  │                                                          │    │
│  │     ┌──────────────────────────────────────────┐       │    │
│  │     │  Thought: [Agent analyzes situation]     │       │    │
│  │     └────────────────┬─────────────────────────┘       │    │
│  │                      │                                  │    │
│  │                      ▼                                  │    │
│  │     ┌──────────────────────────────────────────┐       │    │
│  │     │  Action: tool_name                       │       │    │
│  │     │  Action Input: {"param": "value"}       │       │    │
│  │     └────────────────┬─────────────────────────┘       │    │
│  │                      │                                  │    │
│  │                      ▼                                  │    │
│  │     ┌──────────────────────────────────────────┐       │    │
│  │     │  Execute Tool → Get Result               │       │    │
│  │     └────────────────┬─────────────────────────┘       │    │
│  │                      │                                  │    │
│  │                      ▼                                  │    │
│  │     ┌──────────────────────────────────────────┐       │    │
│  │     │  Observation: [Tool output]              │       │    │
│  │     └────────────────┬─────────────────────────┘       │    │
│  │                      │                                  │    │
│  │                      ├─→ Loop continues if needed      │    │
│  │                      │   (more thoughts/actions)       │    │
│  │                      │                                  │    │
│  │                      ▼                                  │    │
│  │     ┌──────────────────────────────────────────┐       │    │
│  │     │  Final Answer: [Agent's conclusion]      │       │    │
│  │     └──────────────────────────────────────────┘       │    │
│  │                                                          │    │
│  └────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  4. RESULT PARSING                                      │    │
│  │     - Extract JSON from output                         │    │
│  │     - Parse structured result                          │    │
│  │     - Return to caller                                 │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Complete Workflow Diagram

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ INITIALIZATION PHASE                                     │
│ - Read task from prompt.json                            │
│ - Gather context files                                  │
│ - Initialize VerilogState                               │
│ - Set budget: 50 invocations                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ MAIN LOOP (while budget > 0 and not complete)           │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ STEP 1: PLANNER DECISION                        │    │
│  │ ┌────────────────────────────────────────┐     │    │
│  │ │ PlannerAgent.decide_next_action(state) │     │    │
│  │ │                                         │     │    │
│  │ │ ReAct Reasoning:                        │     │    │
│  │ │ • Thought: Analyze current state        │     │    │
│  │ │ • Action: analyze_budget_status         │     │    │
│  │ │ • Observation: Budget zone info         │     │    │
│  │ │ • Thought: Determine next agent         │     │    │
│  │ │ • Final Answer: {"next_action": "..."}  │     │    │
│  │ └────────────────────────────────────────┘     │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                      │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────┐    │
│  │ STEP 2: EXECUTE SPECIALIST OR REACT AGENT      │    │
│  │                                                 │    │
│  │ IF next_action == "code_gen":                  │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │ CodeGenAgent.generate_code(state)    │     │    │
│  │  │                                       │     │    │
│  │  │ ReAct Reasoning:                      │     │    │
│  │  │ • Check if initial or refinement      │     │    │
│  │  │ • Get design patterns if needed       │     │    │
│  │  │ • Analyze errors if refinement        │     │    │
│  │  │ • Generate/refine code                │     │    │
│  │  │ • Return: {"code": "...", ...}        │     │    │
│  │  └──────────────────────────────────────┘     │    │
│  │                                                 │    │
│  │ ELIF next_action == "validate":                │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │ ValidatorAgent.validate(state)        │     │    │
│  │  │ • Check structure                     │     │    │
│  │  │ • Analyze port usage                  │     │    │
│  │  │ • Return: {"valid": bool, ...}        │     │    │
│  │  └──────────────────────────────────────┘     │    │
│  │                                                 │    │
│  │ ELIF next_action == "test":                    │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │ TesterAgent.test(state)               │     │    │
│  │  │ • Write code to file                  │     │    │
│  │  │ • Run Verilator lint                  │     │    │
│  │  │ • Run cocotb tests                    │     │    │
│  │  │ • Return: {"passed": bool, ...}       │     │    │
│  │  └──────────────────────────────────────┘     │    │
│  │                                                 │    │
│  │ ELIF next_action == "analyze":                 │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │ AnalyzerAgent.analyze(state)          │     │    │
│  │  │ • Categorize errors                   │     │    │
│  │  │ • Generate suggestions                │     │    │
│  │  │ • Return: {"category": "...", ...}    │     │    │
│  │  └──────────────────────────────────────┘     │    │
│  │                                                 │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                      │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────┐    │
│  │ STEP 3: UPDATE STATE                            │    │
│  │ • Merge agent results into state                │    │
│  │ • Increment invocation counter                  │    │
│  │ • Update tier achieved                          │    │
│  │ • Record actions in scratchpad                  │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                      │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────┐    │
│  │ STEP 4: CHECK COMPLETION CONDITIONS             │    │
│  │ • Tier 3 achieved? (tests pass)                 │    │
│  │ • Budget exhausted?                             │    │
│  │ • Max iterations reached?                       │    │
│  │ • Planner says "complete"?                      │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                      │
│                   └─→ Loop back or exit                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ COMPLETION PHASE                                         │
│ - Write final code to file                              │
│ - Generate report                                        │
│ - Log statistics                                         │
│ - Return result                                          │
└─────────────────────────────────────────────────────────┘
  │
  ▼
END
```

---

## ReAct Agent Infrastructure

### BaseReActAgent Class

The foundation for all ReAct-enabled agents.

```python
class BaseReActAgent:
    """Base class providing ReAct infrastructure"""
    
    def __init__(self, name, slm_client, tools, system_prompt, react_template):
        # 1. Store configuration
        self.name = name
        self.slm_client = slm_client
        self.tools = tools
        
        # 2. Create LangChain components
        self.prompt = PromptTemplate.from_template(react_template)
        self.agent = create_react_agent(llm=slm_client, tools=tools, prompt=self.prompt)
        
        # 3. Create executor (handles ReAct loop)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5  # Internal ReAct loop limit
        )
```

#### Key Methods

**1. invoke(state) - Universal ReAct Invocation**
```python
def invoke(self, state: Dict) -> Dict[str, Any]:
    """
    Execute ReAct reasoning loop
    
    Flow:
    1. Format state for prompt
    2. Add tools list
    3. Initialize scratchpad
    4. Invoke executor
    5. Return result
    """
    prompt_inputs = self.format_state_for_prompt(state)
    result = self.executor.invoke(prompt_inputs)
    return result
```

**2. format_state_for_prompt(state) - State Formatting**
```python
def format_state_for_prompt(self, state: Dict) -> Dict[str, Any]:
    """
    Convert VerilogState to LangChain-compatible format
    
    Output structure:
    {
        "state": "JSON string of current state",
        "tools": "Formatted list of available tools",
        "agent_scratchpad": "History of thoughts/actions"
    }
    """
    return {
        "state": json.dumps(state, indent=2),
        "tools": self._format_tools(),
        "agent_scratchpad": "\n".join(state.get("agent_scratchpad", []))
    }
```

**3. parse_json_output(output) - Result Parsing**
```python
def parse_json_output(self, output: str) -> Optional[Dict]:
    """
    Extract JSON from agent's Final Answer
    
    Handles cases where JSON is embedded in text:
    "Here is the result: {\"key\": \"value\"}"
    
    Returns: Parsed dictionary or None
    """
    if "{" in output and "}" in output:
        start = output.find("{")
        end = output.rfind("}") + 1
        json_str = output[start:end]
        return json.loads(json_str)
    return None
```

---

## Agent Specifications

### 1. PlannerAgent (ReAct)

**Role**: Master coordinator and decision-maker

**Capabilities**:
- Analyzes current system state
- Decides which specialist agent to invoke next
- Manages computational budget
- Tracks quality tier progression
- Determines task completion

**ReAct Flow**:
```
Thought: Let me analyze the current situation
  - Current code exists? Yes/No
  - Tests passing? Yes/No
  - Budget remaining? X invocations
  - Tier achieved? X/3

Action: analyze_budget_status
Action Input: {"invocations_used": 10, "max_invocations": 50}

Observation: {
  "zone": "green",
  "remaining": 40,
  "recommendation": "continue_exploration"
}

Thought: Budget is healthy. Code exists with errors.
  Need to analyze errors before refinement.

Final Answer: {
  "next_action": "analyze",
  "reasoning": "Categorize errors to guide refinement"
}
```

**Tools**:
- `analyze_budget_status`: Check budget zone (green/yellow/red)
- `categorize_errors`: Classify error types

**Decision Logic**:
```
IF no code exists:
  → action = "code_gen" (initial generation)

ELIF code exists AND has errors:
  → action = "analyze" (understand errors)
  → then action = "code_gen" (fix errors)

ELIF code exists AND structure invalid:
  → action = "validate" (check structure/ports)
  → then action = "code_gen" (fix issues)

ELIF code compiles BUT tests not run:
  → action = "test" (run test suite)

ELIF tests fail:
  → action = "analyze" → "code_gen"

ELIF tests pass (Tier 3):
  → action = "complete"

ELSE:
  → action based on budget and tier
```

---

### 2. CodeGenAgent (ReAct)

**Role**: Verilog code generation and refinement specialist

**Capabilities**:
- Generates initial Verilog code from task description
- Refines code based on errors
- Fixes port usage issues
- Applies design patterns
- Adapts strategy based on feedback

**ReAct Flow for Initial Generation**:
```
Thought: Let me check if this is initial generation or refinement

Action: check_if_initial_generation
Action Input: {"state_json": "{\"current_code\": \"\", ...}"}

Observation: {
  "is_initial": true,
  "reason": "No existing code found"
}

Thought: This is initial generation. I should get a relevant pattern.

Action: get_design_pattern
Action Input: {"pattern_type": "counter"}

Observation: {
  "pattern": "module counter #(parameter WIDTH=4)...",
  "description": "Parameterized counter with enable and reset"
}

Thought: Good! Now I'll adapt this pattern to the specific task.
  Task requires: 4-bit counter with enable and async reset
  Pattern provides: Parameterized counter structure
  I'll customize it for the requirements.

Final Answer: {
  "code": "module counter_4bit(\n  input clk,\n  input rst_n,\n...",
  "success": true,
  "method": "initial_generation"
}
```

**ReAct Flow for Error-Driven Refinement**:
```
Thought: Checking generation type

Action: check_if_initial_generation
Action Input: {"state_json": "{\"current_code\": \"...\", ...}"}

Observation: {
  "is_initial": false,
  "reason": "Code exists, will refine"
}

Thought: This is refinement. Let me analyze the errors.

Action: refine_code_for_errors
Action Input: {
  "code": "current code...",
  "errors": "Error: signal 'enable' undeclared",
  "error_category": "undeclared"
}

Observation: {
  "strategy": "Add missing signal declarations",
  "focus_areas": ["Declare all signals", "Check signal names", "Add wire/reg"]
}

Thought: Clear! I need to add signal declarations.
  The error shows 'enable' is undeclared.
  I'll add proper declarations for all signals.

Final Answer: {
  "code": "module counter_4bit(\n  input clk,\n  input rst_n,\n  input enable,\n  wire enable_internal;\n...",
  "success": true,
  "method": "error_driven"
}
```

**Tools**:
- `check_if_initial_generation`: Determine context
- `get_design_pattern`: Retrieve example patterns
- `refine_code_for_errors`: Error analysis strategy
- `refine_code_for_port_usage`: Port fix strategy
- `build_generation_prompt`: Prompt construction
- `extract_code_from_response`: Code extraction

**Generation Strategies**:

**Initial Generation**:
1. Get relevant design pattern
2. Analyze task requirements
3. Adapt pattern to requirements
4. Generate complete module
5. Return code with metadata

**Error-Driven Refinement**:
1. Analyze error messages
2. Categorize error type
3. Determine fix strategy
4. Apply targeted fixes
5. Return refined code

**Port Usage Refinement**:
1. Identify unused ports
2. Determine how to use them
3. Modify logic to incorporate ports
4. Return improved code

---

### 3. ValidatorAgent (Specialist)

**Role**: Code structure and quality validation

**Capabilities**:
- Validates Verilog syntax structure
- Checks port usage completeness
- Verifies module completeness
- Assigns quality tier (1-3)

**Execution Flow**:
```
1. Check if code exists → Return tier 0 if not

2. Structure Validation:
   - Parse module declaration
   - Verify module/endmodule pairing
   - Check port list syntax
   - Validate signal declarations
   → Pass: Tier 1 achieved

3. Port Usage Analysis:
   - Extract all ports
   - Check if inputs are read
   - Check if outputs are assigned
   - Identify unused ports
   → All used: Tier 2 achieved

4. Return Results:
   {
     "valid": true/false,
     "issues": ["list of issues"],
     "tier_achieved": 0/1/2,
     "port_analysis": {...}
   }
```

**Quality Tiers**:
- **Tier 0**: No code or invalid structure
- **Tier 1**: Valid structure, compiles
- **Tier 2**: All ports used correctly

---

### 4. TesterAgent (Specialist)

**Role**: Test execution and verification

**Capabilities**:
- Writes code to file system
- Runs Verilator linter
- Executes cocotb test suite
- Reports pass/fail with errors

**Execution Flow**:
```
1. Write Code to File:
   - Save code to /code/rtl/top.sv
   - Create backup if needed

2. Run Linter (Verilator):
   - Execute: verilator --lint-only top.sv
   - Timeout: 30 seconds
   - Capture errors/warnings

3. Run Tests (cocotb):
   - Execute test suite
   - Timeout: 120 seconds
   - Capture test results

4. Analyze Results:
   - All passed → Tier 3
   - Some failed → Tier 1 (compiles)
   - Lint errors → Tier 0

5. Return Results:
   {
     "passed": true/false,
     "errors": "error messages" or None,
     "tier_achieved": 0/1/3,
     "backend": "comprehensive"
   }
```

**Tier Assignment**:
- **Tier 3**: All tests pass
- **Tier 1**: Compiles but tests fail
- **Tier 0**: Doesn't compile

---

### 5. AnalyzerAgent (Specialist)

**Role**: Error categorization and insight generation

**Capabilities**:
- Categorizes errors by type
- Generates fix suggestions
- Prioritizes issues
- Provides actionable feedback

**Execution Flow**:
```
1. Extract Error Messages:
   - Parse linter output
   - Parse test failures
   - Identify error patterns

2. Categorize Errors:
   - syntax: Missing semicolons, parentheses
   - undeclared: Missing signal declarations
   - type: Type mismatches
   - width: Bit width mismatches
   - latch: Inferred latches
   - general: Other issues

3. Generate Suggestions:
   For each category, provide:
   - Strategy description
   - Specific focus areas
   - Priority level

4. Return Results:
   {
     "category": "undeclared",
     "suggestions": ["Add signal declarations", ...],
     "priority": "high"
   }
```

**Error Categories**:
- **syntax**: High priority, blocking
- **undeclared**: High priority, blocking
- **type**: Medium priority
- **width**: Medium priority
- **latch**: Medium priority
- **general**: Low priority

---

## State Management

### VerilogState Structure

The system maintains a comprehensive state dictionary that flows through all agents:

```python
{
    # Task Information
    "task_description": str,        # Original task from user
    "context_files": List[str],     # Available context/examples
    "target_file": str,             # Output file path
    
    # Code Evolution
    "current_code": str,            # Latest generated code
    "code_history": List[str],      # Previous versions
    
    # Quality Tracking
    "tier_achieved": int,           # 0/1/2/3
    "tier_history": List[int],      # Tier progression
    
    # Error Feedback
    "current_errors": str,          # Latest error messages
    "error_category": str,          # Categorized error type
    "error_history": List[str],     # Previous errors
    
    # Validation Results
    "port_analysis": {
        "all_ports_used": bool,
        "unused_inputs": List[str],
        "unused_outputs": List[str],
        "feedback": str
    },
    
    # Testing Results
    "tests_passed": bool,
    "test_errors": str,
    
    # Budget Management
    "agent_invocations": int,       # Current count
    "max_invocations": int,         # Budget limit (50)
    "budget_zone": str,             # green/yellow/red
    
    # Execution Tracking
    "iteration": int,               # Main loop iteration
    "agent_scratchpad": List[str],  # Action history
    "decisions": List[Dict],        # Planner decisions
    
    # Metadata
    "start_time": float,
    "elapsed_time": float,
    "timestamp": str
}
```

### State Updates

State is updated after each agent action:

```python
# After CodeGen
state["current_code"] = result["code"]
state["code_history"].append(result["code"])

# After Validator
state["tier_achieved"] = max(state["tier_achieved"], result["tier_achieved"])
state["port_analysis"] = result.get("port_analysis")

# After Tester
state["tests_passed"] = result["passed"]
state["current_errors"] = result["errors"]
state["tier_achieved"] = max(state["tier_achieved"], result["tier_achieved"])

# After Analyzer
state["error_category"] = result["category"]

# After Every Action
state["agent_invocations"] += 1
state["agent_scratchpad"].append(f"{agent_name}: {action_summary}")
```

---

## Feedback Loop Mechanics

### 1. Error Feedback Loop

```
┌─────────────────────────────────────────────────────┐
│ ITERATION N                                          │
│                                                      │
│ CodeGen generates code                              │
│         ↓                                            │
│ Tester runs tests                                   │
│         ↓                                            │
│ Errors detected: "signal 'enable' undeclared"      │
│         ↓                                            │
│ State updated with errors                           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ ITERATION N+2                                        │
│                                                      │
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
│                                                      │
│ Planner → Decision: "test" → verify fixes           │
│         ↓                                            │
│ Tester runs tests → Success or new errors           │
│         ↓                                            │
│ State updated with results                          │
└─────────────────────────────────────────────────────┘
```

This feedback loop continues until either:
- Tests pass (Tier 3 achieved)
- Budget exhausted
- Max iterations reached

---

**Continue to [REACT_AGENT_IMPLEMENTATION_GUIDE_PART2.md](REACT_AGENT_IMPLEMENTATION_GUIDE_PART2.md) for:**
- Complete workflow details
- Tool system architecture
- Implementation examples
- Configuration & tuning
- Performance metrics
- Troubleshooting guide

---

**End of Part 1**
