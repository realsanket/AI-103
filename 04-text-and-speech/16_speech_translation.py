# Run: uv run python 04-text-and-speech/16_speech_translation.py
"""Speech Translation — recognize spoken audio AND translate in one SDK call.

TranslationRecognizer in the Speech SDK is NOT the same as Azure Translator (the
REST text service). It handles the full pipeline: audio → ASR → translation, in
one streaming call. This lesson uses recognize_once_async() for a single utterance
from the microphone. Compare with 04_translator_rest.py (text-only Translator) and
03_llm_translation.py (LLM text translation).

Code path:
  DefaultAzureCredential → Cognitive Services token → SpeechTranslationConfig with
  auth_token + region → add_target_language("fr") → TranslationRecognizer →
  recognize_once_async().get() → print result.text (source) and result.translations["fr"].

What to watch: two blocks of output — the English source text and the French
translation. If result.reason != TranslatedSpeech, print reason to diagnose (no
input audio, auth failure, or unsupported locale).

Prerequisites / env vars:
  SPEECH_REGION       — region string (e.g., eastus); TranslationConfig requires region
  Microphone access   — grant to terminal/IDE before running
"""
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential

from _shared.speech_config import speech_region

_SCOPE = "https://cognitiveservices.azure.com/.default"


def main() -> None:
    token = DefaultAzureCredential().get_token(_SCOPE).token
    cfg = speechsdk.translation.SpeechTranslationConfig(
        auth_token=token, region=speech_region()
    )
    cfg.speech_recognition_language = "en-US"
    cfg.add_target_language("fr")

    audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.translation.TranslationRecognizer(translation_config=cfg, audio_config=audio)

    print("Listening for one utterance...")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        print("\nOriginal:")
        print(result.text)
        print("\nFrench:")
        print(result.translations["fr"])
    else:
        print(f"failed: {result.reason}")


if __name__ == "__main__":
    main()
