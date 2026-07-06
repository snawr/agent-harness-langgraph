from agent.llm.client import LLMClient


def main():
    client = LLMClient()
    ok = client.health_check()
    print(f"LLM health_check: {ok}")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one line."},
    ]

    resp = client.invoke(messages)
    print("--- Response content ---")
    print(resp.content)
    print("--- Raw ---")
    print(getattr(resp, "raw", None))


if __name__ == "__main__":
    main()
