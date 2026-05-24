import pytest
from src.security.analyzer import ScriptAnalyzer, SecurityViolationError
from src.config import settings

def test_select_is_allowed():
    script = "query = 'SELECT * FROM users'"
    # Should not raise any exception
    assert ScriptAnalyzer.analyze(script) is True

def test_insert_is_blocked_by_default():
    script = "query = 'INSERT INTO users (name) VALUES (\"test\")'"
    settings.database_security.allow_insert = False
    with pytest.raises(SecurityViolationError, match="INSERT"):
        ScriptAnalyzer.analyze(script)

def test_insert_is_allowed_if_configured():
    script = "query = 'INSERT INTO users (name) VALUES (\"test\")'"
    settings.database_security.allow_insert = True
    assert ScriptAnalyzer.analyze(script) is True
    # Reset
    settings.database_security.allow_insert = False

def test_update_is_blocked_by_default():
    script = "query = 'UPDATE users SET name=\"test\"'"
    with pytest.raises(SecurityViolationError, match="UPDATE"):
        ScriptAnalyzer.analyze(script)

def test_delete_is_blocked_by_default():
    script = "query = 'DELETE FROM users WHERE id=1'"
    with pytest.raises(SecurityViolationError, match="DELETE"):
        ScriptAnalyzer.analyze(script)

def test_ddl_is_blocked_by_default():
    scripts = [
        "query = 'DROP TABLE users'",
        "query = 'CREATE DATABASE test'",
        "query = 'ALTER TABLE users ADD COLUMN age INT'",
        "query = 'TRUNCATE TABLE users'"
    ]
    for script in scripts:
        with pytest.raises(SecurityViolationError, match="DDL"):
            ScriptAnalyzer.analyze(script)

def test_f_strings_are_caught():
    script = "table = 'users'\nquery = f'DELETE FROM {table}'"
    with pytest.raises(SecurityViolationError, match="DELETE"):
        ScriptAnalyzer.analyze(script)

def test_multiline_strings_are_caught():
    script = '''
query = """
    DELETE FROM users
    WHERE id=1
"""
'''
    with pytest.raises(SecurityViolationError, match="DELETE"):
        ScriptAnalyzer.analyze(script)

def test_syntax_error_is_caught():
    script = "this is not valid python"
    with pytest.raises(SecurityViolationError, match="SyntaxError"):
        ScriptAnalyzer.analyze(script)
