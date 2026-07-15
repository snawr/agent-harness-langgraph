import pytest

from agent.llm.client import LLMClient


@pytest.mark.live
def test_ollama_accepts_a_minimal_chat_request():
    """Optional local-environment check; excluded from the default test suite."""
    client = LLMClient()
    if not client.health_check():
        pytest.skip("Ollama is not reachable")

    response = client.invoke(
        [
            {"role": "system", "content": "Reply with one word."},
            {"role": "user", "content": "hello"},
        ]
    )

    assert response.content.strip()
