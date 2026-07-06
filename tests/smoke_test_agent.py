import os
import sys

def test_agent_initialization():
    """Verify agent can be initialized without errors."""
    try:
        import agent.main
        assert agent.main.__name__ == 'main'
        print("Agent initialization test passed")
    except Exception as e:
        print(f"Agent initialization test failed: {str(e)}")
        sys.exit(1)

def test_required_files():
    """Check presence of essential files."""
    required_files = [
        'agent/main.py',
        'agent/config.yaml',
        'agent/requirements.txt'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"Missing required file: {file}")
            sys.exit(1)
