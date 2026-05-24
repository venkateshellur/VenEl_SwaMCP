import os
import json
from pathlib import Path
from typing import List, Dict, Any
from ..config import settings

class ToolManager:
    """
    Manages the dynamic creation, storage, and loading of MCP tools.
    """
    
    def __init__(self):
        self.tools_dir = Path(settings.tools_directory).resolve()
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
    def save_tool(self, name: str, description: str, schema: Dict[str, Any], script_content: str) -> None:
        """
        Saves a new tool's schema and script to disk.
        """
        # Ensure the tool name is safe for file paths
        safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
        
        schema_path = self.tools_dir / f"{safe_name}.json"
        script_path = self.tools_dir / f"{safe_name}.py"
        
        # Save Schema
        tool_definition = {
            "name": safe_name,
            "description": description,
            "schema": schema
        }
        
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(tool_definition, f, indent=2)
            
        # Save Script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
    def load_all_tools(self) -> List[Dict[str, Any]]:
        """
        Scans the dynamic_tools directory and loads all valid tools.
        Returns a list of dictionaries containing name, description, schema, and the script path.
        """
        tools = []
        if not self.tools_dir.exists():
            return tools
            
        for file_path in self.tools_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tool_def = json.load(f)
                    
                safe_name = tool_def.get("name")
                script_path = self.tools_dir / f"{safe_name}.py"
                
                if script_path.exists():
                    tool_def["script_path"] = str(script_path)
                    tools.append(tool_def)
            except Exception as e:
                # Log error in production, but skip bad files for now
                pass
                
        return tools
