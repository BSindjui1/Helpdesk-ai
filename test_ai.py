import anthropic
import os

#This reads my API key from the environment variable
client =anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# A sample ticket issue to test with
test_issue = "My laptop won't connect to the office WiFi but my phone connects fine."

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[
        {
	    "role": "user",
	    "content": f"""You are an it help desk triage assistant.

Analyze this support ticket and respond in exactly this format:
CATEGORY: [Hardware/Sfotware/Network/Account/Other]
PRIORITY: [Low/Medium/High]
SUGGESTED FIX: [One or two sentences max]

Ticket: {test_issue}"""
	 }
    ]
)

print(message.content[0].text)
	 
