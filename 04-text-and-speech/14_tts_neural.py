# Run: uv run python 04-text-and-speech/14_tts_neural.py
# Practice-question coverage: Q91.
"""Text-to-speech — neural voice synthesis to a WAV file.

SpeechSynthesizer converts plain text to speech audio using a named neural voice.
Set speech_synthesis_voice_name to select the voice; the voice must be available
in the configured region. This is the plain-text path — for prosody control, pauses,
pitch, and emotional style use SSML with a Neural HD voice (15_tts_ssml_hd.py).

Code path:
  speech_config() → set voice name → AudioOutputConfig(filename) → SpeechSynthesizer
  → speak_text_async(_TEXT).get() → check ResultReason → print OK or delete output
  on failure.

What to watch: "OK — synthesized to .../northwind_support_message.wav". Listen to
the file — JennyNeural sounds professional and natural. If it sounds flat, that's
the plain-text path's ceiling; switch to SSML+HD (lesson 15) for more control.

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint (cognitiveservices.azure.com)
"""
import azure.cognitiveservices.speech as speechsdk

from _shared.config import SAMPLE_DATA
from _shared.speech_config import prepare_audio_output, speech_config

_OUTPUT = SAMPLE_DATA / "generated" / "northwind_support_message.wav"
_TEXT = (
    "Hello, and thank you for contacting Northwind Technology Services. "
    "Your support request has been received. One of our cloud support "
    "specialists will review the issue and contact you shortly."
)


def main() -> None:
    cfg = speech_config()
    cfg.speech_synthesis_voice_name = "en-US-JennyNeural"
    prepare_audio_output(_OUTPUT)
    audio_out = speechsdk.audio.AudioOutputConfig(filename=str(_OUTPUT))
    synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio_out)

    try:
        result = synth.speak_text_async(_TEXT).get()
    except Exception:
        _OUTPUT.unlink(missing_ok=True)
        raise
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"OK — synthesized to {_OUTPUT}")
    else:
        _OUTPUT.unlink(missing_ok=True)
        print(f"failed: {result.reason}")


if __name__ == "__main__":
    main()
