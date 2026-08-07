# Run: uv run python 02-generative-ai-and-agents/hosted_agent_responses/main.py

"""Responses endpoint hosted by Foundry Agent Server."""
import asyncio
import os

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set.")
    return value


os.environ.setdefault("PORT", "8088")
_project = AIProjectClient(
    endpoint=_required("FOUNDRY_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)
_responses = _project.get_openai_client().responses
_model = _required("FOUNDRY_MODEL_NAME")

# Adapter owns 0.0.0.0:$PORT, GET /readiness, Responses wire format, and SIGTERM.
app = ResponsesAgentServerHost()


@app.response_handler
async def respond(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
) -> TextResponse:
    user_input = await context.get_input_text() or "Hello!"
    if cancellation_signal.is_set():
        raise asyncio.CancelledError
    response = await asyncio.to_thread(
        _responses.create,
        model=_model,
        instructions="You are a concise Northwind operations assistant.",
        input=user_input,
        store=False,
    )
    return TextResponse(context, request, text=response.output_text)


if __name__ == "__main__":
    app.run()
