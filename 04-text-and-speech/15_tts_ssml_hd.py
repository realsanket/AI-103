# Run: uv run python 04-text-and-speech/15_tts_ssml_hd.py
# Practice-question coverage: Q138.
"""SSML + Neural HD voice — fine-grained prosody and style control.

Neural HD voices (names contain HD: AvaHDNeural, AndrewMultilingualNeural) produce
higher-quality audio and support expressive styles via SSML. Plain text works with
Neural HD, but SSML is how you add pauses, control rate/pitch, and apply emotional
style (friendly, professional, etc.). Builds on 14_tts_neural.py which uses plain
text with a standard neural voice.

Code path:
  speak_ssml_async(_SSML).get() → check ResultReason → print OK or cleanup.
  The SSML document specifies AvaHDNeural, mstts:express-as style=friendly, a 200ms
  break, and a prosody rate of -5%.

What to watch: "OK — synthesized to .../northwind_hd_announcement.wav". Listen —
you should hear the pause after "Northwind" and a slightly slower delivery. If it
sounds flat, the SSML wasn't parsed (bad XML fails silently in some configs).

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint; AvaHDNeural must be available in
  the configured region (check portal before depending on a specific HD voice).
"""
import azure.cognitiveservices.speech as speechsdk

from _shared.config import SAMPLE_DATA
from _shared.speech_config import prepare_audio_output, speech_config

_OUTPUT = SAMPLE_DATA / "generated" / "northwind_hd_announcement.wav"

_SSML = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
  <voice name="en-US-AvaHDNeural">
    <mstts:express-as style="friendly">
      Hello, and thank you for contacting <break time="200ms"/> Northwind.
    </mstts:express-as>
    <break time="400ms"/>
    <prosody rate="-5%">
      Your support request has been received. A specialist will contact you shortly.
    </prosody>
  </voice>
</speak>
"""


def main() -> None:
    cfg = speech_config()
    prepare_audio_output(_OUTPUT)
    audio_out = speechsdk.audio.AudioOutputConfig(filename=str(_OUTPUT))
    synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio_out)
    try:
        result = synth.speak_ssml_async(_SSML).get()
    except Exception:
        _OUTPUT.unlink(missing_ok=True)
        raise
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"OK — synthesized to {_OUTPUT}")
    else:
        _OUTPUT.unlink(missing_ok=True)
        print(f"failed: {result.reason} — {result.error_details}")


if __name__ == "__main__":
    main()
