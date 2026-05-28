import asyncio
import json
import logging
import sys
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import settings
from .managers.tool_manager import ToolManager
from .engines.local_engine import LocalEngine
# from .engines.docker_engine import DockerEngine  # Currently focusing on local for simplicity, but can wrap in try/except

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp-forge")

class SwaMCPServer:
    def __init__(self):
        self.server = Server("VenEl_SwaMCP")
        self.tool_manager = ToolManager()
        
        # Initialize Engine: Try Tier 1 (Docker), fallback to Tier 2 (Local)
        try:
            from .engines.docker_engine import DockerEngine
            self.engine = DockerEngine()
            logger.info("Using Tier 1: Docker Execution Engine")
        except Exception as e:
            if settings.allow_unsafe_local_fallback:
                logger.warning(f"Docker engine unavailable ({e}). Falling back to Tier 2: Local Execution Engine.")
                self.engine = LocalEngine()
            else:
                logger.error(f"Docker engine unavailable ({e}) and allow_unsafe_local_fallback is False.")
                raise Exception("Execution Engine Initialization failed. Cannot safely run tools.")
        
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            tools = [
                Tool(
                    name="execute_script",
                    description="Executes a Python script securely in an isolated sandbox. Use this to test logic or perform one-off computations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script_content": {
                                "type": "string",
                                "description": "The raw python code to execute."
                            }
                        },
                        "required": ["script_content"]
                    }
                ),
                Tool(
                    name="register_tool",
                    description="Registers a new permanent MCP tool. The provided script will be saved and exposed as a new tool. When your tool executes, it will have access to a global dictionary named 'MCP_ARGS' containing the runtime arguments.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the new tool (alphanumeric and underscores only)."
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of what the tool does."
                            },
                            "schema": {
                                "type": "object",
                                "description": "The JSON schema for the tool's arguments, following MCP standard."
                            },
                            "script_content": {
                                "type": "string",
                                "description": "The python code that implements the tool. Must use the global 'MCP_ARGS' dict to read arguments, and print() to return output."
                            }
                        },
                        "required": ["name", "description", "schema", "script_content"]
                    }
                )
            ]
            
            # Load dynamic tools
            dynamic_tools = self.tool_manager.load_all_tools()
            for t in dynamic_tools:
                tools.append(
                    Tool(
                        name=t["name"],
                        description=t["description"],
                        inputSchema=t["schema"]
                    )
                )
                
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
            args = arguments or {}
            
            try:
                if name == "execute_script":
                    script = args.get("script_content", "")
                    output = self.engine.execute(script)
                    return [TextContent(type="text", text=output)]
                    
                elif name == "register_tool":
                    tool_name = args["name"]
                    self.tool_manager.save_tool(
                        name=tool_name,
                        description=args["description"],
                        schema=args["schema"],
                        script_content=args["script_content"]
                    )
                    return [TextContent(type="text", text=f"Tool '{tool_name}' successfully registered and hot-loaded!")]
                    
                else:
                    # Check if it's a dynamic tool
                    dynamic_tools = self.tool_manager.load_all_tools()
                    tool_def = next((t for t in dynamic_tools if t["name"] == name), None)
                    
                    if tool_def:
                        script_path = tool_def["script_path"]
                        with open(script_path, 'r', encoding='utf-8') as f:
                            raw_script = f.read()
                            
                        # Inject arguments into the script
                        args_json = json.dumps(args)
                        injected_script = f"import json\nMCP_ARGS = json.loads('''{args_json}''')\n\n" + raw_script
                        
                        output = self.engine.execute(injected_script)
                        return [TextContent(type="text", text=output)]
                        
                    return [TextContent(type="text", text=f"Tool '{name}' not found.")]
                    
            except Exception as e:
                return [TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            logger.info("VenEl_SwaMCP MCP Server starting on stdio...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    server = SwaMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
