"""Custom Speech model — use a deployed custom acoustic/language model endpoint.

After training a Custom Speech model in Speech Studio:
1. Deploy it → get an endpoint ID (GUID).
2. Set CUSTOM_SPEECH_ENDPOINT_ID=<guid> in .env.
3. Pass `endpoint_id` to SpeechConfig so the recognizer routes to your model.

Contrast with `11_stt_fast_file.py` which uses the standard base model.
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
