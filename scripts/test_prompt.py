from agent.llm.client import LLMClient

client = LLMClient()
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who are you and what is your purpose?"},
]
resp = client.invoke(messages)
print("RESPONSE:")
print(resp.content)
print("RAW:", resp.raw)
