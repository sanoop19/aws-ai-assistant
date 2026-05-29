import anthropic
client = anthropic.Anthropic()

def ask(system, user):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    print("\n" + "="*50)
    print(message.content[0].text)
    print(f"Tokens: {message.usage.input_tokens} in / {message.usage.output_tokens} out")

# Pattern 1: Zero-shot
ask(
    system="You are an AWS expert.",
    user="Classify this error as networking, storage, or compute: 'Unable to connect to RDS instance'"
)

# Pattern 2: Few-shot
ask(
    system="You are an AWS support classifier.",
    user="""
Error: "S3 bucket access denied" → storage
Error: "EC2 instance CPU at 100%" → compute  
Error: "VPC peering connection failed" → networking

Now classify this:
Error: "Lambda function timeout after 15 minutes" →
"""
)

# Pattern 3: Chain of thought
ask(
    system="You are an AWS solutions architect.",
    user="""
A customer has 10TB of data, needs 99.999% durability, 
accessed once a month, wants lowest cost.
Think through this step by step, then recommend the right S3 storage class.
"""
)

# Pattern 4: Structured output
ask(
    system="""You are an AWS cost analyser. 
Always respond in this exact JSON format:
{
  "recommendation": "string",
  "estimated_savings": "string",
  "risk_level": "low|medium|high",
  "action_items": ["item1", "item2"]
}
Return ONLY the JSON. No explanation, no markdown.""",
    user="Customer is running 50 t3.large instances 24/7 but traffic drops 80% on weekends."
)