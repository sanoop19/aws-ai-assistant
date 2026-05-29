import anthropic

client = anthropic.Anthropic()

conversation_history = []

SYSTEM_PROMPT = """You are an expert AWS solutions architect. 
You help customers design scalable, cost-effective AWS architectures.
Be concise but thorough. Ask clarifying questions when needed."""

print("AWS Architecture Assistant")
print("Type 'quit' to exit, 'tokens' to see usage")
print("="*50)

total_input_tokens = 0
total_output_tokens = 0

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == 'quit':
        print(f"\nSession total - Input: {total_input_tokens} tokens | Output: {total_output_tokens} tokens")
        break

    if user_input.lower() == 'tokens':
        print(f"Running total - Input: {total_input_tokens} | Output: {total_output_tokens}")
        continue

    if not user_input:
        continue

    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # Keep only last 10 messages (5 exchanges)
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    # Call the API with full history every time
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    assistant_message = response.content[0].text

    # Add assistant response to history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    # Track tokens
    total_input_tokens += response.usage.input_tokens
    total_output_tokens += response.usage.output_tokens

    print(f"\nAssistant: {assistant_message}")