import anthropic

# Initialize the client
# Automatically picks up ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic()

# Make your first API call
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a grumpy sysadmin who finds AWS questions annoying but answers them anyway.",
    messages=[
        {
            "role": "user",
            "content": "In one paragraph, what is the difference between SQS and SNS?"
        }
    ]
)

# Print the response
print(message)