"""SSML + Neural HD voice — pauses, pitch, rate, style tuning.

Neural HD reads semantic content + emotional cues; SSML lets you nudge
specific words for pronunciation, break points, or emphasis.
"""
import azure.cognitiveservices.speech as speechsdk

from _shared.config import SAMPLE_DATA
from _shared.speech_config import speech_config

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
    audio_out = speechsdk.audio.AudioOutputConfig(filename=str(_OUTPUT))
    synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=audio_out)
    result = synth.speak_ssml_async(_SSML).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"OK — synthesized to {_OUTPUT}")
    else:
        print(f"failed: {result.reason} — {result.error_details}")


if __name__ == "__main__":
    main()
