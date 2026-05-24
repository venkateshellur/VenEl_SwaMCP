# VenEl_SwaMCP: The Self-Tooling Bootstrap Agent

**Project Location:** `/Users/venkateshellur/Venky/Git/VenEl_SwaMCP/`

## Project Overview

**VenEl_SwaMCP** is a standalone, Python-based Model Context Protocol (MCP) server. Its purpose is to act as a "Bootstrap Agent" or "Self-Tooling Agent." 
Unlike traditional MCP servers (like `VenEl.MCPAssistant`) where tools are hardcoded by a developer ahead of time, VenEl_SwaMCP allows an AI agent to dynamically write, execute, and permanently register new tools for itself at runtime.

If the agent encounters a problem it lacks a tool for, it can write the code to solve the problem, and VenEl_SwaMCP will instantly expose that code as a new capability.

## Prerequisites

Before installing, ensure the host machine has the following core dependencies installed:
1. **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
2. **Git**: [Download Git](https://git-scm.com/downloads)
3. **Docker Desktop**: [Download Docker](https://www.docker.com/products/docker-desktop/) (Required for the Tier 1 security sandbox)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/venkateshellur/VenEl_SwaMCP.git
   cd VenEl_SwaMCP
   ```

2. **Set up the Python Virtual Environment:**
   **Mac/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   **Windows:**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Docker Dependency:**
   This server requires Docker Desktop (or equivalent daemon) to be installed on the host machine to securely execute dynamically generated Python tools. The server features an auto-start mechanism and will attempt to wake up Docker automatically if it is closed.

4. **MCP Client Configuration:**
   Add the server to your MCP client (like Claude Desktop) configuration file:
   ```json
   {
     "mcpServers": {
       "VenEl_SwaMCP": {
         "command": "/absolute/path/to/VenEl_SwaMCP/.venv/bin/python",
         "args": ["-m", "src.server"]
       }
     }
   }
   ```

## Planned Architecture

The system is designed to be highly modular, configurable, and platform-independent, mimicking clean architecture principles:

1. **Tiered Execution Engine (Safety First):**
   - **Tier 1 (Docker):** Dynamically generated scripts are executed inside an ephemeral Docker container (`python:3.11-slim`) for maximum safety and sandboxing.
   - **Tier 2 (Local Fallback):** If Docker is unavailable, the system falls back to running the script in an isolated local Python virtual environment (`venv`) with strict resource constraints.
   - *This behavior is configurable via `config.json`.*

2. **Core Components:**
   - **Dispatcher/Server:** The main entry point that registers the core meta-tools with the MCP client.
   - **Tool Manager:** Monitors the `dynamic_tools/` directory, parses incoming script schemas, and hot-reloads them as active MCP tools without requiring a server restart.
   - **Execution Engines:** Abstractions handling the actual running of the dynamically generated code (Docker vs. Local).

3. **Core Meta-Tools:**
   - `execute_script`: Runs a one-off Python script to test logic or gather immediate data.
   - `register_tool`: Accepts a tool name, description, schema, and Python script. Saves it to disk and hot-reloads it as a permanent new tool.

## Current Implementation Status

As of the current session, the foundational scaffolding has been completed:

- [x] **Project Scaffolding:** Directory structure created at `/Users/venkateshellur/Venky/Git/VenEl_SwaMCP/` including `src/engines`, `src/managers`, `src/handlers`, and `dynamic_tools/`.
- [x] **Environment Setup:** Python virtual environment (`.venv`) initialized.
- [x] **Dependencies Installed:** `mcp`, `pydantic`, `docker`, and `anyio` installed and locked in `requirements.txt`.
- [x] **Configuration Layer:** 
  - `config.json` created with base settings (local fallback allowed, docker image defined).
  - `src/config.py` implemented using Pydantic for strong typing and validation.

## Next Steps

We are currently pausing implementation to get into a few more cycles of discussion to fine-tune the design. The immediate next implementation targets will be:

1. Defining the `ExecutionEngine` base class in `src/engines/base.py`.
2. Implementing the Tier 2 local execution fallback in `src/engines/local_engine.py`.
3. Implementing the Tier 1 Docker sandboxing in `src/engines/docker_engine.py`.
4. Building the `ToolManager` to handle hot-reloading of Python files from `dynamic_tools/`. 

---
*Note to future cascades/agents: Please review this document and the `config.json` to understand the current state before resuming implementation.*
