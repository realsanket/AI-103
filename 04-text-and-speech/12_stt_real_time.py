# Run: uv run python 04-text-and-speech/12_stt_real_time.py
"""Real-time streaming STT — continuous recognition from the default microphone.

SpeechRecognizer with AudioConfig(use_default_microphone=True) streams audio to
Azure Speech in real time. The SDK emits events: 'recognizing' (partial results)
and 'recognized' (final results). This lesson wires only 'recognized' events.
Use for live captions, dictation, or meeting transcription. NOT for single-file
batch work (use 11 or 13 for that).

Code path:
  speech_config() → SpeechRecognizer → connect 'recognized' to print final text,
  'session_stopped'/'canceled' to stop. start_continuous_recognition() → spin-wait
  until stop_cb fires.

What to watch: whatever you say prints as recognized phrases. Partial results
('recognizing' events) are not wired — connect that event if you want live typing.
No Ctrl+C cleanup: the process may hang if you interrupt; add try/finally calling
stop_continuous_recognition() for interactive use.

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint
  Microphone permission granted to terminal/IDE
"""
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
