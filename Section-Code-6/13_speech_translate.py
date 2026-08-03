import azure.cognitiveservices.speech as speechsdk

api_key=""
region="eastus2"

translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=api_key,
    region=region
)

translation_config.speech_recognition_language="en-US"
translation_config.add_target_language("fr")

audio_config=speechsdk.audio.AudioConfig(use_default_microphone=True)

translation_recognizer = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config,
    audio_config=audio_config
)

print("Listening...")

result=translation_recognizer.recognize_once_async().get()

if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    print("\nOriginal text:")
    print(result.text)

    print("\nFrench translation:")
    print(result.translations["fr"])