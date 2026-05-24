import ast
import re
from src.config import settings

class SecurityViolationError(Exception):
    """Raised when a script attempts an unauthorized operation."""
    pass

class ScriptAnalyzer:
    """
    Parses dynamically generated Python scripts using AST to detect 
    and block unauthorized database operations (DML/DDL) found within string literals.
    """

    # Regex patterns for detecting SQL operations
    PATTERN_INSERT = re.compile(r'\bINSERT\s+INTO\b', re.IGNORECASE)
    PATTERN_UPDATE = re.compile(r'\bUPDATE\s+\w+\s+SET\b', re.IGNORECASE)
    PATTERN_DELETE = re.compile(r'\bDELETE\s+FROM\b', re.IGNORECASE)
    PATTERN_DDL = re.compile(r'\b(CREATE|DROP|ALTER|TRUNCATE)\s+(TABLE|DATABASE|INDEX|VIEW|PROCEDURE|FUNCTION|TRIGGER)\b', re.IGNORECASE)

    @classmethod
    def analyze(cls, script_content: str):
        """
        Analyzes the given script content. Raises SecurityViolationError if a blocked operation is found.
        """
        try:
            tree = ast.parse(script_content)
        except SyntaxError as e:
            # If it's invalid syntax, it will fail to run anyway, but we can reject it early.
            raise SecurityViolationError(f"SyntaxError during static analysis: {e}")

        # Extract all string literals from the AST
        strings_to_check = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                strings_to_check.append(node.value)
            # Python < 3.8 support (ast.Str was deprecated in 3.8, removed in 3.14, but good to have)
            elif isinstance(node, getattr(ast, 'Str', type(None))):
                strings_to_check.append(node.s)

        # Check each string against our rules and config
        db_security = settings.database_security

        for text in strings_to_check:
            if not db_security.allow_insert and cls.PATTERN_INSERT.search(text):
                raise SecurityViolationError("Database INSERT operations are disabled by configuration.")
            
            if not db_security.allow_update and cls.PATTERN_UPDATE.search(text):
                raise SecurityViolationError("Database UPDATE operations are disabled by configuration.")
            
            if not db_security.allow_delete and cls.PATTERN_DELETE.search(text):
                raise SecurityViolationError("Database DELETE operations are disabled by configuration.")
            
            if not db_security.allow_ddl and cls.PATTERN_DDL.search(text):
                raise SecurityViolationError("Database DDL operations (CREATE/DROP/ALTER/TRUNCATE) are disabled by configuration.")

        return True
