# Dockerfile for ReAct Multi-Agent Verilog Generation System
# Based on open-source verification base image with Verilator, Icarus, etc.

FROM ghcr.io/hdl/sim/osvb

LABEL maintainer="ReAct Agent Team"
LABEL description="ReAct Multi-Agent System for Verilog Code Generation"
LABEL version="2.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        python3-requests \
        build-essential \
        git \
        && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip setuptools wheel

# Install Python dependencies for ReAct Multi-Agent System
RUN pip3 install --no-cache-dir \
    # Core LangChain ecosystem
    langchain>=0.1.0 \
    langgraph>=0.0.20 \
    langchain-community>=0.0.10 \
    # Data validation
    pydantic>=2.0.0 \
    # HTTP clients
    requests>=2.28.0 \
    httpx>=0.24.0 \
    # Verilog processing
    pyverilog>=1.3.0 \
    # Testing framework
    cocotb>=1.7.0 \
    pytest>=7.0.0

# Create necessary directories
RUN mkdir -p /code && chmod 777 /code
RUN mkdir -p /app/slm_agent
RUN mkdir -p /app/slm_agent_react

# Copy the entire agent codebase
# slm_agent/ - Base iterative agent (reused by ReAct)
COPY slm_agent/ /app/slm_agent/

# slm_agent_react/ - ReAct multi-agent system
COPY slm_agent_react/ /app/slm_agent_react/

# Copy main dispatcher
COPY agent.py /app/agent.py

# Make agent.py executable
RUN chmod +x /app/agent.py

# Set Python path to find modules
ENV PYTHONPATH=/app:$PYTHONPATH

# Set environment variables for SLM API
ENV SLM_API_URL=http://host.docker.internal:8000
ENV SLM_MODEL=deepseek
ENV SLM_MAX_LENGTH=8192
ENV SLM_TIMEOUT=300

# ReAct-specific environment variables
ENV AGENT_TYPE=react
ENV MAX_AGENT_INVOCATIONS=50
ENV REACT_MAX_ITERATIONS=5

# Test configuration
ENV TEST_TIMEOUT=120
ENV LINT_TIMEOUT=30

# Output directories
ENV CODE_OUTPUT_DIR=/code/rtl
ENV LOG_LEVEL=INFO

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import langchain, langgraph; print('OK')" || exit 1

# Set the entrypoint to the unified dispatcher
ENTRYPOINT ["python3", "/app/agent.py"]

# Default to ReAct mode (can be overridden with --type argument)
CMD ["--type", "react"]