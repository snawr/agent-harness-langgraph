import sys
import subprocess

def run_smoke_tests():
    try:
        # Example test: Check if the agent starts successfully
        result = subprocess.run(['python', 'agent/main.py', '--version'], capture_output=True, text=True, check=True)
        print("Test 1 Passed:", result.stdout.strip())

        # Example test: Check if the agent handles a basic command
        result = subprocess.run(['python', 'agent/main.py', 'start', '--config=test_config.yaml'], capture_output=True, text=True, check=True)
        print("Test 2 Passed:", result.stdout.strip())

        print("All smoke tests passed.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Test failed with error: {e.stderr.strip()}")
        return 1

if __name__ == "__main__":
