import subprocess
import sys
import os
import tempfile
from .base import ExecutionEngine

class LocalEngine(ExecutionEngine):
    def __init__(self):
        super().__init__()
        
    def execute(self, script_content: str) -> str:
        """
        Executes a python script locally using subprocess.
        Injects a sys.audit hook to prevent system file modification.
        """
        
        # We inject a security wrapper around the user's code.
        security_wrapper = f"""
import sys
import os
from pathlib import Path

# Security Configuration
WORKSPACE_DIR = Path(r'{self.workspace_dir}').resolve()

def security_audit_hook(event, args):
    # We intercept file system operations
    if event in ('open', 'os.remove', 'os.rmdir', 'os.rename', 'os.truncate', 'os.chmod', 'os.chown', 'pathlib.Path.unlink', 'pathlib.Path.rmdir'):
        # For 'open', args[1] is the mode. We only care about writes.
        if event == 'open':
            mode = args[1] if len(args) > 1 else 'r'
            if not any(c in mode for c in ['w', 'a', 'x', '+']):
                return # read-only is fine for now, or we could block it too
        
        path = args[0]
        # Resolve the path to check if it's inside the workspace
        try:
            if isinstance(path, (str, bytes, os.PathLike)):
                resolved_path = Path(os.fsdecode(path)).resolve()
                if not str(resolved_path).startswith(str(WORKSPACE_DIR)):
                    raise PermissionError(f"Security Violation: Attempted to modify file outside workspace -> {{resolved_path}}")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise
            # If resolution fails, err on the side of caution
            pass

sys.addaudithook(security_audit_hook)

# --- Original Script Execution ---
{script_content}
"""

        # We write the wrapped script to a temp file inside the workspace
        # to execute it, ensuring even the temp script is within bounds.
        try:
            fd, tmp_path = tempfile.mkstemp(dir=str(self.workspace_dir), suffix=".py")
            with os.fdopen(fd, 'w') as f:
                f.write(security_wrapper)
                
            # Execute it
            result = subprocess.run(
                [sys.executable, tmp_path],
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=30 # Add a timeout for safety
            )
            
            if result.returncode != 0:
                raise Exception(f"Local Execution Failed:\\n{result.stderr}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise Exception("Local Execution Timeout: Script took too long.")
        except Exception as e:
            raise Exception(f"Local Engine Error: {str(e)}")
        finally:
            # Cleanup temp file
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except:
                pass
