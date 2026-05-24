from abc import ABC, abstractmethod
import os
from pathlib import Path
from ..config import settings
from ..security.analyzer import ScriptAnalyzer

class ExecutionEngine(ABC):
    """
    Abstract base class for all execution engines.
    An execution engine is responsible for safely running dynamically generated Python code.
    """
    
    def __init__(self):
        self.workspace_dir = Path(settings.workspace_directory).resolve()
        # Ensure workspace exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
    def execute(self, script_content: str) -> str:
        """
        Execute the given python script securely by first analyzing it for security violations,
        and then delegating to the concrete implementation.
        """
        # Run AST static analysis first
        ScriptAnalyzer.analyze(script_content)
        
        # Delegate to the specific engine
        return self._execute_impl(script_content)

    @abstractmethod
    def _execute_impl(self, script_content: str) -> str:
        """
        Concrete implementation for running the script.
        """
        pass
