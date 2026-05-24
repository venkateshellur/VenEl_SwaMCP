from src.engines.docker_engine import DockerEngine

try:
    engine = DockerEngine()
    result = engine.execute("print('Hello from Docker sandbox!')")
    print(f"Result: {result.strip()}")
except Exception as e:
    print(f"Error: {e}")
