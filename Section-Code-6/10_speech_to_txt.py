# pip install azure.ai.transcription
from azure.ai.transcription import TranscriptionClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription.models import TranscriptionContent, TranscriptionOptions

endpoint="https://foundry-dev-eus-01.cognitiveservices.azure.com/"
api_key=""

client=TranscriptionClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)

audio_path="conversation.wav"
with open(audio_path, "rb") as audio_file:
    options = TranscriptionOptions(locales=["en-US"])
    result=client.transcribe(TranscriptionContent(definition=options, audio=audio_file))

print(result.combined_phrases[0].text)