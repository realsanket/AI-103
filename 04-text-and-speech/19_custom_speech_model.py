# Run: uv run python 04-text-and-speech/19_custom_speech_model.py
# Practice-question coverage: Q50, Q61.
"""Custom Speech model — route SDK STT to a trained and deployed custom model.

Custom Speech lets you train an acoustic/language model on your domain vocabulary
(product names, technical jargon, accented speech). After training in Speech Studio,
you deploy it and get an endpoint GUID. This lesson shows the consumption step only:
set speech_config.endpoint_id to the GUID and every other SDK call is identical to
standard STT (see 11_stt_fast_file.py for the base model path).

Note: Batch Transcription (13) can reference a custom model directly in the request
body — it does NOT need a deployed endpoint GUID. Only real-time and fast transcription
need the endpoint GUID.

Code path:
  speech_config() → config.endpoint_id = custom_speech_endpoint_id → SpeechRecognizer
  with audio file → recognize_once_async().get() → print result.text or no-match reason.

What to watch: the transcript routed through your custom model. This lesson does NOT
compare accuracy to the base model — you need a held-out test set with word-error-rate
evaluation to measure improvement.

Prerequisites / env vars:
  SPEECH_ENDPOINT              — Speech resource endpoint
  CUSTOM_SPEECH_ENDPOINT_ID    — GUID from Speech Studio → Custom Speech → Deploy model
"""
import azure.cognitiveservices.speech as speechsdk

from _shared.config import settings, SAMPLE_DATA
from _shared.speech_config import speech_config


def recognize_with_custom_model(audio_path: str) -> str:
    s = settings()
    if not s.custom_speech_endpoint_id:
        raise SystemExit(
            "Set CUSTOM_SPEECH_ENDPOINT_ID to your Custom Speech deployment GUID.\n"
            "Create one at https://speech.microsoft.com > Custom Speech > Deploy model."
        )
    config = speech_config()
    # Routing to the custom model is a single attribute — everything else is identical
    # to standard STT. The base model is overridden when endpoint_id is set.
    config.endpoint_id = s.custom_speech_endpoint_id

    audio = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio)
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.NoMatch:
        return f"[no match: {result.no_match_details}]"
    return f"[cancelled: {result.cancellation_details.reason}]"


def main() -> None:
    audio = str(SAMPLE_DATA / "audio" / "northwind_support_message.wav")
    print("Transcribing with custom model...")
    print(recognize_with_custom_model(audio))


if __name__ == "__main__":
    main()
