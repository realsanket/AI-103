from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://foundry-dev-eus-01.services.ai.azure.com/api/projects/ai-103-project"
deployment_name = "gpt-5.4"

project = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai = project.get_openai_client()

source_text = """
Hi team, our VPN keeps dropping every 10 minutes since the last update.
This is affecting our whole sales team and we need this fixed today.
"""

def translate(text: str, target_language: str) -> str:
    system_prompt = f"""
    You are a professional translator. Translate the user's text into
    {target_language}. Preserve the original line breaks and formatting.
    Preserve the tone and register of the original (e.g. formal, urgent,
    casual) rather than producing a flat, literal, word-for-word translation.

    Respond in exactly this plain-text format, with no extra commentary:

    SOURCE LANGUAGE: <detected source language>
    TRANSLATION: <the translated text>
    """

    response = openai.responses.create(
        model=deployment_name,
        input=[
            {"type": "message", "role": "system", "content": system_prompt},
            {"type": "message", "role": "user", "content": text}
        ]
    )
    return response.output_text

for target in ["French", "Japanese"]:
    print(f"--- Translating to {target} ---")
    print(translate(source_text, target))
    print()