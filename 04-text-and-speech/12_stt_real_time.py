"""Real-time streaming STT — continuous recognition from the default microphone."""
import time

import azure.cognitiveservices.speech as speechsdk

from _shared.speech_config import speech_config


def main() -> None:
    audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config(), audio_config=audio)

    done = {"stop": False}

    def stop_cb(_evt) -> None:
        recognizer.stop_continuous_recognition()
        done["stop"] = True

    recognizer.recognized.connect(lambda evt: print(evt.result.text))
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    recognizer.start_continuous_recognition()
    print("Listening — press Ctrl+C to stop.")
    while not done["stop"]:
        time.sleep(0.5)


if __name__ == "__main__":
    main()
