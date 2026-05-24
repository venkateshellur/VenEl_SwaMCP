import sys
from src.engines.local_engine import LocalEngine
import traceback

engine = LocalEngine()

print("--- Testing Benign Write ---")
try:
    res = engine.execute("with open('test.txt', 'w') as f: f.write('hello')\nprint('Success')")
    print(res)
except Exception as e:
    print(e)

print("--- Testing Malicious Write ---")
try:
    res = engine.execute("with open('/tmp/test_malicious.txt', 'w') as f: f.write('hacked')\nprint('Success')")
    print("WARNING: Malicious write succeeded!")
except Exception as e:
    print(f"Blocked as expected: {e}")

