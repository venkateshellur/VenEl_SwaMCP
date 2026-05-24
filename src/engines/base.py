from abc import ABC, abstractmethod
import os
from pathlib import Path
from ..config import settings

class ExecutionEngine(ABC):
    """
    Abstract base class for all execution engines.
    An execution engine is responsible for safely running dynamically generated Python code.
    """
    
    def __init__(self):
        self.workspace_dir = Path(settings.workspace_directory).resolve()
        # Ensure workspace exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def execute(self, script_content: str) -> str:
        """
        Execute the given python script securely.
        
        Args:
            script_content (str): The raw python script to execute.
            
        Returns:
            str: The standard output from the execution.
            
        Raises:
            Exception: If execution fails or violates security constraints.
        """
        pass
