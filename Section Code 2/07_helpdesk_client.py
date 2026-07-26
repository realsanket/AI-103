from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import json

from helpdesk_functions import run_local_function

PROJECT_ENDPOINT = "https://foundry-dev-eus-01.services.ai.azure.com/api/projects/ai-103-project"

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
client = project.get_openai_client()
AGENT_NAME = "IT-HelpDesk-Agent"
AGENT_VERSION = "2"

conversation = client.conversations.create()

response = client.responses.create(
    conversation=conversation.id,
    input="My VPN keeps disconnecting. What should I do?",
    extra_body={
        "agent_reference": {
            "type": "agent_reference",
            "name": AGENT_NAME,
            "version": AGENT_VERSION,
        }
    },
)

tool_outputs = []

for item in response.output:
    if item.type == "function_call":
        function_name = item.name
        arguments = json.loads(item.arguments)

        print(f"Function requested: {function_name}")
        print(f"Arguments received: {arguments}")

        function_result = run_local_function(function_name, arguments)

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": function_result,
            }
        )

if tool_outputs:
    final_response = client.responses.create(
        conversation=conversation.id,
        input=tool_outputs,
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": AGENT_NAME,
                "version": AGENT_VERSION,
            }
        },
    )

    print(final_response.output_text)

else:
    print(response.output_text)