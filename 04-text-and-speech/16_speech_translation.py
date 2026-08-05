"""Speech Translation (dedicated non-LLM path) — mic → target-language text."""
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
