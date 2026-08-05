"""Text-to-speech — neural voice, write WAV to _shared/sample_data/generated/."""
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
